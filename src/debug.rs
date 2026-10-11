//! In-memory diagnostic trace for the local viewer. It is separate from the
//! persistent `.flyer` format and any future trajectory representation.

use std::collections::BTreeMap;
use std::fmt::Write;

use crate::{Coord, Flyer};

pub type Chunk = (i64, i64);

#[derive(Clone, Debug)]
pub struct Link {
    pub from: Coord,
    pub to: Coord,
    pub kind: &'static str,
}

#[derive(Clone, Debug, Default)]
pub struct MoveOverlay {
    pub sources: Vec<Coord>,
    pub destinations: Vec<Coord>,
    pub links: Vec<Link>,
    pub ignored: Vec<Link>,
    pub failure: Option<(Coord, &'static str)>,
}

#[derive(Clone, Debug, Default)]
pub struct StepInfo {
    pub title: String,
    pub stage: &'static str,
    pub action: Option<&'static str>,
    pub tick: usize,
    pub chunk_order: Vec<Chunk>,
    pub active_chunk: Option<Chunk>,
    pub active_piston: Option<Coord>,
    pub movement: Option<MoveOverlay>,
}

#[derive(Clone, Debug)]
pub struct CellChange {
    pub pos: Coord,
    pub cell: Option<u16>,
}

#[derive(Clone, Debug)]
pub struct DebugStep {
    pub info: StepInfo,
    pub changes: Vec<CellChange>,
    pub owners: Vec<(Coord, Coord)>,
    pub arms: Vec<(Coord, u8)>,
}

#[derive(Clone, Debug)]
pub struct TickTrace {
    pub phase_x: u8,
    pub phase_z: u8,
    pub push_limit: u64,
    pub initial: Vec<(Coord, u16)>,
    pub initial_owners: Vec<(Coord, Coord)>,
    pub initial_arms: Vec<(Coord, u8)>,
    pub steps: Vec<DebugStep>,
    previous: BTreeMap<Coord, u16>,
}

impl TickTrace {
    pub fn new(flyer: &Flyer) -> Self {
        let previous: BTreeMap<Coord, u16> = flyer
            .blocks()
            .into_iter()
            .map(|(pos, block)| (pos, block.cell()))
            .collect();
        let initial = previous.iter().map(|(&pos, &cell)| (pos, cell)).collect();
        let initial_owners = owners(flyer);
        let initial_arms = arms(flyer);
        Self {
            phase_x: flyer.phase_x,
            phase_z: flyer.phase_z,
            push_limit: flyer.push_limit,
            initial,
            initial_owners,
            initial_arms,
            steps: Vec::new(),
            previous,
        }
    }

    pub(crate) fn capture(&mut self, flyer: &Flyer, info: StepInfo) {
        let current: BTreeMap<Coord, u16> = flyer
            .blocks()
            .into_iter()
            .map(|(pos, block)| (pos, block.cell()))
            .collect();
        let mut changes = Vec::new();
        for (&pos, &cell) in &current {
            if self.previous.get(&pos) != Some(&cell) {
                changes.push(CellChange {
                    pos,
                    cell: Some(cell),
                });
            }
        }
        for &pos in self.previous.keys() {
            if !current.contains_key(&pos) {
                changes.push(CellChange { pos, cell: None });
            }
        }
        changes.sort_by_key(|change| change.pos);
        self.previous = current;
        self.steps.push(DebugStep {
            info,
            changes,
            owners: owners(flyer),
            arms: arms(flyer),
        });
    }

    pub fn to_json(&self) -> String {
        let mut out = String::new();
        write!(
            out,
            "{{\"phase_x\":{},\"phase_z\":{},\"push_limit\":{},\"initial\":[",
            self.phase_x, self.phase_z, self.push_limit
        )
        .unwrap();
        for (index, &(pos, cell)) in self.initial.iter().enumerate() {
            if index > 0 {
                out.push(',');
            }
            write_cell(&mut out, pos, Some(cell));
        }
        out.push_str("],\"initial_owners\":[");
        write_owners(&mut out, &self.initial_owners);
        out.push_str("],\"initial_arms\":[");
        write_arms(&mut out, &self.initial_arms);
        out.push_str("],\"steps\":[");
        for (index, step) in self.steps.iter().enumerate() {
            if index > 0 {
                out.push(',');
            }
            out.push('{');
            write!(
                out,
                "\"title\":{},\"stage\":{},\"action\":{},\"tick\":{},",
                json_string(&step.info.title),
                json_string(step.info.stage),
                step.info
                    .action
                    .map(json_string)
                    .unwrap_or_else(|| "null".to_string()),
                step.info.tick
            )
            .unwrap();
            out.push_str("\"changes\":[");
            for (i, change) in step.changes.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_cell(&mut out, change.pos, change.cell);
            }
            out.push_str("],\"owners\":[");
            write_owners(&mut out, &step.owners);
            out.push_str("],\"arms\":[");
            write_arms(&mut out, &step.arms);
            out.push_str("],\"chunk_order\":[");
            for (i, &chunk) in step.info.chunk_order.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_chunk(&mut out, chunk);
            }
            out.push_str("],\"active_chunk\":");
            if let Some(chunk) = step.info.active_chunk {
                write_chunk(&mut out, chunk);
            } else {
                out.push_str("null");
            }
            out.push_str(",\"active_piston\":");
            if let Some(pos) = step.info.active_piston {
                write_coord(&mut out, pos);
            } else {
                out.push_str("null");
            }
            out.push_str(",\"movement\":");
            if let Some(movement) = &step.info.movement {
                out.push_str("{\"sources\":[");
                write_coords(&mut out, &movement.sources);
                out.push_str("],\"destinations\":[");
                write_coords(&mut out, &movement.destinations);
                out.push_str("],\"links\":[");
                write_links(&mut out, &movement.links);
                out.push_str("],\"ignored\":[");
                write_links(&mut out, &movement.ignored);
                out.push_str("],\"failure\":");
                if let Some((pos, reason)) = movement.failure {
                    out.push_str("{\"pos\":");
                    write_coord(&mut out, pos);
                    write!(out, ",\"reason\":{}}}", json_string(reason)).unwrap();
                } else {
                    out.push_str("null");
                }
                out.push('}');
            } else {
                out.push_str("null");
            }
            out.push('}');
        }
        out.push_str("]}");
        out
    }
}

