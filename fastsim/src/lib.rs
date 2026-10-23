//! Fast simulator with behaviour identical to `fastflyer`'s reference
//! `Flyer::tick()` (src/sim.rs). The reference stays the definition; this
//! crate only replaces the data structures:
//!
//! * a dense grid window instead of the chunk-column/section BTreeMaps. No
//!   block ever sits on the window's outer layer, so the six neighbours of a
//!   block are plain index offsets. Index order equals `Coord` order;
//! * per-world-chunk occupancy counts and sorted piston lists that are kept
//!   up to date incrementally instead of rescanning every section each tick;
//! * per-cell flag bits (power cache, hard power, discovery marks) instead of
//!   hash sets;
//! * a list of observers pulsed since the last power stage.
//!
//! Every mutation happens in the same order as in the reference, so partial
//! state after an error is identical too. Flyers whose blocks come near the
//! i64 limits, or that are too sparse for a dense window, run on the
//! reference simulator instead.

use std::collections::HashMap;
use std::hash::{BuildHasherDefault, Hasher};

use fastflyer::{Block, Coord, Error, Flyer, Kind, TickReport};

const SLIME: u16 = 1;
const HONEY: u16 = 2;
const SMOOTH_STONE: u16 = 3;
const GLAZED: u16 = 5;
const REDSTONE: u16 = 6;
const OBSERVER: u16 = 7;
const ROD: u16 = 8;
const PISTON: u16 = 9;
const ARM: u16 = 10;

const MOVING: u16 = 1 << 4;
const BIT8: u16 = 1 << 8; // observer powered / piston sticky
const ANGRY: u16 = 1 << 9;
const STATE: u16 = 3 << 10;
// Simulator-only flag bits; the file format keeps bits 12..15 zero.
const F_POWERED: u16 = 1 << 12; // piston power cache for this tick
const F_HARD: u16 = 1 << 13; // hard-powered solid, power stage only
const F_MARK: u16 = 1 << 14; // queued during discovery
const FLAGS: u16 = 0xf000;

const DIRECTIONS: [(i64, i64, i64); 6] = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
];

/// Blocks outside this range use the reference simulator, so that no
/// coordinate arithmetic here can overflow.
const SAFE: i64 = 1 << 60;
/// Largest dense window, in cells, before falling back to the reference.
const MAX_CELLS: i64 = 1 << 22;
const MARGIN: i64 = 8;
/// Room left ahead of a flyer that reached the window edge.
const FORWARD: i64 = 128;

#[inline]
fn kind(cell: u16) -> u16 {
    cell & 15
}
#[inline]
fn moving(cell: u16) -> bool {
    cell & MOVING != 0
}
#[inline]
fn direction(cell: u16) -> usize {
    ((cell >> 5) & 7) as usize
}
#[inline]
fn state(cell: u16) -> u16 {
    (cell >> 10) & 3
}
#[inline]
fn step(pos: Coord, d: usize) -> Coord {
    let (dx, dy, dz) = DIRECTIONS[d];
    Coord::new(pos.x + dx, pos.y + dy, pos.z + dz)
}
#[inline]
fn opposite(d: usize) -> usize {
    d ^ 1
}

#[derive(Default)]
struct FxHasher(u64);
impl Hasher for FxHasher {
    fn finish(&self) -> u64 {
        self.0
    }
    fn write(&mut self, bytes: &[u8]) {
        for &b in bytes {
            self.write_u64(b as u64);
        }
    }
    fn write_i64(&mut self, i: i64) {
        self.write_u64(i as u64);
    }
    fn write_u64(&mut self, i: u64) {
        self.0 = (self.0.rotate_left(5) ^ i).wrapping_mul(0x51_7c_c1_b7_27_22_0a_95);
    }
}
type FxMap<K, V> = HashMap<K, V, BuildHasherDefault<FxHasher>>;

struct ShuffleRng(u64);
impl ShuffleRng {
    #[inline]
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut value = self.0;
        value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
        value ^ (value >> 31)
    }
}

fn shuffle<T>(items: &mut [T], seed: u64) {
    let mut rng = ShuffleRng(seed);
    for end in (1..items.len()).rev() {
        let index = (rng.next() % (end as u64 + 1)) as usize;
        items.swap(end, index);
    }
}

/// Dense window starting at `o`: X spans `sx` cells, Y and Z span powers of
/// two. Index = (x << (by + bz)) | (y << bz) | z, relative to the origin.
struct Grid {
    ox: i64,
    oy: i64,
    oz: i64,
    sx: i64,
    by: u32,
    bz: u32,
    cells: Vec<u16>,
    delta: [usize; 6],
}

impl Grid {
    fn new(lo: Coord, hi: Coord) -> Self {
        let sx = hi.x - lo.x + 1;
        let by = ((hi.y - lo.y + 1) as u64).next_power_of_two().trailing_zeros();
        let bz = ((hi.z - lo.z + 1) as u64).next_power_of_two().trailing_zeros();
        let sxs = 1usize << (by + bz);
        let sys = 1usize << bz;
        Self {
            ox: lo.x,
            oy: lo.y,
            oz: lo.z,
            sx,
            by,
            bz,
            cells: vec![0; (sx as usize) << (by + bz)],
            delta: [
                sxs,
                sxs.wrapping_neg(),
                sys,
                sys.wrapping_neg(),
                1,
                1usize.wrapping_neg(),
            ],
        }
    }

    /// Copy of the geometry without the cells.
    fn shape(&self) -> Grid {
        Grid {
            ox: self.ox,
            oy: self.oy,
            oz: self.oz,
            sx: self.sx,
            by: self.by,
            bz: self.bz,
            cells: Vec::new(),
            delta: self.delta,
        }
    }

    #[inline]
    fn sy(&self) -> i64 {
        1 << self.by
    }
    #[inline]
    fn sz(&self) -> i64 {
        1 << self.bz
    }

    #[inline]
    fn index(&self, pos: Coord) -> Option<usize> {
        let x = pos.x.wrapping_sub(self.ox);
        let y = pos.y.wrapping_sub(self.oy);
        let z = pos.z.wrapping_sub(self.oz);
        if (x as u64) < self.sx as u64 && (y as u64) < self.sy() as u64 && (z as u64) < self.sz() as u64
        {
            Some(((x as usize) << (self.by + self.bz)) | ((y as usize) << self.bz) | z as usize)
        } else {
            None
        }
    }

    #[inline]
    fn coord(&self, index: usize) -> Coord {
        Coord::new(
            self.ox + (index >> (self.by + self.bz)) as i64,
            self.oy + ((index >> self.bz) & ((1 << self.by) - 1)) as i64,
            self.oz + (index & ((1 << self.bz) - 1)) as i64,
        )
    }

