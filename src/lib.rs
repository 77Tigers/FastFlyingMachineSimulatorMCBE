//! Chunk-oriented storage and version-1 file I/O for Bedrock flying machines.
//! Storage and simulation for Bedrock flying machines.

pub mod debug;
pub mod sim;

use std::collections::BTreeMap;
use std::fmt;
use std::fs;
use std::path::Path;

const MAGIC: &[u8; 4] = b"FFLY";
const VERSION: u16 = 1;

#[derive(Debug)]
pub enum Error {
    Format(String),
    Io(std::io::Error),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Format(message) => write!(f, "{message}"),
            Self::Io(error) => write!(f, "{error}"),
        }
    }
}

impl std::error::Error for Error {}

impl From<std::io::Error> for Error {
    fn from(value: std::io::Error) -> Self {
        Self::Io(value)
    }
}

fn invalid(message: impl Into<String>) -> Error {
    Error::Format(message.into())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct Coord {
    pub x: i64,
    pub y: i64,
    pub z: i64,
}

impl Coord {
    pub const fn new(x: i64, y: i64, z: i64) -> Self {
        Self { x, y, z }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum Kind {
    Slime = 1,
    Honey = 2,
    SmoothStone = 3,
    Glass = 4,
    GlazedTerracotta = 5,
    RedstoneBlock = 6,
    Observer = 7,
    Rod = 8,
    Piston = 9,
    PistonArm = 10,
}

impl TryFrom<u16> for Kind {
    type Error = Error;

    fn try_from(value: u16) -> Result<Self, Self::Error> {
        match value {
            1 => Ok(Self::Slime),
            2 => Ok(Self::Honey),
            3 => Ok(Self::SmoothStone),
            4 => Ok(Self::Glass),
            5 => Ok(Self::GlazedTerracotta),
            6 => Ok(Self::RedstoneBlock),
            7 => Ok(Self::Observer),
            8 => Ok(Self::Rod),
            9 => Ok(Self::Piston),
            10 => Ok(Self::PistonArm),
            _ => Err(invalid(format!("unknown block kind: {value}"))),
        }
    }
}

/// The same 16-bit cell encoding is used in memory and on disk.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Block(u16);

impl Block {
    pub fn plain(kind: Kind, moving: bool) -> Result<Self, Error> {
        if matches!(kind, Kind::Observer | Kind::Rod | Kind::Piston) {
            return Err(invalid("this kind requires a directional constructor"));
        }
        Ok(Self(kind as u16 | ((moving as u16) << 4)))
    }

    pub fn observer(direction: u8, powered: bool, moving: bool) -> Result<Self, Error> {
        Self::direction_check(direction)?;
        Ok(Self(
            Kind::Observer as u16
                | ((moving as u16) << 4)
                | ((direction as u16) << 5)
                | ((powered as u16) << 8),
        ))
    }

    pub fn rod(direction: u8, moving: bool) -> Result<Self, Error> {
        Self::direction_check(direction)?;
        Ok(Self(
            Kind::Rod as u16 | ((moving as u16) << 4) | ((direction as u16) << 5),
        ))
    }

    pub fn piston(
        direction: u8,
        sticky: bool,
        angry: bool,
        state: u8,
        moving: bool,
    ) -> Result<Self, Error> {
        Self::direction_check(direction)?;
        if state > 3 {
            return Err(invalid("piston state must be 0..3"));
        }
        Ok(Self(
            Kind::Piston as u16
                | ((moving as u16) << 4)
                | ((direction as u16) << 5)
                | ((sticky as u16) << 8)
                | ((angry as u16) << 9)
                | ((state as u16) << 10),
        ))
    }

    fn direction_check(direction: u8) -> Result<(), Error> {
        if direction > 5 {
            Err(invalid("direction must be 0..5"))
        } else {
            Ok(())
        }
    }

    pub fn from_cell(cell: u16) -> Result<Self, Error> {
        if cell & 0xf000 != 0 {
            return Err(invalid("nonzero reserved cell bits"));
        }
        let kind = Kind::try_from(cell & 15)?;
        let direction = (cell >> 5) & 7;
        let bit8 = cell & 0x100 != 0;
        let angry = cell & 0x200 != 0;
        let state = (cell >> 10) & 3;
        match kind {
            Kind::Observer => {
                if direction > 5 || angry || state != 0 {
                    return Err(invalid("observer has unsupported state bits"));
                }
            }
            Kind::Rod => {
                if direction > 5 || bit8 || angry || state != 0 {
                    return Err(invalid("rod has unsupported state bits"));
                }
            }
            Kind::Piston => {
                if direction > 5 {
                    return Err(invalid("piston has invalid direction"));
                }
            }
            _ => {
                if direction != 0 || bit8 || angry || state != 0 {
                    return Err(invalid("plain block has unsupported state bits"));
                }
            }
        }
        Ok(Self(cell))
    }

    pub fn cell(self) -> u16 {
        self.0
    }
    pub fn kind(self) -> Kind {
        Kind::try_from(self.0 & 15).expect("validated cell")
    }
    pub fn moving(self) -> bool {
        self.0 & 16 != 0
    }
    pub fn with_moving(self, moving: bool) -> Self {
        Self((self.0 & !16) | ((moving as u16) << 4))
    }
    pub fn direction(self) -> u8 {
        ((self.0 >> 5) & 7) as u8
    }
    pub fn powered(self) -> bool {
        self.kind() == Kind::Observer && self.0 & 0x100 != 0
    }
    pub fn sticky(self) -> bool {
        self.kind() == Kind::Piston && self.0 & 0x100 != 0
    }
    pub fn angry(self) -> bool {
        self.kind() == Kind::Piston && self.0 & 0x200 != 0
    }
    pub fn state(self) -> u8 {
        ((self.0 >> 10) & 3) as u8
    }
}

/// A 16x16x16 dense array, allocated only when the subchunk contains a block.
pub struct Section {
    cells: Box<[u16; 4096]>,
    occupied: usize,
}

impl Section {
    fn new() -> Self {
        Self {
            cells: Box::new([0; 4096]),
            occupied: 0,
        }
    }

    pub fn get(&self, local_index: usize) -> Option<Block> {
        let cell = self.cells[local_index];
        (cell != 0).then_some(Block(cell))
    }

    pub fn occupied_count(&self) -> usize {
        self.occupied
    }

    pub fn cells(&self) -> &[u16; 4096] {
        &self.cells
    }

    fn put(&mut self, local_index: usize, cell: u16) -> Option<Block> {
        let old = std::mem::replace(&mut self.cells[local_index], cell);
        if old == 0 && cell != 0 {
            self.occupied += 1;
        }
        if old != 0 && cell == 0 {
            self.occupied -= 1;
        }
        (old != 0).then_some(Block(old))
    }
}

#[derive(Default)]
pub struct ChunkColumn {
    sections: BTreeMap<i64, Section>,
}

impl ChunkColumn {
    pub fn sections(&self) -> &BTreeMap<i64, Section> {
        &self.sections
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct DiskCoord {
    x: u64,
    y: u64,
    z: u64,
}

impl DiskCoord {
    fn from_reader(reader: &mut Reader<'_>) -> Result<Self, Error> {
        Ok(Self {
            x: reader.varint()?,
            y: reader.varint()?,
            z: reader.varint()?,
        })
    }

    fn write(self, output: &mut Vec<u8>) {
        write_varint(output, self.x);
        write_varint(output, self.y);
        write_varint(output, self.z);
    }

    fn to_coord(self) -> Result<Coord, Error> {
        Ok(Coord::new(
            i64::try_from(self.x).map_err(|_| invalid("X exceeds Rust coordinate range"))?,
            i64::try_from(self.y).map_err(|_| invalid("Y exceeds Rust coordinate range"))?,
            i64::try_from(self.z).map_err(|_| invalid("Z exceeds Rust coordinate range"))?,
        ))
    }
}

/// In-memory layout: 16x16 X/Z chunk columns containing 16-cube subchunks.
pub struct Flyer {
    pub phase_x: u8,
    pub phase_z: u8,
    pub rng_state: u64,
    pub push_limit: u64,
    columns: BTreeMap<(i64, i64), ChunkColumn>,
    piston_blocks: BTreeMap<Coord, Vec<Coord>>,
    occupied: usize,
}

impl Flyer {
    pub fn new(phase_x: u8, phase_z: u8, rng_state: u64, push_limit: u64) -> Result<Self, Error> {
        if phase_x > 15 || phase_z > 15 {
            return Err(invalid("X/Z phases must be 0..15"));
        }
        Ok(Self {
            phase_x,
            phase_z,
            rng_state,
            push_limit,
            columns: BTreeMap::new(),
            piston_blocks: BTreeMap::new(),
            occupied: 0,
        })
    }

    pub fn with_defaults() -> Self {
        Self::new(0, 0, 0, 12).expect("valid defaults")
    }

    /// Advance the single stored SplitMix64 state and return its next output.
    pub fn next_random_u64(&mut self) -> u64 {
        self.rng_state = self.rng_state.wrapping_add(0x9e3779b97f4a7c15);
        let mut value = self.rng_state;
        value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
        value ^ (value >> 31)
    }

    pub fn columns(&self) -> &BTreeMap<(i64, i64), ChunkColumn> {
        &self.columns
    }

    pub fn occupied_count(&self) -> usize {
        self.occupied
    }

    fn address(pos: Coord) -> ((i64, i64), i64, usize) {
        let column = (pos.x.div_euclid(16), pos.z.div_euclid(16));
        let section_y = pos.y.div_euclid(16);
        let index = ((pos.y.rem_euclid(16) as usize) << 8)
            | ((pos.z.rem_euclid(16) as usize) << 4)
            | (pos.x.rem_euclid(16) as usize);
        (column, section_y, index)
    }

    pub fn get(&self, pos: Coord) -> Option<Block> {
        let (column, section_y, index) = Self::address(pos);
        self.columns
            .get(&column)?
            .sections
            .get(&section_y)?
            .get(index)
    }

    pub fn set(&mut self, pos: Coord, block: Block) -> Option<Block> {
        let (column, section_y, index) = Self::address(pos);
        let section = self
            .columns
            .entry(column)
            .or_default()
            .sections
            .entry(section_y)
            .or_insert_with(Section::new);
        let old = section.put(index, block.cell());
        if old.is_none() {
            self.occupied += 1;
        }
        if block.kind() != Kind::Piston {
            self.piston_blocks.remove(&pos);
        }
        old
    }

    pub fn remove(&mut self, pos: Coord) -> Option<Block> {
        self.piston_blocks.remove(&pos);
        let (column, section_y, index) = Self::address(pos);
        let chunk = self.columns.get_mut(&column)?;
        let section = chunk.sections.get_mut(&section_y)?;
        let old = section.put(index, 0);
        let empty_section = section.occupied == 0;
        if empty_section {
            chunk.sections.remove(&section_y);
        }
        let empty_column = chunk.sections.is_empty();
        if empty_column {
            self.columns.remove(&column);
        }
        if old.is_some() {
            self.occupied -= 1;
        }
        old
    }

    pub fn set_piston_blocks(&mut self, owner: Coord, mut blocks: Vec<Coord>) -> Result<(), Error> {
        if self.get(owner).map(Block::kind) != Some(Kind::Piston) {
            return Err(invalid("owner coordinate must contain a piston"));
        }
        if (blocks.len() as u64) > self.push_limit {
            return Err(invalid("piston list exceeds push limit"));
        }
        blocks.sort();
        if blocks.windows(2).any(|pair| pair[0] == pair[1]) {
            return Err(invalid("piston list contains duplicate coordinates"));
        }
        if blocks.is_empty() {
            self.piston_blocks.remove(&owner);
        } else {
            self.piston_blocks.insert(owner, blocks);
        }
        Ok(())
    }

    pub fn piston_blocks(&self, owner: Coord) -> &[Coord] {
        self.piston_blocks
            .get(&owner)
            .map(Vec::as_slice)
            .unwrap_or(&[])
    }

    pub fn blocks(&self) -> Vec<(Coord, Block)> {
        let mut result = Vec::with_capacity(self.occupied);
        for (&(cx, cz), chunk) in &self.columns {
            for (&sy, section) in &chunk.sections {
                for (index, &cell) in section.cells.iter().enumerate() {
                    if cell == 0 {
                        continue;
                    }
                    result.push((
                        Coord::new(
                            cx * 16 + (index & 15) as i64,
                            sy * 16 + (index >> 8) as i64,
                            cz * 16 + ((index >> 4) & 15) as i64,
                        ),
                        Block(cell),
                    ));
                }
            }
        }
        result
    }

    pub fn to_bytes(&self) -> Result<Vec<u8>, Error> {
        let blocks = self.blocks();
        let mut minimum: Option<Coord> = None;
        let mut include = |pos: Coord| {
            minimum = Some(match minimum {
                None => pos,
                Some(old) => Coord::new(old.x.min(pos.x), old.y.min(pos.y), old.z.min(pos.z)),
            });
        };
        for &(pos, _) in &blocks {
            include(pos);
        }
        for (&owner, members) in &self.piston_blocks {
            include(owner);
            for &member in members {
                include(member);
            }
        }
        let minimum = minimum.unwrap_or(Coord::new(0, 0, 0));
        let shift_x = -((minimum.x as i128).div_euclid(16) * 16);
        let shift_y = -(minimum.y as i128);
        let shift_z = -((minimum.z as i128).div_euclid(16) * 16);
        let normalize = |pos: Coord| -> Result<DiskCoord, Error> {
            let converted = |value: i64, shift: i128| -> Result<u64, Error> {
                let shifted = value as i128 + shift;
                let result = i64::try_from(shifted)
                    .map_err(|_| invalid("normalized coordinate exceeds Rust coordinate range"))?;
                u64::try_from(result).map_err(|_| invalid("negative normalized coordinate"))
            };
            Ok(DiskCoord {
                x: converted(pos.x, shift_x)?,
                y: converted(pos.y, shift_y)?,
                z: converted(pos.z, shift_z)?,
            })
        };
        let mut sections: BTreeMap<(u64, u64, u64), Vec<(u16, u16)>> = BTreeMap::new();
        for (pos, block) in blocks {
            let pos = normalize(pos)?;
            let key = (pos.x / 16, pos.z / 16, pos.y / 16);
            let index = (((pos.y & 15) << 8) | ((pos.z & 15) << 4) | (pos.x & 15)) as u16;
            sections.entry(key).or_default().push((index, block.cell()));
        }
        let mut output = Vec::new();
        output.extend_from_slice(MAGIC);
        output.extend_from_slice(&VERSION.to_le_bytes());
        output.extend_from_slice(&[self.phase_x, self.phase_z]);
        output.extend_from_slice(&self.rng_state.to_le_bytes());
        write_varint(&mut output, self.push_limit);
        write_varint(&mut output, sections.len() as u64);
        for ((cx, cz, sy), mut records) in sections {
            write_varint(&mut output, cx);
            write_varint(&mut output, cz);
            write_varint(&mut output, sy);
            records.sort_unstable_by_key(|record| record.0);
            write_varint(&mut output, records.len() as u64);
            for (index, cell) in records {
                output.extend_from_slice(&index.to_le_bytes());
                output.extend_from_slice(&cell.to_le_bytes());
            }
        }
        write_varint(&mut output, self.piston_blocks.len() as u64);
        let mut lists = Vec::with_capacity(self.piston_blocks.len());
        for (&owner, members) in &self.piston_blocks {
            if self.get(owner).map(Block::kind) != Some(Kind::Piston) {
                return Err(invalid("piston list owner has no piston"));
            }
            if members.is_empty() || (members.len() as u64) > self.push_limit {
                return Err(invalid("invalid piston list length"));
            }
            let owner = normalize(owner)?;
            let mut members: Vec<DiskCoord> = members
                .iter()
                .map(|&p| normalize(p))
                .collect::<Result<_, _>>()?;
            members.sort();
            if members.windows(2).any(|pair| pair[0] == pair[1]) {
                return Err(invalid("duplicate piston list member"));
            }
            lists.push((owner, members));
        }
        lists.sort_by_key(|entry| entry.0);
        for (owner, members) in lists {
            owner.write(&mut output);
            write_varint(&mut output, members.len() as u64);
            for member in members {
                member.write(&mut output);
            }
        }
        Ok(output)
    }

    pub fn from_bytes(raw: &[u8]) -> Result<Self, Error> {
        let mut reader = Reader::new(raw);
        if reader.take(4)? != MAGIC {
            return Err(invalid("invalid magic"));
        }
        let version = reader.u16()?;
        if version != VERSION {
            return Err(invalid(format!("unsupported version {version}")));
        }
        let phase_x = reader.byte()?;
        let phase_z = reader.byte()?;
        let rng_state = reader.u64()?;
        let push_limit = reader.varint()?;
        let mut flyer = Self::new(phase_x, phase_z, rng_state, push_limit)?;
        let section_count = reader.varint()?;
        let mut previous_key = None;
        for _ in 0..section_count {
            let cx = reader.varint()?;
            let cz = reader.varint()?;
            let sy = reader.varint()?;
            let key = (cx, cz, sy);
            if previous_key.is_some_and(|old| key <= old) {
                return Err(invalid("subchunks are not strictly sorted"));
            }
            previous_key = Some(key);
            let count = reader.varint()?;
            if !(1..=4096).contains(&count) {
                return Err(invalid("invalid occupied count"));
            }
            let mut previous_index = None;
            for _ in 0..count {
                let index = reader.u16()?;
                let cell = reader.u16()?;
                if index >= 4096 || previous_index.is_some_and(|old| index <= old) {
                    return Err(invalid("invalid or unsorted local index"));
                }
                previous_index = Some(index);
                let coordinate = DiskCoord {
                    x: cx
                        .checked_mul(16)
                        .and_then(|v| v.checked_add((index & 15) as u64))
                        .ok_or_else(|| invalid("X coordinate overflow"))?,
                    y: sy
                        .checked_mul(16)
                        .and_then(|v| v.checked_add((index >> 8) as u64))
                        .ok_or_else(|| invalid("Y coordinate overflow"))?,
                    z: cz
                        .checked_mul(16)
                        .and_then(|v| v.checked_add(((index >> 4) & 15) as u64))
                        .ok_or_else(|| invalid("Z coordinate overflow"))?,
                }
                .to_coord()?;
                flyer.set(coordinate, Block::from_cell(cell)?);
            }
        }
        let list_count = reader.varint()?;
        let mut previous_owner = None;
        for _ in 0..list_count {
            let disk_owner = DiskCoord::from_reader(&mut reader)?;
            if previous_owner.is_some_and(|old| disk_owner <= old) {
                return Err(invalid("piston lists are not strictly sorted"));
            }
            previous_owner = Some(disk_owner);
            let owner = disk_owner.to_coord()?;
            let count = reader.varint()?;
            if count == 0 || count > push_limit {
                return Err(invalid("invalid piston list length"));
            }
            let count = usize::try_from(count).map_err(|_| invalid("piston list too large"))?;
            if count > (raw.len() - reader.offset) / 3 {
                return Err(invalid("truncated piston list"));
            }
            let mut members = Vec::with_capacity(count);
            let mut previous_member = None;
            for _ in 0..count {
                let disk_member = DiskCoord::from_reader(&mut reader)?;
                if previous_member.is_some_and(|old| disk_member <= old) {
                    return Err(invalid("piston members are not strictly sorted"));
                }
                previous_member = Some(disk_member);
                members.push(disk_member.to_coord()?);
            }
            flyer.set_piston_blocks(owner, members)?;
        }
        if reader.offset != raw.len() {
            return Err(invalid("trailing bytes"));
        }
        Ok(flyer)
    }

    pub fn save(&self, path: impl AsRef<Path>) -> Result<(), Error> {
        fs::write(path, self.to_bytes()?)?;
        Ok(())
    }

    pub fn load(path: impl AsRef<Path>) -> Result<Self, Error> {
        Self::from_bytes(&fs::read(path)?)
    }
}

fn write_varint(output: &mut Vec<u8>, mut value: u64) {
    while value >= 128 {
        output.push((value as u8 & 127) | 128);
        value >>= 7;
    }
    output.push(value as u8);
}

struct Reader<'a> {
    raw: &'a [u8],
    offset: usize,
}

impl<'a> Reader<'a> {
    fn new(raw: &'a [u8]) -> Self {
        Self { raw, offset: 0 }
    }

    fn take(&mut self, length: usize) -> Result<&'a [u8], Error> {
        let end = self
            .offset
            .checked_add(length)
            .ok_or_else(|| invalid("file offset overflow"))?;
        if end > self.raw.len() {
            return Err(invalid("truncated file"));
        }
        let result = &self.raw[self.offset..end];
        self.offset = end;
        Ok(result)
    }

    fn byte(&mut self) -> Result<u8, Error> {
        Ok(self.take(1)?[0])
    }
    fn u16(&mut self) -> Result<u16, Error> {
        Ok(u16::from_le_bytes(self.take(2)?.try_into().unwrap()))
    }
    fn u64(&mut self) -> Result<u64, Error> {
        Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }

    fn varint(&mut self) -> Result<u64, Error> {
        let mut value = 0u64;
        for index in 0..10 {
            let byte = self.byte()?;
            if index == 9 && byte > 1 {
                return Err(invalid("variable integer exceeds u64"));
            }
            value |= ((byte & 127) as u64) << (7 * index);
            if byte & 128 == 0 {
                if index > 0 && byte == 0 {
                    return Err(invalid("overlong variable integer"));
                }
                return Ok(value);
            }
        }
        Err(invalid("overlong variable integer"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn negative_coords_and_shared_references_round_trip() {
        let mut flyer = Flyer::new(7, 11, 42, 12).unwrap();
        let p1 = Coord::new(-17, -3, 0);
        let p2 = Coord::new(18, -3, 0);
        let shared = Coord::new(-16, -2, 0);
        flyer.set(p1, Block::piston(0, true, true, 3, true).unwrap());
        flyer.set(p2, Block::piston(5, false, false, 0, false).unwrap());
        flyer.set(shared, Block::plain(Kind::PistonArm, true).unwrap());
        flyer.set_piston_blocks(p1, vec![shared]).unwrap();
        flyer.set_piston_blocks(p2, vec![shared]).unwrap();
        let encoded = flyer.to_bytes().unwrap();
        let loaded = Flyer::from_bytes(&encoded).unwrap();
        assert_eq!(encoded, loaded.to_bytes().unwrap());
        assert_eq!(loaded.occupied_count(), 3);
        assert_eq!(loaded.phase_x, 7);
        assert_eq!(loaded.phase_z, 11);
        assert_eq!(loaded.rng_state, 42);
        assert_eq!(loaded.piston_blocks(Coord::new(15, 0, 0)).len(), 1);
    }

    #[test]
    fn moving_bit_is_available_on_every_kind() {
        for kind in [
            Kind::Slime,
            Kind::Honey,
            Kind::SmoothStone,
            Kind::Glass,
            Kind::GlazedTerracotta,
            Kind::RedstoneBlock,
            Kind::PistonArm,
        ] {
            let block = Block::plain(kind, true).unwrap();
            assert_eq!(Block::from_cell(block.cell()).unwrap(), block);
        }
        assert!(Block::observer(0, false, true).unwrap().moving());
        assert!(Block::rod(0, true).unwrap().moving());
        assert!(Block::piston(0, false, false, 0, true).unwrap().moving());
    }

    #[test]
    fn splitmix_state_is_resumable() {
        let mut flyer = Flyer::with_defaults();
        assert_eq!(flyer.next_random_u64(), 0xe220a8397b1dcdaf);
        let resumed = Flyer::from_bytes(&flyer.to_bytes().unwrap()).unwrap();
        let mut original = flyer;
        let mut resumed = resumed;
        assert_eq!(original.next_random_u64(), resumed.next_random_u64());
    }
}
