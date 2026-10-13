//! Tick stages and piston movement. The disk format stays independent of the
//! per-tick power cache and chunk schedule.

use std::collections::{BTreeMap, BTreeSet, HashSet, VecDeque};

use crate::debug::{Link, MoveOverlay, StepInfo, TickTrace};
use crate::{Block, Coord, Error, Flyer, Kind};

type Chunk = (i64, i64);

const DIRECTIONS: [(i64, i64, i64); 6] = [
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
];

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct TickReport {
    pub powered_pistons: usize,
    pub chunks_ticked: usize,
    pub extension_attempts: usize,
    pub extensions_started: usize,
    pub extension_failures: usize,
    pub extensions_finished: usize,
    pub retractions_started: usize,
    pub retractions_finished: usize,
    pub blocks_moved: usize,
}

/// One idealized +X input stroke. `input` is the occupied first block, not an
/// actuator coordinate; the simulator discovers the complete moved set.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct PrescribedMove {
    pub input: Coord,
    pub max_load: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum PrescribedOrder {
    BeforeNatural,
    AfterNatural,
    /// Synthetic stress schedule that inserts prescribed inputs into shuffled
    /// natural piston visits. This does not model a physical driver cadence.
    Interleaved,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum PrescribedFailure {
    MissingInput,
    MovingInput,
    Blocked,
    LoadExceeded { discovered: usize, limit: u64 },
    OverlapsActiveOwner,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum PrescribedOutcome {
    Moved { blocks: usize },
    Failed(PrescribedFailure),
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PrescribedActionResult {
    pub id: u64,
    pub input: Coord,
    pub outcome: PrescribedOutcome,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PrescribedTickReport {
    pub natural: TickReport,
    pub order: PrescribedOrder,
    /// Derived local scheduling seed for replaying interleaved event placement.
    /// Legacy before/after schedules leave this absent.
    pub schedule_seed: Option<u64>,
    pub settled: Vec<u64>,
    pub actions: Vec<PrescribedActionResult>,
}

#[derive(Clone, Debug)]
struct PendingPrescribedMove {
    id: u64,
    input: Coord,
    destinations: Vec<Coord>,
}

/// Opt-in wrapper for prescribed input motion. Pending ownership is transient
/// and never added to the ordinary Flyer or its disk representation.
pub struct PrescribedSession {
    flyer: Flyer,
    pending: Vec<PendingPrescribedMove>,
    next_id: u64,
}

impl PrescribedSession {
    pub fn new(flyer: Flyer) -> Self {
        Self {
            flyer,
            pending: Vec::new(),
            next_id: 0,
        }
    }

    /// Expose the underlying flyer only when no external settlement is pending.
    pub fn settled_flyer(&self) -> Option<&Flyer> {
        self.pending.is_empty().then_some(&self.flyer)
    }

    /// Create a trace snapshot without exposing the underlying flyer.
    pub fn new_trace(&self) -> TickTrace {
        TickTrace::new(&self.flyer)
    }

    pub fn has_pending_moves(&self) -> bool {
        !self.pending.is_empty()
    }

    pub fn pending_moves(&self) -> Vec<(u64, Coord, Vec<Coord>)> {
        self.pending
            .iter()
            .map(|move_| (move_.id, move_.input, move_.destinations.clone()))
            .collect()
    }

    pub fn into_flyer(self) -> Result<Flyer, Self> {
        if self.pending.is_empty() {
            Ok(self.flyer)
        } else {
            Err(self)
        }
    }

    pub fn tick(
        &mut self,
        moves: &[PrescribedMove],
        order: PrescribedOrder,
    ) -> Result<PrescribedTickReport, Error> {
        self.tick_inner(moves, order, None, 0)
    }

    pub fn tick_traced(
        &mut self,
        moves: &[PrescribedMove],
        order: PrescribedOrder,
        trace: &mut TickTrace,
        tick: usize,
    ) -> Result<PrescribedTickReport, Error> {
        self.tick_inner(moves, order, Some(trace), tick)
    }

    fn tick_inner(
        &mut self,
        moves: &[PrescribedMove],
        order: PrescribedOrder,
        trace: Option<&mut TickTrace>,
        tick: usize,
    ) -> Result<PrescribedTickReport, Error> {
        let mut actions = Vec::new();
        let mut settled = Vec::new();
        let mut prescribed = PrescribedTick {
            moves,
            order,
            pending: &mut self.pending,
            next_id: &mut self.next_id,
            actions: &mut actions,
            settled: &mut settled,
            schedule_seed: None,
        };
        let natural = self.flyer.tick_inner(trace, tick, Some(&mut prescribed))?;
        Ok(PrescribedTickReport {
            natural,
            order,
            schedule_seed: prescribed.schedule_seed,
            settled,
            actions,
        })
    }
}

struct PrescribedTick<'a> {
    moves: &'a [PrescribedMove],
    order: PrescribedOrder,
    pending: &'a mut Vec<PendingPrescribedMove>,
    next_id: &'a mut u64,
    actions: &'a mut Vec<PrescribedActionResult>,
    settled: &'a mut Vec<u64>,
    schedule_seed: Option<u64>,
}

fn order_name(order: PrescribedOrder) -> &'static str {
    match order {
        PrescribedOrder::BeforeNatural => "before_natural",
        PrescribedOrder::AfterNatural => "after_natural",
        PrescribedOrder::Interleaved => "interleaved",
    }
}

struct TickContext {
    powered: HashSet<Coord>,
    pistons_by_chunk: BTreeMap<Chunk, BTreeSet<Coord>>,
}

impl TickContext {
    fn add_piston(&mut self, flyer: &Flyer, pos: Coord) {
        self.pistons_by_chunk
            .entry(flyer.world_chunk(pos))
            .or_default()
            .insert(pos);
    }

    fn remove_piston(&mut self, flyer: &Flyer, pos: Coord) {
        let chunk = flyer.world_chunk(pos);
        if let Some(positions) = self.pistons_by_chunk.get_mut(&chunk) {
            positions.remove(&pos);
            if positions.is_empty() {
                self.pistons_by_chunk.remove(&chunk);
            }
        }
        self.powered.remove(&pos);
    }
}

/// Local SplitMix64 used for shuffling. Only one draw from Flyer's stored RNG
/// is consumed per tick; derived shuffles cannot depend on earlier outcomes.
struct ShuffleRng(u64);

impl ShuffleRng {
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
    shuffle_with_rng(items, &mut rng);
}

fn shuffle_with_rng<T>(items: &mut [T], rng: &mut ShuffleRng) {
    for end in (1..items.len()).rev() {
        let index = (rng.next() % (end as u64 + 1)) as usize;
        items.swap(end, index);
    }
}

fn offset(pos: Coord, direction: (i64, i64, i64)) -> Option<Coord> {
    Some(Coord::new(
        pos.x.checked_add(direction.0)?,
        pos.y.checked_add(direction.1)?,
        pos.z.checked_add(direction.2)?,
    ))
}

fn opposite(direction: (i64, i64, i64)) -> (i64, i64, i64) {
    (-direction.0, -direction.1, -direction.2)
}

fn is_solid(block: Block) -> bool {
    !block.moving()
        && matches!(
            block.kind(),
            Kind::Slime | Kind::Honey | Kind::SmoothStone | Kind::GlazedTerracotta
        )
}

fn immovable(pos: Coord, block: Block, owner: Option<Coord>) -> bool {
    owner == Some(pos)
        || block.moving()
        || block.kind() == Kind::PistonArm
        || (block.kind() == Kind::Piston && block.state() != 0)
}

fn adheres(sticky: Kind, neighbor: Kind) -> bool {
    if neighbor == Kind::GlazedTerracotta {
        return false;
    }
    !matches!(
        (sticky, neighbor),
        (Kind::Slime, Kind::Honey) | (Kind::Honey, Kind::Slime)
    )
}

impl Flyer {
    /// Relative world chunk, accounting for the flyer's X/Z position modulo 16.
    /// Disk subchunks are aligned to local coordinates and need not match this.
    pub fn world_chunk(&self, pos: Coord) -> Chunk {
        let x = (pos.x as i128 + self.phase_x as i128).div_euclid(16);
        let z = (pos.z as i128 + self.phase_z as i128).div_euclid(16);
        (x as i64, z as i64)
    }

    /// Execute one power stage followed by one shuffled piston stage.
    pub fn tick(&mut self) -> Result<TickReport, Error> {
        self.tick_inner(None, 0, None)
    }

    /// Execute one tick while recording inspectable, in-memory viewer steps.
    pub fn tick_traced(&mut self, trace: &mut TickTrace, tick: usize) -> Result<TickReport, Error> {
        self.tick_inner(Some(trace), tick, None)
    }

    fn tick_inner(
        &mut self,
        mut trace: Option<&mut TickTrace>,
        tick: usize,
        mut prescribed: Option<&mut PrescribedTick<'_>>,
    ) -> Result<TickReport, Error> {
        let powered = self.power_stage();
        let mut report = TickReport {
            powered_pistons: powered.len(),
            ..TickReport::default()
        };

        // Moving pistons retain angry, including when they have no power.
        for (pos, block) in self.blocks() {
            if block.kind() == Kind::Piston && !block.moving() && !powered.contains(&pos) {
                self.set(
                    pos,
                    Block::piston(
                        block.direction(),
                        block.sticky(),
                        false,
                        block.state(),
                        false,
                    )?,
                );
            }
        }

        // External moves complete after this snapshot, so observer pulses are
        // available to the next tick's power stage.
        if let Some(state) = prescribed.as_deref_mut() {
            for movement in state.pending.iter() {
                for &destination in &movement.destinations {
                    if !self.get(destination).is_some_and(|block| block.moving()) {
                        return Err(Error::Format(format!(
                            "prescribed move {} lost moving destination at ({}, {}, {})",
                            movement.id, destination.x, destination.y, destination.z
                        )));
                    }
                }
            }
            let due = std::mem::take(state.pending);
            for movement in due {
                for &destination in &movement.destinations {
                    self.finish_moved_block(destination);
                }
                state.settled.push(movement.id);
                if let Some(view) = trace.as_deref_mut() {
                    view.capture(
                        self,
                        StepInfo {
                            title: format!("Tick {tick} | settle prescribed move {}", movement.id),
                            stage: "prescribed",
                            action: Some("settle prescribed move"),
                            tick,
                            active_input: Some(movement.input),
                            prescribed_move_id: Some(movement.id),
                            prescribed_order: Some(order_name(state.order)),
                            movement: Some(MoveOverlay {
                                sources: movement.destinations,
                                ..MoveOverlay::default()
                            }),
                            ..StepInfo::default()
                        },
                    );
                }
            }
        }

        let mut occupied_chunks = BTreeSet::new();
        let mut context = TickContext {
            powered,
            pistons_by_chunk: BTreeMap::new(),
        };
        for (pos, block) in self.blocks() {
            occupied_chunks.insert(self.world_chunk(pos));
            if block.kind() == Kind::Piston {
                context.add_piston(self, pos);
            }
        }

        let tick_seed = self.next_random_u64();
        let mut chunks: Vec<Chunk> = occupied_chunks.into_iter().collect();
        let minimum_chunk_x = chunks.iter().map(|chunk| chunk.0).min().unwrap_or(0);
        let minimum_chunk_z = chunks.iter().map(|chunk| chunk.1).min().unwrap_or(0);
        shuffle(&mut chunks, tick_seed);
        let schedule_seed = tick_seed ^ 0xa0761d6478bd642f;
        let mut event_buckets = if prescribed
            .as_deref()
            .is_some_and(|state| state.order == PrescribedOrder::Interleaved)
        {
            let mut buckets = vec![Vec::new(); chunks.len() + 1];
            let mut rng = ShuffleRng(schedule_seed);
            if let Some(state) = prescribed.as_deref() {
                for &intent in state.moves {
                    let bucket = (rng.next() % buckets.len() as u64) as usize;
                    buckets[bucket].push(intent);
                }
            }
            for events in &mut buckets {
                shuffle_with_rng(events, &mut rng);
            }
            Some((buckets, rng))
        } else {
            None
        };
        report.chunks_ticked = chunks.len();
        if prescribed
            .as_deref()
            .is_some_and(|state| state.order == PrescribedOrder::BeforeNatural)
        {
            let state = prescribed.as_deref_mut().unwrap();
            let moves = state.moves.to_vec();
            self.run_prescribed_moves(&moves, &mut context, state, trace.as_deref_mut(), tick)?;
        }
        for (chunk_index, &chunk) in chunks.iter().enumerate() {
            let mut pistons: Vec<Coord> = context
                .pistons_by_chunk
                .get(&chunk)
                .into_iter()
                .flat_map(|positions| positions.iter().copied())
                .filter(|&pos| self.get(pos).is_some_and(|block| !block.moving()))
                .collect();
            // Saving translates all coordinates by a constant whole-chunk
            // offset. Relative chunk positions keep the shuffle unchanged.
            let relative_x = (chunk.0 as i128 - minimum_chunk_x as i128) as u64;
            let relative_z = (chunk.1 as i128 - minimum_chunk_z as i128) as u64;
            let chunk_seed = tick_seed
                ^ relative_x.wrapping_mul(0x517cc1b727220a95)
                ^ relative_z.wrapping_mul(0x6c8e9cf570932bd5);
            shuffle(&mut pistons, chunk_seed);
            if let Some(view) = trace.as_deref_mut() {
                view.capture(
                    self,
                    StepInfo {
                        title: format!("Tick {tick} · chunk ({}, {})", chunk.0, chunk.1),
                        stage: "chunk",
                        tick,
                        chunk_order: chunks.clone(),
                        active_chunk: Some(chunk),
                        ..StepInfo::default()
                    },
                );
            }
            let mut events_by_gap = event_buckets.as_mut().map(|(buckets, rng)| {
                let events = std::mem::take(&mut buckets[chunk_index]);
                let mut gaps = vec![Vec::new(); pistons.len() + 1];
                for event in events {
                    let gap = (rng.next() % gaps.len() as u64) as usize;
                    gaps[gap].push(event);
                }
                gaps
            });
            for piston_index in 0..pistons.len() {
                if let Some(gaps) = events_by_gap.as_mut() {
                    if !gaps[piston_index].is_empty() {
                        let state = prescribed.as_deref_mut().unwrap();
                        self.run_prescribed_moves(
                            &gaps[piston_index],
                            &mut context,
                            state,
                            trace.as_deref_mut(),
                            tick,
                        )?;
                    }
                }
                let pos = pistons[piston_index];
                // An earlier piston in this chunk may have moved this one.
                let Some(block) = self.get(pos) else { continue };
                if block.kind() != Kind::Piston || block.moving() {
                    continue;
                }
                let mut action = "idle";
                let mut movement = None;
                match block.state() {
                    0 if context.powered.contains(&pos) || block.angry() => {
                        action = "extend";
                        if trace.is_some() {
                            movement = Some(self.describe_extension(pos, block));
                        }
                        report.extension_attempts += 1;
                        if self.start_extension(pos, block, &mut context, &mut report)? {
                            report.extensions_started += 1;
                        } else {
                            action = "extend failed";
                            report.extension_failures += 1;
                            self.set(
                                pos,
                                Block::piston(block.direction(), block.sticky(), true, 0, false)?,
                            );
                        }
                    }
                    1 => {
                        action = "finish extension";
                        self.finish_movement(pos, block, 2)?;
                        report.extensions_finished += 1;
                    }
                    2 if !context.powered.contains(&pos) => {
                        action = "retract";
                        if trace.is_some() {
                            movement = Some(self.describe_retraction(pos, block));
                        }
                        self.start_retraction(pos, block, &mut context, &mut report)?;
                        report.retractions_started += 1;
                    }
                    3 => {
                        action = "finish retraction";
                        self.finish_movement(pos, block, 0)?;
                        report.retractions_finished += 1;
                    }
                    _ => {}
                }
                if action != "idle" {
                    if let Some(view) = trace.as_deref_mut() {
                        view.capture(
                            self,
                            StepInfo {
                                title: format!(
                                    "Tick {tick} · {action} @ ({}, {}, {})",
                                    pos.x, pos.y, pos.z
                                ),
                                stage: "piston",
                                action: Some(action),
                                tick,
                                chunk_order: chunks.clone(),
                                active_chunk: Some(chunk),
                                active_piston: Some(pos),
                                movement,
                                ..StepInfo::default()
                            },
                        );
                    }
                }
            }
            if let Some(gaps) = events_by_gap.as_mut() {
                if !gaps[pistons.len()].is_empty() {
                    let state = prescribed.as_deref_mut().unwrap();
                    self.run_prescribed_moves(
                        &gaps[pistons.len()],
                        &mut context,
                        state,
                        trace.as_deref_mut(),
                        tick,
                    )?;
                }
            }
        }
        if prescribed
            .as_deref()
            .is_some_and(|state| state.order == PrescribedOrder::AfterNatural)
        {
            let state = prescribed.as_deref_mut().unwrap();
            let moves = state.moves.to_vec();
            self.run_prescribed_moves(&moves, &mut context, state, trace.as_deref_mut(), tick)?;
        }
        if let Some((buckets, _)) = event_buckets.as_mut() {
            let tail = buckets.last_mut().expect("tail event bucket exists");
            if !tail.is_empty() {
                let state = prescribed.as_deref_mut().unwrap();
                self.run_prescribed_moves(
                    tail,
                    &mut context,
                    state,
                    trace.as_deref_mut(),
                    tick,
                )?;
            }
        }
        if let Some(state) = prescribed.as_deref_mut() {
            if state.order == PrescribedOrder::Interleaved {
                state.schedule_seed = Some(schedule_seed);
            }
        }
        Ok(report)
    }

    fn run_prescribed_moves(
        &mut self,
        moves: &[PrescribedMove],
        context: &mut TickContext,
        state: &mut PrescribedTick<'_>,
        mut trace: Option<&mut TickTrace>,
        tick: usize,
    ) -> Result<(), Error> {
        const EAST: (i64, i64, i64) = (1, 0, 0);
        for &intent in moves {
            let id = *state.next_id;
            *state.next_id = state.next_id.wrapping_add(1);
            let mut overlay = MoveOverlay::default();
            let outcome = match self.get(intent.input) {
                None => {
                    overlay.failure = Some((intent.input, "missing prescribed input"));
                    PrescribedOutcome::Failed(PrescribedFailure::MissingInput)
                }
                Some(block) if block.moving() => {
                    overlay.failure = Some((intent.input, "input is already moving"));
                    PrescribedOutcome::Failed(PrescribedFailure::MovingInput)
                }
                Some(_) => match self.discover_move(intent.input, EAST, None, false) {
                    None => {
                        overlay.failure =
                            Some((intent.input, "blocked or simulator push limit exceeded"));
                        PrescribedOutcome::Failed(PrescribedFailure::Blocked)
                    }
                    Some(sources) => {
                        overlay.sources = sources.clone();
                        overlay.destinations = sources
                            .iter()
                            .filter_map(|&pos| offset(pos, EAST))
                            .collect();
                        if sources
                            .iter()
                            .any(|&source| self.has_active_owner_outside(source, &sources))
                        {
                            overlay.failure = sources
                                .iter()
                                .find(|&&source| self.has_active_owner_outside(source, &sources))
                                .copied()
                                .map(|pos| (pos, "source has an active piston owner"));
                            PrescribedOutcome::Failed(PrescribedFailure::OverlapsActiveOwner)
                        } else {
                            let limit = intent.max_load.min(self.push_limit);
                            if sources.len() as u64 > limit {
                                let failing =
                                    sources.get(limit as usize).copied().unwrap_or(intent.input);
                                overlay.failure = Some((failing, "prescribed load limit exceeded"));
                                PrescribedOutcome::Failed(PrescribedFailure::LoadExceeded {
                                    discovered: sources.len(),
                                    limit,
                                })
                            } else {
                                let destinations = self.move_blocks(&sources, EAST, context)?;
                                state.pending.push(PendingPrescribedMove {
                                    id,
                                    input: intent.input,
                                    destinations,
                                });
                                PrescribedOutcome::Moved {
                                    blocks: sources.len(),
                                }
                            }
                        }
                    }
                },
            };
            state.actions.push(PrescribedActionResult {
                id,
                input: intent.input,
                outcome: outcome.clone(),
            });
            if let Some(view) = trace.as_deref_mut() {
                let success = matches!(outcome, PrescribedOutcome::Moved { .. });
                view.capture(
                    self,
                    StepInfo {
                        title: format!(
                            "Tick {tick} | prescribed move {} @ ({}, {}, {})",
                            id, intent.input.x, intent.input.y, intent.input.z
                        ),
                        stage: "prescribed",
                        action: Some(if success {
                            "prescribed move"
                        } else {
                            "prescribed move failed"
                        }),
                        tick,
                        active_input: Some(intent.input),
                        prescribed_move_id: Some(id),
                        prescribed_order: Some(order_name(state.order)),
                        movement: Some(overlay),
                        ..StepInfo::default()
                    },
                );
            }
        }
        Ok(())
    }

    fn has_active_owner_outside(&self, member: Coord, selected: &[Coord]) -> bool {
        self.blocks().into_iter().any(|(owner, block)| {
            block.kind() == Kind::Piston
                && !selected.contains(&owner)
                && self.piston_blocks(owner).contains(&member)
        })
    }

    fn finish_moved_block(&mut self, pos: Coord) {
        if let Some(block) = self.get(pos) {
            let finished = if block.kind() == Kind::Observer {
                Block::observer(block.direction(), true, false).unwrap()
            } else {
                block.with_moving(false)
            };
            self.set(pos, finished);
        }
    }

    fn describe_extension(&self, pos: Coord, piston: Block) -> MoveOverlay {
        let direction = DIRECTIONS[piston.direction() as usize];
        let Some(first) = offset(pos, direction) else {
            return MoveOverlay {
                failure: Some((pos, "coordinate overflow")),
                ..MoveOverlay::default()
            };
        };
        self.describe_discovery(first, direction, Some(pos), false)
    }

    fn describe_retraction(&self, pos: Coord, piston: Block) -> MoveOverlay {
        let direction = DIRECTIONS[piston.direction() as usize];
        let mut result = MoveOverlay::default();
        if !piston.sticky() {
            return result;
        }
        let Some(first) = offset(pos, direction).and_then(|p| offset(p, direction)) else {
            return result;
        };
        // The arm disappears before pull discovery; it is not an obstruction.
        result = self.describe_discovery(first, opposite(direction), Some(pos), true);
        result
    }

    fn describe_discovery(
        &self,
        first: Coord,
        direction: (i64, i64, i64),
        owner: Option<Coord>,
        pulling: bool,
    ) -> MoveOverlay {
        let mut result = MoveOverlay::default();
        let Some(initial) = self.get(first) else {
            return result;
        };
        if pulling && initial.kind() == Kind::GlazedTerracotta {
            result.failure = Some((first, "glazed terracotta cannot be pulled"));
            return result;
        }
        let mut queue = VecDeque::from([first]);
        let mut selected = BTreeSet::new();
        while let Some(pos) = queue.pop_front() {
            if selected.contains(&pos) {
                continue;
            }
            let Some(block) = self.get(pos) else {
                continue;
            };
            if immovable(pos, block, owner) {
                result.sources = selected.iter().copied().collect();
                result.failure = Some((pos, "immovable obstruction"));
                return result;
            }
            selected.insert(pos);
            if selected.len() as u64 > self.push_limit {
                result.sources = selected.iter().copied().collect();
                result.failure = Some((pos, "push limit exceeded"));
                return result;
            }
            if matches!(block.kind(), Kind::Slime | Kind::Honey) {
                for &side in &DIRECTIONS {
                    let Some(neighbor_pos) = offset(pos, side) else {
                        continue;
                    };
                    let Some(neighbor) = self.get(neighbor_pos) else {
                        continue;
                    };
                    if immovable(neighbor_pos, neighbor, owner) {
                        result.ignored.push(Link {
                            from: pos,
                            to: neighbor_pos,
                            kind: "immovable",
                        });
                    } else if adheres(block.kind(), neighbor.kind()) {
                        result.links.push(Link {
                            from: pos,
                            to: neighbor_pos,
                            kind: "stick",
                        });
                        queue.push_back(neighbor_pos);
                    } else {
                        result.ignored.push(Link {
                            from: pos,
                            to: neighbor_pos,
                            kind: "non-sticking",
                        });
                    }
                }
            }
            let Some(destination) = offset(pos, direction) else {
                result.sources = selected.iter().copied().collect();
                result.failure = Some((pos, "coordinate overflow"));
                return result;
            };
            if self.get(destination).is_some() && !selected.contains(&destination) {
                // The retracting arm is removed before discovery.
                if !(pulling
                    && owner.is_some_and(|owner| {
                        destination == offset(owner, opposite(direction)).unwrap_or(owner)
                    }))
                {
                    result.links.push(Link {
                        from: pos,
                        to: destination,
                        kind: "obstruction",
                    });
                    queue.push_back(destination);
                }
            }
        }
        result.sources = selected.iter().copied().collect();
        result.destinations = result
            .sources
            .iter()
            .filter_map(|&p| offset(p, direction))
            .collect();
        result
    }

    fn power_stage(&mut self) -> HashSet<Coord> {
        let snapshot = self.blocks();
        let mut hard_powered = HashSet::new();
        for &(pos, block) in &snapshot {
            if block.moving() {
                continue;
            }
            if block.kind() == Kind::Rod || (block.kind() == Kind::Observer && block.powered()) {
                let direction = DIRECTIONS[block.direction() as usize];
                if let Some(target) = offset(pos, direction) {
                    if self.get(target).is_some_and(is_solid) {
                        hard_powered.insert(target);
                    }
                }
            }
        }

        let mut powered = HashSet::new();
        for &(pos, block) in &snapshot {
            if block.kind() != Kind::Piston || block.moving() {
                continue;
            }
            let front = block.direction() as usize;
            for (index, &direction) in DIRECTIONS.iter().enumerate() {
                if index == front {
                    continue;
                }
                let Some(neighbor_pos) = offset(pos, direction) else {
                    continue;
                };
                if hard_powered.contains(&neighbor_pos) {
                    powered.insert(pos);
                    break;
                }
                let Some(neighbor) = self.get(neighbor_pos) else {
                    continue;
                };
                if neighbor.moving() {
                    continue;
                }
                if matches!(neighbor.kind(), Kind::Rod | Kind::RedstoneBlock)
                    || (neighbor.kind() == Kind::Observer
                        && neighbor.powered()
                        && offset(neighbor_pos, DIRECTIONS[neighbor.direction() as usize])
                            == Some(pos))
                {
                    powered.insert(pos);
                    break;
                }
            }
        }

        for (pos, block) in snapshot {
            if block.kind() == Kind::Observer && block.powered() {
                self.set(
                    pos,
                    Block::observer(block.direction(), false, block.moving()).unwrap(),
                );
            }
        }
        powered
    }

    /// Fixed-point closure over forward obstructions and six-face slime/honey
    /// adhesion. Immovable neighbors are not adhesive; immovable obstructions
    /// block the attempt. Glazed terracotta may be pushed by an obstruction,
    /// but cannot be directly pulled or added through adhesion.
    fn discover_move(
        &self,
        first: Coord,
        direction: (i64, i64, i64),
        owner: Option<Coord>,
        pulling: bool,
    ) -> Option<Vec<Coord>> {
        let first_block = match self.get(first) {
            Some(block) => block,
            None => return Some(Vec::new()),
        };
        if pulling && first_block.kind() == Kind::GlazedTerracotta {
            return None;
        }
        let mut queue = VecDeque::from([first]);
        let mut selected = BTreeSet::new();
        while let Some(pos) = queue.pop_front() {
            if selected.contains(&pos) {
                continue;
            }
            let block = self.get(pos)?;
            if immovable(pos, block, owner) {
                return None;
            }
            selected.insert(pos);
            if selected.len() as u64 > self.push_limit {
                return None;
            }

            if matches!(block.kind(), Kind::Slime | Kind::Honey) {
                for &neighbor_direction in &DIRECTIONS {
                    let Some(neighbor_pos) = offset(pos, neighbor_direction) else {
                        continue;
                    };
                    let Some(neighbor) = self.get(neighbor_pos) else {
                        continue;
                    };
                    if !immovable(neighbor_pos, neighbor, owner)
                        && adheres(block.kind(), neighbor.kind())
                    {
                        queue.push_back(neighbor_pos);
                    }
                }
            }

            let destination = offset(pos, direction)?;
            if self.get(destination).is_some() && !selected.contains(&destination) {
                queue.push_back(destination);
            }
        }
        Some(selected.into_iter().collect())
    }

    fn remove_indexed(&mut self, pos: Coord, context: &mut TickContext) -> Option<Block> {
        let old = self.remove(pos);
        if old.is_some_and(|block| block.kind() == Kind::Piston) {
            context.remove_piston(self, pos);
        }
        context.powered.remove(&pos);
        old
    }

    fn place_indexed(&mut self, pos: Coord, block: Block, context: &mut TickContext) {
        let old = self.set(pos, block);
        if old.is_some_and(|previous| previous.kind() == Kind::Piston) {
            context.remove_piston(self, pos);
        }
        if block.kind() == Kind::Piston {
            context.add_piston(self, pos);
        }
        context.powered.remove(&pos);
    }

    fn move_blocks(
        &mut self,
        sources: &[Coord],
        direction: (i64, i64, i64),
        context: &mut TickContext,
    ) -> Result<Vec<Coord>, Error> {
        let selected: HashSet<Coord> = sources.iter().copied().collect();
        let mut entries = Vec::with_capacity(sources.len());
        for &source in sources {
            let destination = offset(source, direction).expect("discovery checked destinations");
            let block = self.get(source).expect("discovery selected occupied block");
            let piston_list = self.piston_blocks(source).to_vec();
            entries.push((source, destination, block, piston_list));
        }
        for &(source, _, _, _) in &entries {
            self.remove_indexed(source, context);
        }
        let mut destinations = Vec::with_capacity(entries.len());
        for &(_, destination, block, _) in &entries {
            let moving = if block.kind() == Kind::Observer {
                Block::observer(block.direction(), false, true)?
            } else {
                block.with_moving(true)
            };
            self.place_indexed(destination, moving, context);
            destinations.push(destination);
        }
        for &(_, destination, block, ref list) in &entries {
            if block.kind() == Kind::Piston && !list.is_empty() {
                let translated = list
                    .iter()
                    .map(|&member| {
                        if selected.contains(&member) {
                            offset(member, direction).expect("discovery checked destinations")
                        } else {
                            member
                        }
                    })
                    .collect();
                self.set_piston_blocks(destination, translated)?;
            }
        }
        Ok(destinations)
    }

    fn start_extension(
        &mut self,
        pos: Coord,
        piston: Block,
        context: &mut TickContext,
        report: &mut TickReport,
    ) -> Result<bool, Error> {
        let direction = DIRECTIONS[piston.direction() as usize];
        let Some(front) = offset(pos, direction) else {
            return Ok(false);
        };
        let Some(sources) = self.discover_move(front, direction, Some(pos), false) else {
            return Ok(false);
        };
        let destinations = self.move_blocks(&sources, direction, context)?;
        report.blocks_moved += destinations.len();
        self.place_indexed(front, Block::plain(Kind::PistonArm, false)?, context);
        self.set(
            pos,
            Block::piston(piston.direction(), piston.sticky(), false, 1, false)?,
        );
        self.set_piston_blocks(pos, destinations)?;
        Ok(true)
    }

    fn start_retraction(
        &mut self,
        pos: Coord,
        piston: Block,
        context: &mut TickContext,
        report: &mut TickReport,
    ) -> Result<(), Error> {
        let direction = DIRECTIONS[piston.direction() as usize];
        if let Some(front) = offset(pos, direction) {
            self.remove_indexed(front, context);
        }
        let mut destinations = Vec::new();
        if piston.sticky() {
            if let Some(first) = offset(pos, direction).and_then(|p| offset(p, direction)) {
                if let Some(sources) =
                    self.discover_move(first, opposite(direction), Some(pos), true)
                {
                    destinations = self.move_blocks(&sources, opposite(direction), context)?;
                    report.blocks_moved += destinations.len();
                }
            }
        }
        self.set(
            pos,
            Block::piston(
                piston.direction(),
                piston.sticky(),
                piston.angry(),
                3,
                false,
            )?,
        );
        self.set_piston_blocks(pos, destinations)?;
        Ok(())
    }

    fn finish_movement(&mut self, pos: Coord, piston: Block, next_state: u8) -> Result<(), Error> {
        let destinations = self.piston_blocks(pos).to_vec();
        for destination in destinations {
            self.finish_moved_block(destination);
        }
        self.set_piston_blocks(pos, Vec::new())?;
        self.set(
            pos,
            Block::piston(
                piston.direction(),
                piston.sticky(),
                piston.angry(),
                next_state,
                false,
            )?,
        );
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn piston(direction: u8, sticky: bool, angry: bool, state: u8, moving: bool) -> Block {
        Block::piston(direction, sticky, angry, state, moving).unwrap()
    }

    fn plain(kind: Kind) -> Block {
        Block::plain(kind, false).unwrap()
    }

    fn powered_piston(sticky: bool) -> Flyer {
        let mut flyer = Flyer::with_defaults();
        flyer.set(Coord::new(0, 0, 0), piston(0, sticky, false, 0, false));
        flyer.set(Coord::new(0, -1, 0), Block::rod(0, false).unwrap());
        flyer
    }

    #[test]
    fn extend_finish_retract_finish() {
        let mut flyer = powered_piston(true);
        flyer.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        let first = flyer.tick().unwrap();
        assert_eq!(first.extensions_started, 1);
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 1);
        assert_eq!(
            flyer.get(Coord::new(1, 0, 0)).unwrap().kind(),
            Kind::PistonArm
        );
        assert!(flyer.get(Coord::new(2, 0, 0)).unwrap().moving());
        assert_eq!(
            flyer.piston_blocks(Coord::new(0, 0, 0)),
            &[Coord::new(2, 0, 0)]
        );

        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 2);
        assert!(!flyer.get(Coord::new(2, 0, 0)).unwrap().moving());
        assert!(flyer.piston_blocks(Coord::new(0, 0, 0)).is_empty());

        flyer.remove(Coord::new(0, -1, 0));
        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 3);
        assert!(flyer.get(Coord::new(1, 0, 0)).unwrap().moving());
        assert!(flyer.get(Coord::new(2, 0, 0)).is_none());
        assert_eq!(
            flyer.piston_blocks(Coord::new(0, 0, 0)),
            &[Coord::new(1, 0, 0)]
        );

        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 0);
        assert!(!flyer.get(Coord::new(1, 0, 0)).unwrap().moving());
        assert!(flyer.piston_blocks(Coord::new(0, 0, 0)).is_empty());
    }

    #[test]
    fn sticky_closure_ignores_immovable_and_incompatible_neighbors() {
        let mut flyer = powered_piston(false);
        flyer.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        flyer.set(Coord::new(1, 1, 0), plain(Kind::SmoothStone));
        flyer.set(Coord::new(1, 0, 1), plain(Kind::Honey));
        flyer.set(Coord::new(1, 0, -1), plain(Kind::GlazedTerracotta));
        flyer.set(Coord::new(1, -1, 0), plain(Kind::PistonArm));
        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(2, 0, 0)).unwrap().kind(), Kind::Slime);
        assert_eq!(
            flyer.get(Coord::new(2, 1, 0)).unwrap().kind(),
            Kind::SmoothStone
        );
        assert_eq!(flyer.get(Coord::new(1, 0, 1)).unwrap().kind(), Kind::Honey);
        assert_eq!(
            flyer.get(Coord::new(1, 0, -1)).unwrap().kind(),
            Kind::GlazedTerracotta
        );
        assert_eq!(
            flyer.get(Coord::new(1, -1, 0)).unwrap().kind(),
            Kind::PistonArm
        );
        assert_eq!(flyer.piston_blocks(Coord::new(0, 0, 0)).len(), 2);
    }

    #[test]
    fn collision_with_immovable_fails_but_touching_it_does_not() {
        let mut flyer = powered_piston(false);
        flyer.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        flyer.set(Coord::new(2, 0, 0), plain(Kind::PistonArm));
        let report = flyer.tick().unwrap();
        assert_eq!(report.extension_failures, 1);
        assert_eq!(flyer.get(Coord::new(1, 0, 0)).unwrap().kind(), Kind::Slime);
        let block = flyer.get(Coord::new(0, 0, 0)).unwrap();
        assert_eq!(block.state(), 0);
        assert!(block.angry());
    }

    #[test]
    fn push_limit_counts_the_entire_discovered_set() {
        let mut flyer = Flyer::new(0, 0, 0, 1).unwrap();
        flyer.set(Coord::new(0, 0, 0), piston(0, false, false, 0, false));
        flyer.set(Coord::new(0, -1, 0), Block::rod(0, false).unwrap());
        flyer.set(Coord::new(1, 0, 0), plain(Kind::SmoothStone));
        flyer.set(Coord::new(2, 0, 0), plain(Kind::Glass));
        assert_eq!(flyer.tick().unwrap().extension_failures, 1);
        assert_eq!(
            flyer.get(Coord::new(1, 0, 0)).unwrap().kind(),
            Kind::SmoothStone
        );
        assert_eq!(flyer.get(Coord::new(2, 0, 0)).unwrap().kind(), Kind::Glass);
    }

    #[test]
    fn moving_ordinary_block_does_not_collect_stationary_slime() {
        let mut flyer = powered_piston(false);
        flyer.set(Coord::new(1, 0, 0), plain(Kind::SmoothStone));
        flyer.set(Coord::new(1, 0, 1), plain(Kind::Slime));
        flyer.tick().unwrap();
        assert_eq!(
            flyer.get(Coord::new(2, 0, 0)).unwrap().kind(),
            Kind::SmoothStone
        );
        assert_eq!(flyer.get(Coord::new(1, 0, 1)).unwrap().kind(), Kind::Slime);
        assert_eq!(flyer.piston_blocks(Coord::new(0, 0, 0)).len(), 1);
    }

    #[test]
    fn power_is_directional_and_moving_sources_are_inert() {
        let mut flyer = Flyer::with_defaults();
        flyer.set(Coord::new(0, 0, 0), piston(0, false, false, 0, false));
        flyer.set(Coord::new(1, 0, 0), plain(Kind::RedstoneBlock));
        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 0);

        flyer.set(Coord::new(0, 1, 0), plain(Kind::SmoothStone));
        flyer.set(
            Coord::new(0, 2, 0),
            Block::observer(3, true, false).unwrap(),
        );
        flyer.tick().unwrap();
        assert_eq!(flyer.get(Coord::new(0, 0, 0)).unwrap().state(), 1);
        assert!(!flyer.get(Coord::new(0, 2, 0)).unwrap().powered());

        let mut moving_source = Flyer::with_defaults();
        moving_source.set(Coord::new(0, 0, 0), piston(0, false, false, 0, false));
        moving_source.set(
            Coord::new(0, 1, 0),
            Block::plain(Kind::RedstoneBlock, true).unwrap(),
        );
        moving_source.tick().unwrap();
        assert_eq!(moving_source.get(Coord::new(0, 0, 0)).unwrap().state(), 0);
    }

    #[test]
    fn glazed_can_be_pushed_but_not_pulled() {
        let mut flyer = powered_piston(true);
        flyer.set(Coord::new(1, 0, 0), plain(Kind::GlazedTerracotta));
        flyer.tick().unwrap();
        flyer.tick().unwrap();
        flyer.remove(Coord::new(0, -1, 0));
        flyer.tick().unwrap();
        assert_eq!(
            flyer.get(Coord::new(2, 0, 0)).unwrap().kind(),
            Kind::GlazedTerracotta
        );
        assert!(flyer.get(Coord::new(1, 0, 0)).is_none());
        assert!(flyer.piston_blocks(Coord::new(0, 0, 0)).is_empty());
    }

    #[test]
    fn sticky_pull_can_push_an_obstruction_backward() {
        let mut flyer = Flyer::with_defaults();
        let owner = Coord::new(0, 0, 0);
        flyer.set(owner, piston(0, true, false, 2, false));
        flyer.set(Coord::new(1, 0, 0), plain(Kind::PistonArm));
        flyer.set(Coord::new(2, 0, 0), plain(Kind::Slime));
        flyer.set(Coord::new(2, 0, 1), plain(Kind::SmoothStone));
        flyer.set(Coord::new(1, 0, 1), plain(Kind::GlazedTerracotta));
        flyer.tick().unwrap();
        assert_eq!(flyer.get(owner).unwrap().state(), 3);
        assert_eq!(flyer.get(Coord::new(1, 0, 0)).unwrap().kind(), Kind::Slime);
        assert_eq!(
            flyer.get(Coord::new(1, 0, 1)).unwrap().kind(),
            Kind::SmoothStone
        );
        assert_eq!(
            flyer.get(Coord::new(0, 0, 1)).unwrap().kind(),
            Kind::GlazedTerracotta
        );
        assert_eq!(flyer.piston_blocks(owner).len(), 3);
    }

    #[test]
    fn phase_changes_world_chunk_boundaries() {
        let flyer = Flyer::new(7, 9, 0, 12).unwrap();
        assert_eq!(flyer.world_chunk(Coord::new(8, 0, 6)), (0, 0));
        assert_eq!(flyer.world_chunk(Coord::new(9, 0, 7)), (1, 1));
    }

    #[test]
    fn chunk_list_excludes_newly_occupied_chunks() {
        let mut flyer = Flyer::with_defaults();
        flyer.set(Coord::new(15, 0, 0), piston(0, false, false, 0, false));
        flyer.set(Coord::new(15, -1, 0), Block::rod(0, false).unwrap());
        let report = flyer.tick().unwrap();
        assert_eq!(report.chunks_ticked, 1);
        assert_eq!(
            flyer.get(Coord::new(16, 0, 0)).unwrap().kind(),
            Kind::PistonArm
        );
    }

    #[test]
    fn angry_moved_piston_can_activate_after_movement_finishes() {
        let mut seed = 0;
        loop {
            let mut probe = Flyer::new(0, 0, seed, 12).unwrap();
            let tick_seed = probe.next_random_u64();
            if ShuffleRng(tick_seed).next() % 2 == 1 {
                break;
            }
            seed += 1;
        }
        let mut flyer = Flyer::new(0, 0, seed, 12).unwrap();
        let owner = Coord::new(0, 0, 0);
        let angry = Coord::new(16, 0, 0);
        flyer.set(owner, piston(0, false, false, 1, false));
        flyer.set(angry, piston(0, false, true, 0, true));
        flyer.set_piston_blocks(owner, vec![angry]).unwrap();
        let mut trace = TickTrace::new(&flyer);
        let report = flyer.tick_traced(&mut trace, 1).unwrap();
        assert_eq!(report.extensions_finished, 1);
        assert_eq!(report.extensions_started, 1);
        assert_eq!(flyer.get(angry).unwrap().state(), 1);
        assert!(!flyer.get(angry).unwrap().moving());
        let actions: Vec<_> = trace
            .steps
            .iter()
            .filter(|step| step.info.stage == "piston")
            .map(|step| (step.info.active_piston, step.info.action))
            .collect();
        assert_eq!(
            actions,
            vec![
                (Some(owner), Some("finish extension")),
                (Some(angry), Some("extend"))
            ]
        );
    }

    #[test]
    fn deterministic_from_saved_state() {
        let mut first = powered_piston(false);
        first.set(Coord::new(1, 0, 0), plain(Kind::Honey));
        let mut second = Flyer::from_bytes(&first.to_bytes().unwrap()).unwrap();
        for _ in 0..4 {
            assert_eq!(first.tick().unwrap(), second.tick().unwrap());
            assert_eq!(first.to_bytes().unwrap(), second.to_bytes().unwrap());
        }
    }

    #[test]
    fn observer_powers_immediately_when_movement_finishes() {
        let mut flyer = Flyer::with_defaults();
        let owner = Coord::new(0, 0, 0);
        let observer_pos = Coord::new(2, 0, 0);
        flyer.set(owner, piston(0, false, false, 1, false));
        flyer.set(observer_pos, Block::observer(1, false, true).unwrap());
        flyer.set_piston_blocks(owner, vec![observer_pos]).unwrap();
        flyer.tick().unwrap();
        let observer = flyer.get(observer_pos).unwrap();
        assert!(!observer.moving());
        assert!(observer.powered());
        flyer.tick().unwrap();
        assert!(!flyer.get(observer_pos).unwrap().powered());
    }

    #[test]
    fn tracing_does_not_change_tick_result() {
        let mut normal = powered_piston(true);
        normal.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        let mut traced = Flyer::from_bytes(&normal.to_bytes().unwrap()).unwrap();
        let mut trace = TickTrace::new(&traced);
        for tick in 1..=5 {
            assert_eq!(
                normal.tick().unwrap(),
                traced.tick_traced(&mut trace, tick).unwrap()
            );
            assert_eq!(normal.to_bytes().unwrap(), traced.to_bytes().unwrap());
        }
        assert!(trace.steps.len() >= 5);
        assert!(trace.steps.iter().all(|step| {
            step.info.stage == "chunk"
                || (step.info.stage == "piston"
                    && step.info.action.is_some_and(|action| action != "idle"))
        }));
    }

    #[test]
    fn detailed_trace_skips_idle_pistons() {
        let mut flyer = Flyer::with_defaults();
        flyer.set(Coord::new(0, 0, 0), piston(0, false, false, 0, false));
        flyer.set(Coord::new(1, 0, 3), piston(0, false, true, 0, false));
        flyer.set(Coord::new(3, 0, 0), piston(0, false, false, 2, false));
        flyer.set(Coord::new(3, -1, 0), Block::rod(0, false).unwrap());
        let mut trace = TickTrace::new(&flyer);
        flyer.tick_traced(&mut trace, 1).unwrap();
        assert!(trace.steps.iter().any(|step| step.info.stage == "chunk"));
        assert!(trace.steps.iter().all(|step| step.info.stage == "chunk"));
        assert!(!flyer.get(Coord::new(1, 0, 3)).unwrap().angry());
        let json = trace.to_json();
        assert!(!json.contains("piston_order"));
        assert!(!json.contains("\"stage\":\"piston\""));
    }

    #[test]
    fn saving_coordinate_translation_does_not_change_chunk_shuffle() {
        for seed in 0..32 {
            let mut editor = Flyer::new(7, 11, seed, 12).unwrap();
            editor.set(Coord::new(-17, 0, -3), piston(0, false, false, 0, false));
            editor.set(Coord::new(-15, 0, -3), piston(1, false, false, 0, false));
            editor.set(Coord::new(-16, 0, -3), plain(Kind::SmoothStone));
            editor.set(Coord::new(-17, -1, -3), Block::rod(0, false).unwrap());
            editor.set(Coord::new(-15, -1, -3), Block::rod(0, false).unwrap());
            editor.set(Coord::new(20, 0, -3), plain(Kind::Glass));
            let mut loaded = Flyer::from_bytes(&editor.to_bytes().unwrap()).unwrap();
            editor.tick().unwrap();
            loaded.tick().unwrap();
            assert_eq!(editor.to_bytes().unwrap(), loaded.to_bytes().unwrap());
        }
    }

    #[test]
    fn prescribed_empty_session_matches_default_tick_and_trace() {
        let mut original = powered_piston(true);
        original.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        let initial = original.to_bytes().unwrap();
        let mut regular = Flyer::from_bytes(&initial).unwrap();
        let mut session = PrescribedSession::new(Flyer::from_bytes(&initial).unwrap());
        let mut interleaved = PrescribedSession::new(Flyer::from_bytes(&initial).unwrap());
        let mut regular_trace = TickTrace::new(&regular);
        let mut session_trace = session.new_trace();
        let mut interleaved_trace = interleaved.new_trace();
        for tick in 1..=5 {
            let expected = regular.tick_traced(&mut regular_trace, tick).unwrap();
            let actual = session
                .tick_traced(
                    &[],
                    PrescribedOrder::BeforeNatural,
                    &mut session_trace,
                    tick,
                )
                .unwrap();
            assert_eq!(actual.natural, expected);
            assert!(actual.actions.is_empty());
            assert_eq!(
                regular.to_bytes().unwrap(),
                session.flyer.to_bytes().unwrap()
            );
            let stress = interleaved
                .tick_traced(
                    &[],
                    PrescribedOrder::Interleaved,
                    &mut interleaved_trace,
                    tick,
                )
                .unwrap();
            assert_eq!(stress.natural, expected);
            assert!(stress.schedule_seed.is_some());
            assert!(stress.actions.is_empty());
            assert_eq!(regular.to_bytes().unwrap(), interleaved.flyer.to_bytes().unwrap());
        }
        assert_eq!(regular_trace.to_json(), session_trace.to_json());
        assert_eq!(regular_trace.to_json(), interleaved_trace.to_json());
    }

    #[test]
    fn prescribed_move_uses_closure_and_load_failure_is_atomic() {
        let input = Coord::new(0, 0, 0);
        let mut flyer = Flyer::with_defaults();
        flyer.set(input, plain(Kind::Slime));
        flyer.set(Coord::new(0, 1, 0), plain(Kind::SmoothStone));
        flyer.set(Coord::new(1, 0, 0), plain(Kind::Glass));
        let before = flyer
            .blocks()
            .into_iter()
            .map(|(p, b)| (p, b.cell()))
            .collect::<Vec<_>>();
        let mut session = PrescribedSession::new(flyer);
        let failed = session
            .tick(
                &[PrescribedMove { input, max_load: 2 }],
                PrescribedOrder::Interleaved,
            )
            .unwrap();
        assert_eq!(
            failed.actions[0].outcome,
            PrescribedOutcome::Failed(PrescribedFailure::LoadExceeded {
                discovered: 3,
                limit: 2
            })
        );
        assert!(!session.has_pending_moves());
        assert_eq!(
            session
                .flyer
                .blocks()
                .into_iter()
                .map(|(p, b)| (p, b.cell()))
                .collect::<Vec<_>>(),
            before
        );

        let moved = session
            .tick(
                &[PrescribedMove { input, max_load: 3 }],
                PrescribedOrder::BeforeNatural,
            )
            .unwrap();
        assert_eq!(
            moved.actions[0].outcome,
            PrescribedOutcome::Moved { blocks: 3 }
        );
        assert!(session.flyer.get(Coord::new(1, 0, 0)).unwrap().moving());
        assert_eq!(
            session.flyer.get(Coord::new(2, 0, 0)).unwrap().kind(),
            Kind::Glass
        );
        assert_eq!(
            session.flyer.get(Coord::new(1, 1, 0)).unwrap().kind(),
            Kind::SmoothStone
        );
    }

    #[test]
    fn prescribed_observer_settlement_pulses_after_power_snapshot() {
        let observer = Coord::new(0, 0, 0);
        let mut flyer = Flyer::with_defaults();
        flyer.set(observer, Block::observer(0, false, false).unwrap());
        flyer.set(Coord::new(2, 0, 0), plain(Kind::SmoothStone));
        flyer.set(Coord::new(3, 0, 0), piston(2, false, false, 0, false));
        let mut session = PrescribedSession::new(flyer);
        let start = session
            .tick(
                &[PrescribedMove {
                    input: observer,
                    max_load: 1,
                }],
                PrescribedOrder::Interleaved,
            )
            .unwrap();
        assert!(matches!(
            start.actions[0].outcome,
            PrescribedOutcome::Moved { blocks: 1 }
        ));
        assert_eq!(
            session.flyer.get(Coord::new(1, 0, 0)).unwrap().kind(),
            Kind::Observer
        );
        assert!(session.flyer.get(Coord::new(1, 0, 0)).unwrap().moving());

        let settled = session.tick(&[], PrescribedOrder::BeforeNatural).unwrap();
        assert_eq!(settled.natural.powered_pistons, 0);
        assert_eq!(settled.settled, vec![0]);
        let observer = session.flyer.get(Coord::new(1, 0, 0)).unwrap();
        assert!(observer.powered());
        assert!(!observer.moving());

        let pulsed = session.tick(&[], PrescribedOrder::BeforeNatural).unwrap();
        assert_eq!(pulsed.natural.powered_pistons, 1);
        assert_eq!(pulsed.natural.extensions_started, 1);
    }

    #[test]
    fn prescribed_settle_preserves_angry_piston_through_clear_pass() {
        let input = Coord::new(0, 0, 0);
        let mut flyer = Flyer::with_defaults();
        flyer.set(input, piston(0, false, true, 0, false));
        flyer.set(Coord::new(0, -1, 0), Block::rod(0, false).unwrap());
        let mut session = PrescribedSession::new(flyer);
        let started = session
            .tick(
                &[PrescribedMove { input, max_load: 1 }],
                PrescribedOrder::BeforeNatural,
            )
            .unwrap();
        assert_eq!(
            started.actions[0].outcome,
            PrescribedOutcome::Moved { blocks: 1 }
        );
        assert!(session.flyer.get(Coord::new(1, 0, 0)).unwrap().moving());

        let settled = session.tick(&[], PrescribedOrder::BeforeNatural).unwrap();
        assert_eq!(settled.settled, vec![0]);
        assert_eq!(settled.natural.extensions_started, 1);
        assert_eq!(session.flyer.get(Coord::new(1, 0, 0)).unwrap().state(), 1);
    }

    #[test]
    fn prescribed_move_translates_moved_piston_ownership() {
        let owner = Coord::new(0, 0, 0);
        let member = Coord::new(1, 0, 0);
        let mut flyer = Flyer::with_defaults();
        flyer.set(owner, piston(0, false, false, 0, false));
        flyer.set(member, plain(Kind::SmoothStone));
        flyer.set_piston_blocks(owner, vec![member]).unwrap();
        let mut session = PrescribedSession::new(flyer);
        let report = session
            .tick(
                &[PrescribedMove {
                    input: owner,
                    max_load: 2,
                }],
                PrescribedOrder::BeforeNatural,
            )
            .unwrap();
        assert_eq!(
            report.actions[0].outcome,
            PrescribedOutcome::Moved { blocks: 2 }
        );
        assert_eq!(
            session.flyer.piston_blocks(Coord::new(1, 0, 0)),
            &[Coord::new(2, 0, 0)]
        );
    }

    #[test]
    fn prescribed_moves_reject_active_or_moving_inputs_and_guard_extraction() {
        let input = Coord::new(1, 0, 0);
        let owner = Coord::new(0, 0, 0);
        let mut flyer = Flyer::with_defaults();
        flyer.set(owner, piston(0, false, false, 1, false));
        flyer.set(input, plain(Kind::SmoothStone));
        flyer.set_piston_blocks(owner, vec![input]).unwrap();
        let mut session = PrescribedSession::new(flyer);
        let active = session
            .tick(
                &[PrescribedMove { input, max_load: 1 }],
                PrescribedOrder::BeforeNatural,
            )
            .unwrap();
        assert_eq!(
            active.actions[0].outcome,
            PrescribedOutcome::Failed(PrescribedFailure::OverlapsActiveOwner)
        );

        let mut flyer = Flyer::with_defaults();
        flyer.set(Coord::new(0, 0, 0), plain(Kind::Glass));
        let mut session = PrescribedSession::new(flyer);
        let moving = session
            .tick(
                &[
                    PrescribedMove {
                        input: Coord::new(0, 0, 0),
                        max_load: 1,
                    },
                    PrescribedMove {
                        input: Coord::new(1, 0, 0),
                        max_load: 1,
                    },
                ],
                PrescribedOrder::BeforeNatural,
            )
            .unwrap();
        assert_eq!(
            moving.actions[0].outcome,
            PrescribedOutcome::Moved { blocks: 1 }
        );
        assert_eq!(
            moving.actions[1].outcome,
            PrescribedOutcome::Failed(PrescribedFailure::MovingInput)
        );
        assert!(session.has_pending_moves());
        assert!(session.settled_flyer().is_none());
        session = match session.into_flyer() {
            Ok(_) => panic!("pending extraction unexpectedly succeeded"),
            Err(session) => session,
        };
        let settled = session.tick(&[], PrescribedOrder::BeforeNatural).unwrap();
        assert_eq!(settled.settled, vec![0]);
        assert!(session.into_flyer().is_ok());
    }

    #[test]
    fn prescribed_trace_records_order_and_action_identity() {
        for order in [
            PrescribedOrder::BeforeNatural,
            PrescribedOrder::AfterNatural,
        ] {
            let mut flyer = powered_piston(false);
            flyer.set(Coord::new(10, 0, 0), plain(Kind::Glass));
            let mut session = PrescribedSession::new(flyer);
            let mut trace = session.new_trace();
            session
                .tick_traced(
                    &[PrescribedMove {
                        input: Coord::new(10, 0, 0),
                        max_load: 1,
                    }],
                    order,
                    &mut trace,
                    1,
                )
                .unwrap();
            let prescribed = trace
                .steps
                .iter()
                .position(|step| {
                    step.info.stage == "prescribed" && step.info.action == Some("prescribed move")
                })
                .unwrap();
            let natural = trace
                .steps
                .iter()
                .position(|step| step.info.stage == "piston" && step.info.action == Some("extend"))
                .unwrap();
            match order {
                PrescribedOrder::BeforeNatural => assert!(prescribed < natural),
                PrescribedOrder::AfterNatural => assert!(natural < prescribed),
                PrescribedOrder::Interleaved => unreachable!(),
            }
            let step = &trace.steps[prescribed].info;
            assert_eq!(step.active_input, Some(Coord::new(10, 0, 0)));
            assert_eq!(step.prescribed_move_id, Some(0));
            assert_eq!(
                step.prescribed_order,
                Some(match order {
                    PrescribedOrder::BeforeNatural => "before_natural",
                    PrescribedOrder::AfterNatural => "after_natural",
                    PrescribedOrder::Interleaved => unreachable!(),
                })
            );
        }
    }

    #[test]
    fn interleaved_can_place_an_input_between_natural_visits() {
        let input = Coord::new(10, 0, 0);
        let mut found = false;
        for seed in 0..128 {
            let mut flyer = powered_piston(false);
            flyer.rng_state = seed;
            flyer.set(Coord::new(4, 0, 0), piston(0, false, false, 0, false));
            flyer.set(Coord::new(4, -1, 0), Block::rod(0, false).unwrap());
            flyer.set(input, plain(Kind::Glass));
            let mut session = PrescribedSession::new(flyer);
            let mut trace = session.new_trace();
            let report = session
                .tick_traced(
                    &[PrescribedMove { input, max_load: 1 }],
                    PrescribedOrder::Interleaved,
                    &mut trace,
                    0,
                )
                .unwrap();
            let order = trace
                .steps
                .iter()
                .filter_map(|step| match (step.info.stage, step.info.action) {
                    ("piston", Some(action)) if action == "extend" => Some("natural"),
                    ("prescribed", Some("prescribed move")) => Some("input"),
                    _ => None,
                })
                .collect::<Vec<_>>();
            if order == ["natural", "input", "natural"] {
                assert!(report.schedule_seed.is_some());
                assert_eq!(report.actions.len(), 1);
                assert_eq!(report.actions[0].id, 0);
                found = true;
                break;
            }
        }
        assert!(found, "expected a deterministic intermediate event placement");
    }

    #[test]
    fn interleaved_multi_input_permutations_are_deterministic_and_attempt_once() {
        let inputs = [Coord::new(10, 0, 0), Coord::new(20, 0, 0)];
        let mut observed = BTreeSet::new();
        for seed in 0..128 {
            let mut flyer = Flyer::with_defaults();
            flyer.rng_state = seed;
            for input in inputs {
                flyer.set(input, plain(Kind::Glass));
            }
            let moves = inputs.map(|input| PrescribedMove { input, max_load: 1 });
            let mut first = PrescribedSession::new(Flyer::from_bytes(&flyer.to_bytes().unwrap()).unwrap());
            let mut second = PrescribedSession::new(flyer);
            let mut first_trace = first.new_trace();
            let mut second_trace = second.new_trace();
            let first_report = first
                .tick_traced(&moves, PrescribedOrder::Interleaved, &mut first_trace, 0)
                .unwrap();
            let second_report = second
                .tick_traced(&moves, PrescribedOrder::Interleaved, &mut second_trace, 0)
                .unwrap();
            assert_eq!(first_report, second_report);
            assert_eq!(first_trace.to_json(), second_trace.to_json());
            assert_eq!(first_report.actions.len(), 2);
            assert_eq!(first_report.actions[0].id, 0);
            assert_eq!(first_report.actions[1].id, 1);
            observed.insert(first_report.actions.iter().map(|action| action.input).collect::<Vec<_>>());
            if observed.len() == 2 {
                break;
            }
        }
        assert_eq!(observed.len(), 2, "both execution permutations should be reachable");
    }

    #[test]
    fn interleaved_natural_intermediate_load_failure_is_between_successful_endpoints() {
        fn run(seed: u64, order: PrescribedOrder) -> (PrescribedTickReport, TickTrace) {
            let owner = Coord::new(0, 0, 0);
            let moved = Coord::new(2, 0, 0);
            let second_piston = Coord::new(2, -1, 0);
            let input = Coord::new(3, 0, 0);
            let mut flyer = Flyer::with_defaults();
            flyer.rng_state = seed;
            flyer.set(owner, piston(0, false, false, 1, false));
            flyer.set(Coord::new(1, 0, 0), plain(Kind::PistonArm));
            flyer.set(moved, Block::plain(Kind::SmoothStone, true).unwrap());
            flyer.set(second_piston, piston(2, false, false, 0, false));
            flyer.set(Coord::new(2, -2, 0), Block::rod(0, false).unwrap());
            flyer.set(input, plain(Kind::Slime));
            flyer.set_piston_blocks(owner, vec![moved]).unwrap();
            let mut session = PrescribedSession::new(flyer);
            let mut trace = session.new_trace();
            let report = session
                .tick_traced(
                    &[PrescribedMove { input, max_load: 1 }],
                    order,
                    &mut trace,
                    0,
                )
                .unwrap();
            (report, trace)
        }

        let owner = Coord::new(0, 0, 0);
        let second_piston = Coord::new(2, -1, 0);
        let input = Coord::new(3, 0, 0);
        let mut found = false;
        for seed in 0..128 {
            let (interleaved, trace) = run(seed, PrescribedOrder::Interleaved);
            let order = trace
                .steps
                .iter()
                .filter_map(|step| match (step.info.active_piston, step.info.action) {
                    (Some(pos), Some("finish extension")) if pos == owner => Some("finish-a"),
                    (Some(pos), Some("extend")) if pos == second_piston => Some("extend-b"),
                    (_, Some("prescribed move failed"))
                        if step.info.active_input == Some(input) =>
                    {
                        Some("input-failed")
                    }
                    _ => None,
                })
                .collect::<Vec<_>>();
            if order != ["finish-a", "input-failed", "extend-b"] {
                continue;
            }

            let (before, _) = run(seed, PrescribedOrder::BeforeNatural);
            let (after, _) = run(seed, PrescribedOrder::AfterNatural);
            for endpoint in [&before, &after] {
                assert_eq!(endpoint.natural.extension_failures, 0);
                assert_eq!(endpoint.natural.extensions_finished, 1);
                assert_eq!(endpoint.natural.extensions_started, 1);
                assert_eq!(
                    endpoint.actions[0].outcome,
                    PrescribedOutcome::Moved { blocks: 1 }
                );
            }
            assert_eq!(interleaved.natural.extension_failures, 0);
            assert_eq!(interleaved.natural.extensions_finished, 1);
            assert_eq!(interleaved.natural.extensions_started, 1);
            assert_eq!(
                interleaved.actions[0].outcome,
                PrescribedOutcome::Failed(PrescribedFailure::LoadExceeded {
                    discovered: 2,
                    limit: 1,
                })
            );
            found = true;
            break;
        }
        assert!(
            found,
            "expected a schedule where only the intermediate input exceeds its load cap"
        );
    }

    #[test]
    fn browser_snapshot_origin_keeps_motion_continuous() {
        let mut live = Flyer::new(0, 0, 2, 12).unwrap();
        live.set(Coord::new(0, 0, 0), piston(0, false, false, 0, false));
        live.set(Coord::new(1, 0, 1), piston(1, true, false, 0, false));
        live.set(Coord::new(0, 0, 1), plain(Kind::Slime));
        live.set(Coord::new(1, 0, 0), plain(Kind::Slime));
        live.set(
            Coord::new(0, 1, 1),
            Block::observer(3, true, false).unwrap(),
        );
        live.set(
            Coord::new(1, 1, 0),
            Block::observer(3, false, false).unwrap(),
        );
        let mut cached = Flyer::from_bytes(&live.to_bytes().unwrap()).unwrap();
        let mut origin = (0i128, 0i128, 0i128);
        for _ in 0..100 {
            live.tick().unwrap();
            cached.tick().unwrap();
            let shift = cached.normalization_shift();
            cached = Flyer::from_bytes(&cached.to_bytes().unwrap()).unwrap();
            origin.0 -= shift.0;
            origin.1 -= shift.1;
            origin.2 -= shift.2;
            let mut actual = cached
                .blocks()
                .into_iter()
                .map(|(pos, block)| {
                    (
                        (
                            pos.x as i128 + origin.0,
                            pos.y as i128 + origin.1,
                            pos.z as i128 + origin.2,
                        ),
                        block.cell(),
                    )
                })
                .collect::<Vec<_>>();
            let mut expected = live
                .blocks()
                .into_iter()
                .map(|(pos, block)| ((pos.x as i128, pos.y as i128, pos.z as i128), block.cell()))
                .collect::<Vec<_>>();
            actual.sort();
            expected.sort();
            assert_eq!(actual, expected);
        }
    }
}