    #[inline]
    fn x_of(&self, index: usize) -> i64 {
        self.ox + (index >> (self.by + self.bz)) as i64
    }
    #[inline]
    fn z_of(&self, index: usize) -> i64 {
        self.oz + (index & ((1 << self.bz) - 1)) as i64
    }

    /// Outer-layer sides a cell touches, where blocks may not stay: bit 0
    /// for -x, 1 for +x, 2 for -y, 3 for +y, 4 for -z, 5 for +z.
    #[inline]
    fn border_sides(&self, index: usize) -> u8 {
        let x = (index >> (self.by + self.bz)) as i64;
        let y = ((index >> self.bz) & ((1 << self.by) - 1)) as i64;
        let z = (index & ((1 << self.bz) - 1)) as i64;
        (x == 0) as u8
            | ((x == self.sx - 1) as u8) << 1
            | ((y == 0) as u8) << 2
            | ((y == self.sy() - 1) as u8) << 3
            | ((z == 0) as u8) << 4
            | ((z == self.sz() - 1) as u8) << 5
    }

    /// Whether a cell lies on the outer layer on the side that direction
    /// `dir` (DIRECTIONS order) points to.
    #[inline]
    fn at_side(&self, index: usize, dir: usize) -> bool {
        match dir {
            0 => (index >> (self.by + self.bz)) as i64 == self.sx - 1,
            1 => index >> (self.by + self.bz) == 0,
            2 => (index >> self.bz) & ((1 << self.by) - 1) == (1 << self.by) - 1,
            3 => (index >> self.bz) & ((1 << self.by) - 1) == 0,
            4 => index & ((1 << self.bz) - 1) == (1 << self.bz) - 1,
            _ => index & ((1 << self.bz) - 1) == 0,
        }
    }

    #[inline]
    fn slab(&self) -> usize {
        1 << (self.by + self.bz)
    }

    #[inline]
    fn get(&self, pos: Coord) -> u16 {
        match self.index(pos) {
            Some(i) => self.cells[i],
            None => 0,
        }
    }

    fn occupied(&self) -> impl Iterator<Item = (Coord, u16)> + '_ {
        self.cells
            .iter()
            .enumerate()
            .filter(|(_, &c)| c != 0)
            .map(|(i, &c)| (self.coord(i), c))
    }

    /// Bounding box of occupied cells.
    fn bounds(&self) -> Option<(Coord, Coord)> {
        let mut result: Option<(Coord, Coord)> = None;
        for (pos, _) in self.occupied() {
            result = Some(match result {
                None => (pos, pos),
                Some((lo, hi)) => (
                    Coord::new(lo.x.min(pos.x), lo.y.min(pos.y), lo.z.min(pos.z)),
                    Coord::new(hi.x.max(pos.x), hi.y.max(pos.y), hi.z.max(pos.z)),
                ),
            });
        }
        result
    }
}


struct Fast {
    phase_x: i64,
    phase_z: i64,
    rng_state: u64,
    push_limit: u64,
    grid: Grid,
    lists: FxMap<Coord, Vec<Coord>>,
    /// Block count per world chunk (entries may reach zero).
    chunk_counts: Vec<((i64, i64), u32)>,
    /// Every piston, as sorted `piston_key`s, i.e. ordered by (world chunk,
    /// position); exact at the start of each tick. Re-keyed on relocation.
    pistons: Vec<u128>,
    /// Ranges of `pistons` per world chunk, for the current tick.
    piston_ranges: Vec<((i64, i64), usize, usize)>,
    /// Every rod position, unordered; exact at the start of each tick.
    rods: Vec<Coord>,
    /// Positions where pistons and rods were placed during this tick. Every
    /// piston or rod present mid-tick is in `pistons`/`rods` or here.
    added_pistons: Vec<Coord>,
    added_rods: Vec<Coord>,
    /// Observers that may be powered; reset by the next power stage.
    pulsed: Vec<Coord>,
    // Scratch buffers.
    hard: Vec<usize>,
    queue: Vec<usize>,
    entries: Vec<(usize, u16, bool)>,
    key_scratch: Vec<u128>,
    merge_scratch: Vec<u128>,
    candidates: Vec<Coord>,
    /// Number of blocks of each kind.
    kinds: [usize; 16],
    /// Cleared list allocations for reuse.
    pool: Vec<Vec<Coord>>,
    /// Trace-equivalent movement diagnostics, collected when present.
    diag: Option<Diagnostics>,
}

/// A flyer being simulated. Converts from and to `fastflyer::Flyer`.
pub struct FastFlyer {
    inner: Inner,
}

enum Inner {
    Fast(Box<Fast>),
    Reference(Box<Flyer>),
}

impl FastFlyer {
    pub fn from_flyer(flyer: &Flyer) -> Self {
        match Fast::from_flyer(flyer) {
            Some(fast) => Self {
                inner: Inner::Fast(Box::new(fast)),
            },
            None => Self {
                inner: Inner::Reference(Box::new(clone_flyer(flyer))),
            },
        }
    }

    pub fn load(path: impl AsRef<std::path::Path>) -> Result<Self, Error> {
        Ok(Self::from_flyer(&Flyer::load(path)?))
    }

    pub fn to_flyer(&self) -> Flyer {
        match &self.inner {
            Inner::Fast(fast) => fast.to_flyer(),
            Inner::Reference(flyer) => clone_flyer(flyer),
        }
    }

    /// Window geometry (x, y, z sizes), for diagnostics.
    pub fn window_size(&self) -> Option<(i64, i64, i64)> {
        match &self.inner {
            Inner::Fast(fast) => Some((fast.grid.sx, fast.grid.sy(), fast.grid.sz())),
            Inner::Reference(_) => None,
        }
    }

    /// Like `tick`, also adding what the reference's `tick_traced` would
    /// report in its steps' movement overlays: every failure `(position,
    /// reason)` in order, and the largest successful source set.
    pub fn tick_diagnosed(&mut self, diag: &mut Diagnostics) -> Result<TickReport, Error> {
        if let Inner::Fast(fast) = &self.inner {
            if !fast.safe() {
                let flyer = fast.to_flyer();
                self.inner = Inner::Reference(Box::new(flyer));
            }
        }
        match &mut self.inner {
            Inner::Fast(fast) => {
                fast.diag = Some(std::mem::take(diag));
                let result = fast.tick();
                *diag = fast.diag.take().unwrap();
                result
            }
            Inner::Reference(flyer) => {
                let mut trace = fastflyer::debug::TickTrace::new(flyer);
                let result = flyer.tick_traced(&mut trace, 0);
                for step in trace.steps {
                    if let Some(m) = step.info.movement {
                        match m.failure {
                            Some(failure) => diag.failures.push(failure),
                            None => {
                                diag.max_successful_action =
                                    diag.max_successful_action.max(m.sources.len())
                            }
                        }
                    }
                }
                result
            }
        }
    }