fn arms(flyer: &Flyer) -> Vec<(Coord, u8)> {
    const DIRECTIONS: [(i64, i64, i64); 6] = [
        (1, 0, 0),
        (-1, 0, 0),
        (0, 1, 0),
        (0, -1, 0),
        (0, 0, 1),
        (0, 0, -1),
    ];
    let mut result = Vec::new();
    for (pos, block) in flyer.blocks() {
        if block.kind() != crate::Kind::Piston || !matches!(block.state(), 1 | 2) {
            continue;
        }
        let (dx, dy, dz) = DIRECTIONS[block.direction() as usize];
        let Some(x) = pos.x.checked_add(dx) else {
            continue;
        };
        let Some(y) = pos.y.checked_add(dy) else {
            continue;
        };
        let Some(z) = pos.z.checked_add(dz) else {
            continue;
        };
        let arm = Coord::new(x, y, z);
        if flyer
            .get(arm)
            .is_some_and(|candidate| candidate.kind() == crate::Kind::PistonArm)
        {
            result.push((arm, block.direction()));
        }
    }
    result.sort();
    result
}

fn write_arms(out: &mut String, arms: &[(Coord, u8)]) {
    for (i, &(pos, direction)) in arms.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push('[');
        write_coord(out, pos);
        write!(out, ",{direction}]").unwrap();
    }
}

fn owners(flyer: &Flyer) -> Vec<(Coord, Coord)> {
    let mut result = Vec::new();
    for (owner, block) in flyer.blocks() {
        if block.kind() == crate::Kind::Piston {
            for &member in flyer.piston_blocks(owner) {
                result.push((owner, member));
            }
        }
    }
    result.sort();
    result
}

fn write_owners(out: &mut String, owners: &[(Coord, Coord)]) {
    for (i, &(owner, member)) in owners.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push('[');
        write_coord(out, owner);
        out.push(',');
        write_coord(out, member);
        out.push(']');
    }
}

fn write_cell(out: &mut String, pos: Coord, cell: Option<u16>) {
    out.push('[');
    write!(out, "{},{},{},", pos.x, pos.y, pos.z).unwrap();
    if let Some(cell) = cell {
        write!(out, "{cell}").unwrap();
    } else {
        out.push_str("null");
    }
    out.push(']');
}

fn write_coord(out: &mut String, pos: Coord) {
    write!(out, "[{},{},{}]", pos.x, pos.y, pos.z).unwrap();
}

fn write_chunk(out: &mut String, chunk: Chunk) {
    write!(out, "[{},{}]", chunk.0, chunk.1).unwrap();
}

fn write_coords(out: &mut String, coords: &[Coord]) {
    for (i, &pos) in coords.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        write_coord(out, pos);
    }
}

fn write_links(out: &mut String, links: &[Link]) {
    for (i, link) in links.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        out.push('[');
        write_coord(out, link.from);
        out.push(',');
        write_coord(out, link.to);
        write!(out, ",{}]", json_string(link.kind)).unwrap();
    }
}

fn json_string(value: &str) -> String {
    let mut result = String::from("\"");
    for ch in value.chars() {
        match ch {
            '\"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c < ' ' => write!(result, "\\u{:04x}", c as u32).unwrap(),
            c => result.push(c),
        }
    }
    result.push('"');
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Block, Kind};

    #[test]
    fn arm_direction_is_derived_without_cell_state() {
        let mut flyer = Flyer::with_defaults();
        flyer.set(
            Coord::new(0, 0, 0),
            Block::piston(4, false, false, 1, false).unwrap(),
        );
        flyer.set(
            Coord::new(0, 0, 1),
            Block::plain(Kind::PistonArm, false).unwrap(),
        );
        let trace = TickTrace::new(&flyer);
        assert_eq!(trace.initial_arms, vec![(Coord::new(0, 0, 1), 4)]);
        assert_eq!(flyer.get(Coord::new(0, 0, 1)).unwrap().direction(), 0);
        assert!(trace.to_json().contains("\"initial_arms\":[[[0,0,1],4]]"));
    }
}