    /// Number of blocks of each kind, indexed by kind number (arms included).
    pub fn kind_counts(&self) -> [usize; 16] {
        match &self.inner {
            Inner::Fast(fast) => fast.kinds,
            Inner::Reference(flyer) => {
                let mut counts = [0; 16];
                for (_, block) in flyer.blocks() {
                    counts[block.kind() as usize] += 1;
                }
                counts
            }
        }
    }

    pub fn occupied_count(&self) -> usize {
        self.kind_counts().iter().sum()
    }

    pub fn push_limit(&self) -> u64 {
        match &self.inner {
            Inner::Fast(fast) => fast.push_limit,
            Inner::Reference(flyer) => flyer.push_limit,
        }
    }

    /// True while the fast engine is in use (false after a reference fallback).
    pub fn is_fast(&self) -> bool {
        matches!(self.inner, Inner::Fast(_))
    }

    pub fn rng_state(&self) -> u64 {
        match &self.inner {
            Inner::Fast(fast) => fast.rng_state,
            Inner::Reference(flyer) => flyer.rng_state,
        }
    }

    /// Same result as `Flyer::tick()` on the equivalent flyer.
    pub fn tick(&mut self) -> Result<TickReport, Error> {
        if let Inner::Fast(fast) = &self.inner {
            if !fast.safe() {
                let flyer = fast.to_flyer();
                self.inner = Inner::Reference(Box::new(flyer));
            }
        }
        match &mut self.inner {
            Inner::Fast(fast) => fast.tick(),
            Inner::Reference(flyer) => flyer.tick(),
        }
    }

    /// Minimum occupied X (0 when empty), as used by the bank statistics.
    pub fn minimum_x(&self) -> i64 {
        match &self.inner {
            Inner::Fast(fast) => fast.minimum_x(),
            Inner::Reference(flyer) => flyer.blocks().iter().map(|(p, _)| p.x).min().unwrap_or(0),
        }
    }

    /// Count of each block kind except piston arms, indexed by kind number.
    pub fn signature(&self) -> [usize; 10] {
        let mut result = [0; 10];
        match &self.inner {
            Inner::Fast(fast) => {
                for &cell in &fast.grid.cells {
                    let k = kind(cell);
                    if k != 0 && k != ARM {
                        result[k as usize] += 1;
                    }
                }
            }
            Inner::Reference(flyer) => {
                for (_, block) in flyer.blocks() {
                    if block.kind() != Kind::PistonArm {
                        result[block.kind() as usize] += 1;
                    }
                }
            }
        }
        result
    }
}

/// Movement diagnostics matching the reference trace; see
/// `FastFlyer::tick_diagnosed`. Accumulates across ticks until cleared.
#[derive(Clone, Debug, Default)]
pub struct Diagnostics {
    pub failures: Vec<(Coord, &'static str)>,
    pub max_successful_action: usize,
}

/// Deep copy through the public API (Flyer is not Clone).
pub fn clone_flyer(flyer: &Flyer) -> Flyer {
    let mut copy = Flyer::new(flyer.phase_x, flyer.phase_z, flyer.rng_state, flyer.push_limit)
        .expect("valid phases");
    let blocks = flyer.blocks();
    for &(pos, block) in &blocks {
        copy.set(pos, block);
    }
    for &(pos, block) in &blocks {
        if block.kind() == Kind::Piston {
            let list = flyer.piston_blocks(pos);
            if !list.is_empty() {
                copy.set_piston_blocks(pos, list.to_vec())
                    .expect("copied list is valid");
            }
        }
    }
    copy
}

fn invalid(message: &str) -> Error {
    Error::Format(message.to_owned())
}

/// Window around [lo, hi] with per-side margins in the order
/// (-x, +x, -y, +y, -z, +z) of extra room below lo and above hi.
fn window(lo: Coord, hi: Coord, margins: [i64; 6]) -> Option<(Coord, Coord)> {
    let limit = SAFE / 2;
    for v in [lo.x, lo.y, lo.z, hi.x, hi.y, hi.z] {
        if !(-limit..limit).contains(&v) {
            return None;
        }
    }
    let wlo = Coord::new(lo.x - margins[0], lo.y - margins[2], lo.z - margins[4]);
    let whi = Coord::new(hi.x + margins[1], hi.y + margins[3], hi.z + margins[5]);
    let pow2 = |n: i64| (n as u64).checked_next_power_of_two().map(|v| v as i64);
    let cells = (whi.x - wlo.x + 1)
        .checked_mul(pow2(whi.y - wlo.y + 1)?)?
        .checked_mul(pow2(whi.z - wlo.z + 1)?)?;
    (cells <= MAX_CELLS).then_some((wlo, whi))
}

impl Fast {
    fn from_flyer(flyer: &Flyer) -> Option<Self> {
        let blocks = flyer.blocks();
        let (lo, hi) = match blocks.first() {
            None => (Coord::new(0, 0, 0), Coord::new(0, 0, 0)),
            Some(&(first, _)) => blocks.iter().fold((first, first), |(lo, hi), &(p, _)| {
                (
                    Coord::new(lo.x.min(p.x), lo.y.min(p.y), lo.z.min(p.z)),
                    Coord::new(hi.x.max(p.x), hi.y.max(p.y), hi.z.max(p.z)),
                )
            }),
        };
        let (lo, hi) = window(lo, hi, [MARGIN; 6])?;
        let mut fast = Self {
            phase_x: flyer.phase_x as i64,
            phase_z: flyer.phase_z as i64,
            rng_state: flyer.rng_state,
            push_limit: flyer.push_limit,
            grid: Grid::new(lo, hi),
            lists: FxMap::default(),
            chunk_counts: Vec::new(),
            pistons: Vec::new(),
            piston_ranges: Vec::new(),
            rods: Vec::new(),
            added_pistons: Vec::new(),
            added_rods: Vec::new(),
            pulsed: Vec::new(),
            hard: Vec::new(),
            queue: Vec::new(),
            entries: Vec::new(),
            key_scratch: Vec::new(),
            merge_scratch: Vec::new(),
            candidates: Vec::new(),
            kinds: [0; 16],
            pool: Vec::new(),
            diag: None,
        };
        for &(pos, block) in &blocks {
            let cell = block.cell();
            let i = fast.grid.index(pos).expect("window covers blocks");
            fast.grid.cells[i] = cell;
            fast.kinds[kind(cell) as usize] += 1;
            fast.indexed_add(pos, cell);
            if kind(cell) == PISTON {
                let list = flyer.piston_blocks(pos);
                if !list.is_empty() {
                    fast.lists.insert(pos, list.to_vec());
                }
            }
            if kind(cell) == OBSERVER && cell & BIT8 != 0 {
                fast.pulsed.push(pos);
            }
        }
        fast.rebuild_indexes();
        Some(fast)
    }

    fn to_flyer(&self) -> Flyer {
        let mut flyer = Flyer::new(
            self.phase_x as u8,
            self.phase_z as u8,
            self.rng_state,
            self.push_limit,
        )
        .expect("valid phases");
        for (pos, cell) in self.grid.occupied() {
            flyer.set(pos, Block::from_cell(cell & !FLAGS).expect("valid cell"));
        }
        let mut owners: Vec<_> = self.lists.keys().copied().collect();
        owners.sort();
        for owner in owners {
            flyer
                .set_piston_blocks(owner, self.lists[&owner].clone())
                .expect("valid list");
        }
        flyer
    }

    fn minimum_x(&self) -> i64 {
        let g = &self.grid;
        let slab = g.slab();
        (0..g.sx as usize)
            .find(|&x| g.cells[x * slab..(x + 1) * slab].iter().any(|&c| c != 0))
            .map_or(0, |x| g.ox + x as i64)
    }

    fn safe(&self) -> bool {
        let g = &self.grid;
        g.cells.len() as i64 <= MAX_CELLS
            && -SAFE < g.ox
            && g.ox + g.sx < SAFE
            && -SAFE < g.oy
            && g.oy + g.sy() < SAFE
            && -SAFE < g.oz
            && g.oz + g.sz() < SAFE
    }

    #[inline]
    fn chunk_key(&self, pos: Coord) -> (i64, i64) {
        ((pos.x + self.phase_x) >> 4, (pos.z + self.phase_z) >> 4)
    }

    #[inline]
    fn chunk_count(&mut self, pos: Coord) -> &mut u32 {
        let key = self.chunk_key(pos);
        let index = match self.chunk_counts.iter().position(|entry| entry.0 == key) {
            Some(index) => index,
            None => {
                self.chunk_counts.push((key, 0));
                self.chunk_counts.len() - 1
            }
        };
        &mut self.chunk_counts[index].1
    }

    /// Bookkeeping for a block that now occupies `pos`.
    #[inline]
    fn indexed_add(&mut self, pos: Coord, cell: u16) {
        *self.chunk_count(pos) += 1;
        self.note_placed(pos, cell);
    }

    #[inline]
    fn note_placed(&mut self, pos: Coord, cell: u16) {
        match kind(cell) {
            PISTON => self.added_pistons.push(pos),
            ROD => self.added_rods.push(pos),
            _ => {}
        }
    }

    /// Bookkeeping for a block that no longer occupies `pos`. Pistons and
    /// rods leave their lists lazily, in `rebuild_indexes`.
    #[inline]
    fn indexed_remove(&mut self, pos: Coord) {
        *self.chunk_count(pos) -= 1;
    }

    /// (chunk x, chunk z, grid index), relative to the window and packed so
    /// that integer order is (world chunk, Coord) order: index order within
    /// a window is Coord order. `pos` must be in the window.
    #[inline]
    fn piston_key(&self, pos: Coord, index: usize) -> u128 {
        let g = &self.grid;
        let cx0 = (g.ox + self.phase_x) >> 4;
        let cz0 = (g.oz + self.phase_z) >> 4;
        ((((pos.x + self.phase_x) >> 4) - cx0) as u128) << 80
            | ((((pos.z + self.phase_z) >> 4) - cz0) as u128) << 40
            | index as u128
    }

    #[inline]
    fn key_index(key: u128) -> usize {
        (key as u64 & ((1 << 40) - 1)) as usize
    }

    /// Absolute world chunk of a piston key.
    fn key_chunk(&self, key: u128) -> (i64, i64) {
        let g = &self.grid;
        (
            ((g.ox + self.phase_x) >> 4) + (key >> 80) as i64,
            ((g.oz + self.phase_z) >> 4) + ((key >> 40) as u64 & ((1 << 40) - 1)) as i64,
        )
    }

    /// Make `pistons` and `rods` exact again: keep entries whose cell still
    /// holds that kind, add placed ones, drop duplicates.
    fn rebuild_indexes(&mut self) {
        let _prof = prof::Prof::new(7);
        let grid = &self.grid;
        self.pistons
            .retain(|&key| kind(grid.cells[Self::key_index(key)]) == PISTON);
        if !self.added_pistons.is_empty() {
            let mut added = std::mem::take(&mut self.added_pistons);
            let mut keys = std::mem::take(&mut self.key_scratch);
            keys.clear();
            keys.extend(added.iter().filter_map(|&p| {
                let i = self.grid.index(p)?;
                (kind(self.grid.cells[i]) == PISTON).then(|| self.piston_key(p, i))
            }));
            keys.sort_unstable();
            keys.dedup();
            let list = &self.pistons;
            let mut merged = std::mem::take(&mut self.merge_scratch);
            merged.clear();
            let (mut a, mut b) = (0, 0);
            while a < list.len() && b < keys.len() {
                if list[a] < keys[b] {
                    merged.push(list[a]);
                    a += 1;
                } else {
                    merged.push(keys[b]);
                    a += (list[a] == keys[b]) as usize;
                    b += 1;
                }
            }
            merged.extend_from_slice(&list[a..]);
            merged.extend_from_slice(&keys[b..]);
            self.merge_scratch = std::mem::replace(&mut self.pistons, merged);
            self.key_scratch = keys;
            added.clear();
            self.added_pistons = added;
        }
        let grid = &self.grid;
        self.rods.retain(|&p| kind(grid.get(p)) == ROD);
        if !self.added_rods.is_empty() {
            for &p in &self.added_rods {
                if kind(grid.get(p)) == ROD {
                    self.rods.push(p);
                }
            }
            self.added_rods.clear();
            self.rods.sort_unstable();
            self.rods.dedup();
        }
    }

    /// Recompute piston keys for a new window. Their order is unchanged.
    fn rekey(&mut self, old: &Grid) {
        for index in 0..self.pistons.len() {
            let pos = old.coord(Self::key_index(self.pistons[index]));
            let i = self.grid.index(pos).unwrap();
            self.pistons[index] = self.piston_key(pos, i);
        }
    }

    #[inline]
    fn get(&self, pos: Coord) -> u16 {
        self.grid.get(pos)
    }

    /// Overwrite a cell in place, keeping simulator flags (reference `set`
    /// with the same kind, which leaves the power cache alone).
    #[inline]
    fn set_same_kind(&mut self, pos: Coord, cell: u16) {
        let i = self.grid.index(pos).unwrap();
        let old = self.grid.cells[i];
        self.grid.cells[i] = (old & FLAGS) | cell;
    }

    /// Reference `remove_indexed`.
    fn remove_indexed(&mut self, pos: Coord) {
        let Some(i) = self.grid.index(pos) else { return };
        let old = self.grid.cells[i];
        if old != 0 {
            self.kinds[kind(old) as usize] -= 1;
            // Lists exist only at piston cells.
            if kind(old) == PISTON {
                self.lists.remove(&pos);
            }
            self.grid.cells[i] = 0;
            self.indexed_remove(pos);
        }
    }

    /// Reference `place_indexed` at a neighbour of a block.
    fn place_indexed(&mut self, pos: Coord, cell: u16) {
        let i = self.grid.index(pos).expect("neighbours of blocks are in the window");
        let old = self.grid.cells[i];
        if old != 0 {
            if kind(old) == PISTON && kind(cell) != PISTON {
                self.lists.remove(&pos);
            }
            self.kinds[kind(old) as usize] -= 1;
            self.indexed_remove(pos);
        }
        self.grid.cells[i] = cell;
        self.kinds[kind(cell) as usize] += 1;
        self.indexed_add(pos, cell);
        let border = self.grid.border_sides(i);
        if border != 0 {
            self.relocate(border);
        }
    }

    /// Move or rebuild the window so that every block is at least one layer
    /// inside it again. `sides` are the border sides that blocks reached.
    #[cold]
    fn relocate(&mut self, sides: u8) {
        let _prof = prof::Prof::new(4);
        if (sides == 1 || sides == 2) && self.shift_x(sides == 2) {
            return;
        }
        let (lo, hi) = self.grid.bounds().expect("a block is on the border");
        let extent = [hi.x - lo.x, hi.y - lo.y, hi.z - lo.z];
        let mut margins = [MARGIN; 6];
        for (side, margin) in margins.iter_mut().enumerate() {
            if sides & (1 << side) != 0 {
                *margin = FORWARD.max(2 * extent[side / 2]);
            }
        }
        // A window over the limit is still exact, just large; the next
        // tick's safety check then hands over to the reference simulator.
        let (lo, hi) = window(lo, hi, margins).unwrap_or((
            Coord::new(lo.x - 1, lo.y - 1, lo.z - 1),
            Coord::new(hi.x + 1, hi.y + 1, hi.z + 1),
        ));
        let mut grid = Grid::new(lo, hi);
        for (p, cell) in self.grid.occupied() {
            let i = grid.index(p).unwrap();
            grid.cells[i] = cell;
        }
        let old = std::mem::replace(&mut self.grid, grid);
        self.rekey(&old);
    }

    /// Slide the window along X, keeping its size, when the blocks fit with
    /// MARGIN behind and FORWARD (or twice their length) ahead.
    fn shift_x(&mut self, forward: bool) -> bool {
        let g = &mut self.grid;
        let slab = g.slab();
        let sx = g.sx as usize;
        let filled = |x: usize| g.cells[x * slab..(x + 1) * slab].iter().any(|&c| c != 0);
        let Some(xmin) = (0..sx).find(|&x| filled(x)) else { return false };
        let xmax = (0..sx).rev().find(|&x| filled(x)).unwrap();
        let length = (xmax - xmin + 1) as i64;
        let ahead = FORWARD.max(2 * length);
        if length + MARGIN + ahead > g.sx {
            return false;
        }
        // New origin, in slabs relative to the old one.
        let shift = if forward {
            xmin as i64 - MARGIN
        } else {
            xmax as i64 + MARGIN + 1 - g.sx
        };
        let cells = g.cells.len();
        if shift > 0 {
            let k = shift as usize * slab;
            g.cells.copy_within(k.., 0);
            g.cells[cells - k..].fill(0);
        } else if shift < 0 {
            let k = (-shift) as usize * slab;
            g.cells.copy_within(..cells - k, k);
            g.cells[..k].fill(0);
        }
        let old = g.shape();
        g.ox += shift;
        self.rekey(&old);
        true
    }

    fn set_list(&mut self, owner: Coord, mut blocks: Vec<Coord>) -> Result<(), Error> {
        if kind(self.get(owner)) != PISTON {
            return Err(invalid("owner coordinate must contain a piston"));
        }
        if (blocks.len() as u64) > self.push_limit {
            return Err(invalid("piston list exceeds push limit"));
        }
        blocks.sort_unstable();
        if blocks.windows(2).any(|pair| pair[0] == pair[1]) {
            return Err(invalid("piston list contains duplicate coordinates"));
        }
        self.set_valid_list(owner, blocks);
        Ok(())
    }

    /// `set_piston_blocks` for a duplicate-free list within the push limit,
    /// at a piston. Lists are kept unsorted; `to_flyer` sorts them.
    #[inline]
    fn set_valid_list(&mut self, owner: Coord, list: Vec<Coord>) {
        let old = if list.is_empty() {
            self.recycle(list);
            self.lists.remove(&owner)
        } else {
            self.lists.insert(owner, list)
        };
        if let Some(old) = old {
            self.recycle(old);
        }
    }

    #[inline]
    fn recycle(&mut self, mut list: Vec<Coord>) {
        if list.capacity() != 0 && self.pool.len() < 64 {
            list.clear();
            self.pool.push(list);
        }
    }

    fn next_random_u64(&mut self) -> u64 {
        let mut rng = ShuffleRng(self.rng_state);
        let value = rng.next();
        self.rng_state = rng.0;
        value
    }

    /// Returns the number of powered pistons; marks them with F_POWERED.
    fn power_stage(&mut self) -> usize {
        let _prof = prof::Prof::new(0);
        // Hard power from stationary rods and powered observers.
        let mut hard = std::mem::take(&mut self.hard);
        hard.clear();
        for index in 0..self.rods.len() + self.pulsed.len() {
            let pos = if index < self.rods.len() {
                self.rods[index]
            } else {
                self.pulsed[index - self.rods.len()]
            };
            let Some(i) = self.grid.index(pos) else { continue };
            let cell = self.grid.cells[i];
            if moving(cell) {
                continue;
            }
            let source = kind(cell) == ROD || (kind(cell) == OBSERVER && cell & BIT8 != 0);
            if !source {
                continue;
            }
            let t = i.wrapping_add(self.grid.delta[direction(cell)]);
            let target = self.grid.cells[t];
            if target != 0
                && !moving(target)
                && matches!(kind(target), SLIME | HONEY | SMOOTH_STONE | GLAZED)
                && target & F_HARD == 0
            {
                self.grid.cells[t] = target | F_HARD;
                hard.push(t);
            }
        }

        let mut powered = 0;
        let grid = &mut self.grid;
        {
            for &key in &self.pistons {
                let i = Self::key_index(key);
                let cell = grid.cells[i] & !F_POWERED;
                grid.cells[i] = cell;
                if moving(cell) {
                    continue;
                }
                let front = direction(cell);
                let mut on = false;
                for d in 0..6 {
                    if d == front {
                        continue;
                    }
                    let ni = i.wrapping_add(grid.delta[d]);
                    let n = grid.cells[ni];
                    if n == 0 {
                        continue;
                    }
                    if n & F_HARD != 0 {
                        on = true;
                        break;
                    }
                    if moving(n) {
                        continue;
                    }
                    let k = kind(n);
                    // An observer faces the piston when its direction is
                    // the opposite of the piston-to-observer direction.
                    if k == ROD || k == REDSTONE || (k == OBSERVER && n & BIT8 != 0 && direction(n) == opposite(d))
                    {
                        on = true;
                        break;
                    }
                }
                if on {
                    grid.cells[i] = cell | F_POWERED;
                    powered += 1;
                } else {
                    // Moving pistons retain angry, including when they have
                    // no power. (Reference: after the power stage.)
                    grid.cells[i] = cell & !ANGRY;
                }
            }
        }

        for &i in &hard {
            self.grid.cells[i] &= !F_HARD;
        }
        self.hard = hard;

        // Every observer turns off, including moving observers.
        for index in 0..self.pulsed.len() {
            let pos = self.pulsed[index];
            if let Some(i) = self.grid.index(pos) {
                let cell = self.grid.cells[i];
                if kind(cell) == OBSERVER {
                    self.grid.cells[i] = cell & !BIT8;
                }
            }
        }
        self.pulsed.clear();
        powered
    }

    fn tick(&mut self) -> Result<TickReport, Error> {
        let _prof = prof::Prof::new(6);
        let powered = self.power_stage();
        let mut report = TickReport {
            powered_pistons: powered,
            ..TickReport::default()
        };

        self.piston_ranges.clear();
        let mut start = 0;
        for index in 0..self.pistons.len() {
            let part = self.pistons[index] >> 40;
            if self.pistons.get(index + 1).map(|&k| k >> 40) != Some(part) {
                let chunk = self.key_chunk(self.pistons[index]);
                self.piston_ranges.push((chunk, start, index + 1));
                start = index + 1;
            }
        }

        self.chunk_counts.retain(|entry| entry.1 != 0);
        let mut chunks: Vec<(i64, i64)> = self.chunk_counts.iter().map(|entry| entry.0).collect();
        chunks.sort_unstable();
        let tick_seed = self.next_random_u64();
        let minimum_chunk_x = chunks.iter().map(|chunk| chunk.0).min().unwrap_or(0);
        let minimum_chunk_z = chunks.iter().map(|chunk| chunk.1).min().unwrap_or(0);
        shuffle(&mut chunks, tick_seed);
        report.chunks_ticked = chunks.len();

        let mut candidates = std::mem::take(&mut self.candidates);
        let result = self.run_chunks(
            &chunks,
            minimum_chunk_x,
            minimum_chunk_z,
            tick_seed,
            &mut candidates,
            &mut report,
        );
        self.candidates = candidates;
        self.rebuild_indexes();
        result.map(|()| report)
    }

    fn run_chunks(
        &mut self,
        chunks: &[(i64, i64)],
        minimum_chunk_x: i64,
        minimum_chunk_z: i64,
        tick_seed: u64,
        pistons: &mut Vec<Coord>,
        report: &mut TickReport,
    ) -> Result<(), Error> {
        let _prof = prof::Prof::new(5);
        for &chunk in chunks {
            // The reference reads this chunk's current pistons, sorted, and
            // drops moving ones.
            pistons.clear();
            if let Some(&(_, start, end)) = self.piston_ranges.iter().find(|r| r.0 == chunk) {
                for &key in &self.pistons[start..end] {
                    let i = Self::key_index(key);
                    let cell = self.grid.cells[i];
                    if kind(cell) == PISTON && !moving(cell) {
                        pistons.push(self.grid.coord(i));
                    }
                }
            }
            let mut extra = false;
            for &pos in &self.added_pistons {
                let cell = self.grid.get(pos);
                if kind(cell) == PISTON && !moving(cell) && self.chunk_key(pos) == chunk {
                    pistons.push(pos);
                    extra = true;
                }
            }
            if extra {
                pistons.sort_unstable();
                pistons.dedup();
            }
            let relative_x = chunk.0.wrapping_sub(minimum_chunk_x) as u64;
            let relative_z = chunk.1.wrapping_sub(minimum_chunk_z) as u64;
            let chunk_seed = tick_seed
                ^ relative_x.wrapping_mul(0x517cc1b727220a95)
                ^ relative_z.wrapping_mul(0x6c8e9cf570932bd5);
            shuffle(pistons, chunk_seed);
            for index in 0..pistons.len() {
                let pos = pistons[index];
                // An earlier piston in this chunk may have moved this one.
                let cell = self.get(pos);
                if kind(cell) != PISTON || moving(cell) {
                    continue;
                }
                let cell_powered = cell & F_POWERED != 0;
                let cell = cell & !FLAGS;
                match state(cell) {
                    0 if cell_powered || cell & ANGRY != 0 => {
                        report.extension_attempts += 1;
                        if self.start_extension(pos, cell, report)? {
                            report.extensions_started += 1;
                        } else {
                            report.extension_failures += 1;
                            self.set_same_kind(pos, (cell & !(MOVING | STATE)) | ANGRY);
                        }
                    }
                    1 => {
                        self.finish_movement(pos, cell, 2);
                        report.extensions_finished += 1;
                    }
                    2 if !cell_powered => {
                        self.start_retraction(pos, cell, report)?;
                        report.retractions_started += 1;
                    }
                    3 => {
                        self.finish_movement(pos, cell, 0);
                        report.retractions_finished += 1;
                    }
                    _ => {}
                }
            }
        }
        Ok(())
    }

    #[inline]
    fn immovable(cell: u16) -> bool {
        moving(cell) || kind(cell) == ARM || (kind(cell) == PISTON && cell & STATE != 0)
    }

    /// Reference `discover_move`; `None` on failure. Returns the cell
    /// indices in visit order; the reference's sorted order only matters
    /// where lists are compared or saved, and those sort for themselves. The closure and the failure verdict do not depend on the
    /// visit order, so marking cells when queued instead of when visited
    /// gives the same answer.
    fn discover_move(
        &mut self,
        first: Coord,
        dir: usize,
        owner: Coord,
        pulling: bool,
    ) -> Option<Vec<usize>> {
        let _prof = prof::Prof::new(1);
        // Cells outside the window are empty.
        let Some(first) = self.grid.index(first) else {
            return Some(Vec::new());
        };
        let first_cell = self.grid.cells[first];
        if first_cell == 0 {
            return Some(Vec::new());
        }
        if pulling && kind(first_cell) == GLAZED {
            return None;
        }
        let owner = self.grid.index(owner).unwrap();
        let grid = &mut self.grid;
        // The initiating piston is immovable for its own move: give it the
        // moving bit while discovering, then restore it.
        let owner_cell = grid.cells[owner];
        grid.cells[owner] = owner_cell | MOVING;
        let delta = grid.delta;
        let mut queue = std::mem::take(&mut self.queue);
        queue.clear();
        queue.push(first);
        grid.cells[first] |= F_MARK;
        let mut head = 0;
        let mut ok = true;
        // Every queued cell is occupied, so it is off the border and its
        // neighbours are inside the window.
        while head < queue.len() {
            let i = queue[head];
            head += 1;
            let cell = grid.cells[i];
            if Self::immovable(cell) || head as u64 > self.push_limit {
                ok = false;
                break;
            }
            let k = kind(cell);
            if k == SLIME || k == HONEY {
                let other = k ^ (SLIME ^ HONEY);
                for &dl in &delta {
                    let ni = i.wrapping_add(dl);
                    let n = grid.cells[ni];
                    if n == 0 || n & F_MARK != 0 {
                        continue;
                    }
                    let nk = kind(n);
                    if nk != GLAZED && nk != other && !Self::immovable(n) {
                        grid.cells[ni] = n | F_MARK;
                        queue.push(ni);
                    }
                }
            }
            let di = i.wrapping_add(delta[dir]);
            let n = grid.cells[di];
            if n != 0 && n & F_MARK == 0 {
                grid.cells[di] = n | F_MARK;
                queue.push(di);
            }
        }
        for &i in &queue {
            grid.cells[i] &= !F_MARK;
        }
        grid.cells[owner] = owner_cell;
        if ok {
            Some(queue)
        } else {
            self.queue = queue;
            None
        }
    }

    /// Faithful port of the reference `describe_discovery` (used by
    /// `tick_traced`), in its exact visit order: the failure `(position,
    /// reason)` if any, and the number of sources. Only run for diagnostics.
    fn describe_discovery(
        &self,
        first: Coord,
        dir: usize,
        owner: Coord,
        pulling: bool,
    ) -> (Option<(Coord, &'static str)>, usize) {
        let immovable = |pos: Coord, cell: u16| pos == owner || Self::immovable(cell);
        let initial = self.get(first);
        if initial == 0 {
            return (None, 0);
        }
        if pulling && kind(initial) == GLAZED {
            return (Some((first, "glazed terracotta cannot be pulled")), 0);
        }
        let front = step(owner, opposite(dir));
        let mut queue = std::collections::VecDeque::from([first]);
        let mut selected = std::collections::HashSet::new();
        while let Some(pos) = queue.pop_front() {
            if selected.contains(&pos) {
                continue;
            }
            let cell = self.get(pos);
            if cell == 0 {
                continue;
            }
            if immovable(pos, cell) {
                return (Some((pos, "immovable obstruction")), selected.len());
            }
            selected.insert(pos);
            if selected.len() as u64 > self.push_limit {
                return (Some((pos, "push limit exceeded")), selected.len());
            }
            let k = kind(cell);
            if k == SLIME || k == HONEY {
                for side in 0..6 {
                    let neighbor_pos = step(pos, side);
                    let n = self.get(neighbor_pos);
                    if n == 0 || immovable(neighbor_pos, n) {
                        continue;
                    }
                    let nk = kind(n);
                    let adheres = nk != GLAZED
                        && !((k == SLIME && nk == HONEY) || (k == HONEY && nk == SLIME));
                    if adheres {
                        queue.push_back(neighbor_pos);
                    }
                }
            }
            let destination = step(pos, dir);
            if self.get(destination) != 0 && !selected.contains(&destination) {
                // The retracting arm is removed before discovery.
                if !(pulling && destination == front) {
                    queue.push_back(destination);
                }
            }
        }
        (None, selected.len())
    }

    /// The trace outcome of a discovery, if diagnostics are collected.
    fn diagnose(
        &self,
        found: Option<usize>,
        first: Coord,
        dir: usize,
        owner: Coord,
        pulling: bool,
    ) -> Option<(Option<(Coord, &'static str)>, usize)> {
        self.diag.as_ref()?;
        Some(match found {
            Some(len) => (None, len),
            None => self.describe_discovery(first, dir, owner, pulling),
        })
    }

    /// Add an action's trace outcome. The reference captures the step after
    /// the action, so an action that returns an error records nothing.
    fn record(&mut self, outcome: Option<(Option<(Coord, &'static str)>, usize)>) {
        let (Some(diag), Some(outcome)) = (self.diag.as_mut(), outcome) else { return };
        match outcome {
            (Some(failure), _) => diag.failures.push(failure),
            (None, len) => diag.max_successful_action = diag.max_successful_action.max(len),
        }
    }

    /// Whether moving the block at index `i` one step along `dir` crosses a
    /// world chunk boundary.
    #[inline]
    fn crosses_chunk(&self, i: usize, dir: usize) -> bool {
        match dir {
            0 => (self.grid.x_of(i) + self.phase_x) & 15 == 15,
            1 => (self.grid.x_of(i) + self.phase_x) & 15 == 0,
            4 => (self.grid.z_of(i) + self.phase_z) & 15 == 15,
            5 => (self.grid.z_of(i) + self.phase_z) & 15 == 0,
            _ => false,
        }
    }

    /// Reference `move_blocks`; returns the destination coordinates in the
    /// order of `sources`. The reference's order of removals, placements and
    /// list updates only matters for the list updates, whose failures
    /// depend on the order; those are applied in sorted source order. Discovery guarantees that every occupied
    /// destination is itself a source, so all destinations are empty once
    /// the sources are removed.
    fn move_blocks(&mut self, sources: &[usize], dir: usize) -> Result<Vec<Coord>, Error> {
        let _prof = prof::Prof::new(2);
        let mut entries = std::mem::take(&mut self.entries);
        entries.clear();
        let mut moved_lists = Vec::new();
        for &i in sources {
            let cell = self.grid.cells[i] & !FLAGS;
            self.grid.cells[i] = 0;
            if kind(cell) == PISTON {
                let source = self.grid.coord(i);
                if let Some(list) = self.lists.remove(&source) {
                    moved_lists.push((step(source, dir), list));
                }
            }
            let crosses = self.crosses_chunk(i, dir);
            if crosses {
                self.indexed_remove(self.grid.coord(i));
            }
            entries.push((i, cell, crosses));
        }
        let mut destinations = self.pool.pop().unwrap_or_default();
        let mut border = false;
        let delta = self.grid.delta[dir];
        for &(i, cell, crosses) in &entries {
            let di = i.wrapping_add(delta);
            let moved = if kind(cell) == OBSERVER {
                (cell & !BIT8) | MOVING
            } else {
                cell | MOVING
            };
            debug_assert_eq!(self.grid.cells[di], 0);
            self.grid.cells[di] = moved;
            let destination = self.grid.coord(di);
            if crosses {
                *self.chunk_count(destination) += 1;
            }
            if matches!(kind(moved), PISTON | ROD) {
                self.note_placed(destination, moved);
            }
            // Sources are off the border, so a destination can only reach
            // the side it moved towards.
            border |= self.grid.at_side(di, dir);
            destinations.push(destination);
        }
        self.entries = entries;
        if border {
            // border_sides numbers sides -x first; DIRECTIONS starts at +x.
            self.relocate(1 << (dir ^ 1));
        }
        moved_lists.sort_unstable_by_key(|entry: &(Coord, Vec<Coord>)| entry.0);
        for (destination, list) in moved_lists {
            let translated = list
                .iter()
                .map(|&member| {
                    if destinations.contains(&step(member, dir)) {
                        step(member, dir)
                    } else {
                        member
                    }
                })
                .collect();
            self.set_list(destination, translated)?;
        }
        Ok(destinations)
    }

    fn start_extension(
        &mut self,
        pos: Coord,
        piston: u16,
        report: &mut TickReport,
    ) -> Result<bool, Error> {
        let dir = direction(piston);
        let front = step(pos, dir);
        let found = self.discover_move(front, dir, pos, false);
        let outcome = self.diagnose(found.as_ref().map(Vec::len), front, dir, pos, false);
        let Some(sources) = found else {
            self.record(outcome);
            return Ok(false);
        };
        let destinations = self.move_blocks(&sources, dir)?;
        self.queue = sources;
        report.blocks_moved += destinations.len();
        self.place_indexed(front, ARM);
        self.set_same_kind(pos, (piston & !(MOVING | STATE | ANGRY)) | (1 << 10));
        self.set_valid_list(pos, destinations);
        self.record(outcome);
        Ok(true)
    }

    fn start_retraction(
        &mut self,
        pos: Coord,
        piston: u16,
        report: &mut TickReport,
    ) -> Result<(), Error> {
        let dir = direction(piston);
        let front = step(pos, dir);
        let sticky = piston & BIT8 != 0;
        // The reference describes the pull before removing the front cell.
        // That only differs from describing it afterwards when the front
        // holds a movable block (normally it holds the immovable arm).
        let mut outcome = None;
        if sticky && self.diag.is_some() {
            let f = self.get(front);
            if f != 0 && !Self::immovable(f) {
                outcome = Some(self.describe_discovery(step(front, dir), opposite(dir), pos, true));
            }
        }
        self.remove_indexed(front);
        let mut destinations = Vec::new();
        if sticky {
            let first = step(front, dir);
            let found = self.discover_move(first, opposite(dir), pos, true);
            if outcome.is_none() {
                outcome = self.diagnose(found.as_ref().map(Vec::len), first, opposite(dir), pos, true);
            }
            if let Some(sources) = found {
                destinations = self.move_blocks(&sources, opposite(dir))?;
                self.queue = sources;
                report.blocks_moved += destinations.len();
            }
        }
        self.set_same_kind(pos, (piston & !(MOVING | STATE)) | (3 << 10));
        self.set_valid_list(pos, destinations);
        self.record(outcome);
        Ok(())
    }

    fn finish_movement(&mut self, pos: Coord, piston: u16, next_state: u16) {
        let _prof = prof::Prof::new(3);
        // finish_moved_block never touches lists, so removing first is the
        // same as the reference's finish-then-clear.
        if let Some(destinations) = self.lists.remove(&pos) {
            for &destination in &destinations {
                self.finish_moved_block(destination);
            }
            self.recycle(destinations);
        }
        self.set_same_kind(pos, (piston & !(MOVING | STATE)) | (next_state << 10));
    }

    fn finish_moved_block(&mut self, pos: Coord) {
        let Some(i) = self.grid.index(pos) else { return };
        let cell = self.grid.cells[i];
        if cell == 0 {
            return;
        }
        if kind(cell) == OBSERVER {
            self.grid.cells[i] = (cell & !MOVING) | BIT8;
            self.pulsed.push(pos);
        } else {
            self.grid.cells[i] = cell & !MOVING;
        }
    }
}

/// Cycle counters for `--features profile`; free otherwise.
pub mod prof {
    #[cfg(feature = "profile")]
    pub static COUNTERS: [std::sync::atomic::AtomicU64; 8] =
        [const { std::sync::atomic::AtomicU64::new(0) }; 8];

    #[cfg(feature = "profile")]
    pub static EVENTS: [std::sync::atomic::AtomicU64; 4] =
        [const { std::sync::atomic::AtomicU64::new(0) }; 4];

    #[inline(always)]
    #[allow(unused_variables)]
    pub fn count(slot: usize) {
        #[cfg(feature = "profile")]
        EVENTS[slot].fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    }

    pub struct Prof {
        #[cfg(feature = "profile")]
        slot: usize,
        #[cfg(feature = "profile")]
        start: u64,
    }

    impl Prof {
        #[inline(always)]
        #[allow(unused_variables)]
        pub fn new(slot: usize) -> Self {
            Self {
                #[cfg(feature = "profile")]
                slot,
                #[cfg(feature = "profile")]
                start: unsafe { core::arch::x86_64::_rdtsc() },
            }
        }
    }

    #[cfg(feature = "profile")]
    impl Drop for Prof {
        fn drop(&mut self) {
            let now = unsafe { core::arch::x86_64::_rdtsc() };
            COUNTERS[self.slot]
                .fetch_add(now - self.start, std::sync::atomic::Ordering::Relaxed);
        }
    }
}
