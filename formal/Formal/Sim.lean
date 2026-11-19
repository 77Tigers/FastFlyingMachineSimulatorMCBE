/-
The tick semantics of `src/sim.rs` (`Flyer::tick`), without the prescribed-move
test harness, the tick report counters and the disk layout.

Randomness: Rust shuffles the chunk order and, at each chunk's turn, that
chunk's pistons with a SplitMix64 RNG. Here both orders come from an *oracle*
(`TickOracle`), which may be any function returning a permutation of the list it
is given. Theorems quantify over all oracles, so they hold for every update
order, which includes every order the Rust RNG can produce.

Faithfulness notes (each checked against the Rust source):
* Rust keeps a per-chunk index of piston positions. Every write that can change
  the kind of a cell during a tick goes through `remove_indexed` /
  `place_indexed`, which update that index, so the index always equals "the
  positions holding a piston". We therefore compute the candidates of a chunk
  directly from the world when its turn starts.
* Rust's discovery is a breadth-first search that stops early. It returns the
  same answer as the closure computed here: the least set containing the first
  block that is closed under (a) occupied destinations and (b) adhesion of
  slime/honey to movable, adhering neighbours; the move fails iff that set
  contains an immovable block or has more than `pushLimit` blocks.
* Errors: Rust returns `Err` from a tick only through `set_piston_blocks`
  (owner not a piston, list longer than the push limit, duplicate members).
  These are kept as `Except` errors. On states loaded from valid files they do
  not occur.
-/
import Formal.Basic

namespace FF

open Std

/-- Fixed per-flyer parameters. Rust stores them in the `Flyer`; they never change. -/
structure Config where
  /-- X/Z chunk phases, `0..15`: a local position `p` lies in world chunk
  `⌊(p.x + phaseX) / 16⌋, ⌊(p.z + phaseZ) / 16⌋`. -/
  phaseX : Int
  phaseZ : Int
  pushLimit : Nat
  deriving Repr

/-- The simulator state: blocks, and each piston's list of blocks whose move it
has not finished yet (Rust `piston_blocks`; only nonempty lists are stored). -/
structure St where
  world : ExtTreeMap Pos Block
  lists : ExtTreeMap Pos (List Pos)

inductive Err
  | listOwnerNotPiston (owner : Pos)
  | listTooLong (owner : Pos)
  | listDuplicate (owner : Pos)
  deriving Repr, DecidableEq

def Config.chunkOf (c : Config) (p : Pos) : Chunk :=
  ⟨(p.x + c.phaseX) / 16, (p.z + c.phaseZ) / 16⟩

namespace St

def get (s : St) (p : Pos) : Option Block := s.world[p]?

/-- Rust `Flyer::set`: a non-piston block also drops any list stored at `p`. -/
def set (s : St) (p : Pos) (b : Block) : St :=
  { world := s.world.insert p b, lists := if b.isPiston then s.lists else s.lists.erase p }

/-- Rust `Flyer::remove`. -/
def remove (s : St) (p : Pos) : St :=
  { world := s.world.erase p, lists := s.lists.erase p }

def list (s : St) (p : Pos) : List Pos := s.lists.getD p []

/-- Rust `Flyer::set_piston_blocks`. -/
def setList (c : Config) (s : St) (owner : Pos) (l : List Pos) : Except Err St :=
  match s.get owner with
  | some b =>
    if !b.isPiston then .error (.listOwnerNotPiston owner)
    else if l.length > c.pushLimit then .error (.listTooLong owner)
    else
      let l := l.mergeSort (fun a b => compare a b != .gt)
      if !l.Nodup then .error (.listDuplicate owner)
      else if l.isEmpty then .ok { s with lists := s.lists.erase owner }
      else .ok { s with lists := s.lists.insert owner l }
  | none => .error (.listOwnerNotPiston owner)

end St

/-- Tick-local context: the state and the cached piston power (Rust `TickContext`;
its piston index is not needed, see the module note). -/
structure Ctx where
  st : St
  powered : ExtTreeSet Pos

namespace Ctx

/-- Rust `remove_indexed`: also clears the cached power at `p`. -/
def removeIndexed (cx : Ctx) (p : Pos) : Ctx :=
  { st := cx.st.remove p, powered := cx.powered.erase p }

/-- Rust `place_indexed`: also clears the cached power at `p`. -/
def placeIndexed (cx : Ctx) (p : Pos) (b : Block) : Ctx :=
  { st := cx.st.set p b, powered := cx.powered.erase p }

end Ctx

/-! ## Power stage -/

/-- Slime, honey, smooth stone and glazed terracotta that are not moving. -/
def isSolid (b : Block) : Bool :=
  !b.moving && (b.kind == .slime || b.kind == .honey || b.kind == .stone || b.kind == .glazed)

/-- `t` is hard-powered: a solid block with a nonmoving rod or powered observer
behind it facing it. -/
def hardPowered (s : St) (t : Pos) : Bool :=
  match s.get t with
  | some tb =>
    isSolid tb && Dir.all.any fun d =>
      match s.get (t.add d.opp) with
      | some (.rod e false) => e == d
      | some (.observer e true false) => e == d
      | _ => false
  | none => false

/-- Rust `power_stage`'s test for one piston, evaluated on the stage's starting state. -/
def pistonPowered (s : St) (p : Pos) : Bool :=
  match s.get p with
  | some (.piston d _ _ _ false) =>
    Dir.all.any fun e =>
      e != d &&
        (hardPowered s (p.add e) ||
          match s.get (p.add e) with
          | some nb =>
            !nb.moving &&
              (nb.kind == .rod || nb.kind == .redstone ||
                (nb.kind == .observer && nb.powered && (p.add e).add nb.dir == p))
          | none => false)
  | _ => false

/-- The power stage: the set of powered pistons, then every observer pulse is consumed. -/
def powerStage (s : St) : St × ExtTreeSet Pos :=
  let pw : ExtTreeSet Pos :=
    s.world.foldl (fun acc p _ => if pistonPowered s p then acc.insert p else acc) ∅
  let isPulse (p : Pos) : Bool :=
    match s.get p with
    | some (.observer _ true _) => true
    | _ => false
  let world := s.world.map fun _ b =>
    match b with
    | .observer d true m => .observer d false m
    | b => b
  -- Rust turns observers off with `Flyer::set`, which drops a list stored at that cell.
  let lists := s.lists.filter fun p _ => !isPulse p
  ({ world, lists }, pw)

/-- All nonmoving, unpowered pistons lose `angry`. -/
def clearAngry (s : St) (pw : ExtTreeSet Pos) : St :=
  { s with
    world := s.world.map fun p b =>
      match b with
      | .piston d st _ state false => if pw.contains p then b else .piston d st false state false
      | b => b }

/-! ## Discovering the blocks a piston moves -/

/-- Rust `immovable`: the initiating piston, moving blocks, arms, and pistons in states 1-3. -/
def immovable (owner : Option Pos) (p : Pos) (b : Block) : Bool :=
  owner == some p || b.moving || b.kind == .arm || (b.isPiston && b.state != 0)

/-- Slime and honey do not stick to each other; neither sticks to glazed terracotta. -/
def adheres (sticky neighbor : Kind) : Bool :=
  neighbor != .glazed &&
    !((sticky == .slime && neighbor == .honey) || (sticky == .honey && neighbor == .slime))

/-- Slime or honey. -/
def isGlue (b : Block) : Bool := b.kind == .slime || b.kind == .honey

/-- Adhesion of glue block `b` at `p` to its neighbour in direction `e`. -/
def adhStep (s : St) (owner : Option Pos) (p : Pos) (b : Block) (acc : ExtTreeSet Pos) (e : Dir) :
    ExtTreeSet Pos :=
  match s.get (p.add e) with
  | some nb =>
    if !immovable owner (p.add e) nb && adheres b.kind nb.kind then acc.insert (p.add e) else acc
  | none => acc

/-- For a slime or honey block at `p`: add its movable, adhering neighbours. -/
def adhesion (s : St) (owner : Option Pos) (acc : ExtTreeSet Pos) (p : Pos) : ExtTreeSet Pos :=
  match s.get p with
  | some b => if isGlue b then Dir.all.foldl (adhStep s owner p b) acc else acc
  | none => acc

/-- What one block `p` of the moved set adds: its adhering neighbours and its occupied
destination. -/
def expandStep (s : St) (dir : Dir) (owner : Option Pos) (acc : ExtTreeSet Pos) (p : Pos) :
    ExtTreeSet Pos :=
  let acc := adhesion s owner acc p
  if (s.get (p.add dir)).isSome then acc.insert (p.add dir) else acc

/-- One closure step: add what every block of `S` adds. -/
def expand (s : St) (dir : Dir) (owner : Option Pos) (S : ExtTreeSet Pos) : ExtTreeSet Pos :=
  S.foldl (expandStep s dir owner) S

/-- Iterate `expand` to its fixed point; `none` once the set exceeds the push limit. -/
def closure (c : Config) (s : St) (dir : Dir) (owner : Option Pos) :
    Nat → ExtTreeSet Pos → Option (ExtTreeSet Pos)
  | 0, _ => none
  | n + 1, S =>
    if S.size > c.pushLimit then none
    else
      let S' := expand s dir owner S
      if S'.toList.all S.contains then some S else closure c s dir owner n S'

/-- Rust `discover_move`: the sorted list of blocks that move, or `none` if the move fails.
An empty first cell moves nothing and succeeds. -/
def discover (c : Config) (s : St) (first : Pos) (dir : Dir) (owner : Option Pos)
    (pulling : Bool) : Option (List Pos) :=
  match s.get first with
  | none => some []
  | some fb =>
    if pulling && fb.kind == .glazed then none
    else
      match closure c s dir owner (s.world.size + 1) {first} with
      | none => none
      | some S =>
        let l := S.toList
        let bad := l.any fun p =>
          match s.get p with
          | some b => immovable owner p b
          | none => true
        if bad || l.length > c.pushLimit then none else some l

/-! ## Piston actions -/

/-- A block as it is placed by a move: observers lose a pending pulse, all become moving. -/
def Block.startMoving : Block → Block
  | .observer d _ _ => .observer d false true
  | b => b.withMoving true

/-- Rust `move_blocks`: remove every source, place every block one step along `dir`
(moving), and carry moved pistons' lists along. Returns the destinations. -/
def moveBlocks (c : Config) (cx : Ctx) (sources : List Pos) (dir : Dir) :
    Except Err (Ctx × List Pos) := do
  let entries := sources.filterMap fun p => (cx.st.get p).map fun b => (p, b, cx.st.list p)
  let cx := entries.foldl (fun cx e => cx.removeIndexed e.1) cx
  let cx := entries.foldl (fun cx e => cx.placeIndexed (e.1.add dir) e.2.1.startMoving) cx
  let cx ← entries.foldlM (init := cx) fun cx e =>
    let (p, b, l) := e
    if b.isPiston && !l.isEmpty then do
      let tl := l.map fun m => if sources.contains m then m.add dir else m
      let st ← cx.st.setList c (p.add dir) tl
      pure { cx with st }
    else pure cx
  pure (cx, entries.map fun e => e.1.add dir)

/-- Rust `start_extension`; `none` when the move fails (nothing changed). -/
def startExtension (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (sticky : Bool) :
    Except Err (Option Ctx) := do
  let front := pos.add d
  match discover c cx.st front d (some pos) false with
  | none => pure none
  | some sources =>
    let (cx, dests) ← moveBlocks c cx sources d
    let cx := cx.placeIndexed front (.plain .arm false)
    let st := cx.st.set pos (.piston d sticky false 1 false)
    let st ← st.setList c pos dests
    pure (some { cx with st })

/-- Rust `start_retraction`: remove whatever is in front; a sticky piston then pulls
starting two cells ahead (a failed pull still retracts). -/
def startRetraction (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (sticky angry : Bool) :
    Except Err Ctx := do
  let cx := cx.removeIndexed (pos.add d)
  let (cx, dests) ←
    if sticky then
      match discover c cx.st ((pos.add d).add d) d.opp (some pos) true with
      | some sources => moveBlocks c cx sources d.opp
      | none => pure (cx, [])
    else pure (cx, [])
  let st := cx.st.set pos (.piston d sticky angry 3 false)
  let st ← st.setList c pos dests
  pure { cx with st }

/-- Rust `finish_moved_block`: the block stops moving; an observer emits a pulse. -/
def finishMovedBlock (s : St) (p : Pos) : St :=
  match s.get p with
  | some (.observer d _ _) => s.set p (.observer d true false)
  | some b => s.set p (b.withMoving false)
  | none => s

/-- Rust `finish_movement`: finish the listed blocks, clear the list, enter `next`. -/
def finishMovement (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (sticky angry : Bool)
    (next : Fin 4) : Except Err Ctx := do
  let st := (cx.st.list pos).foldl finishMovedBlock cx.st
  let st ← st.setList c pos []
  let st := st.set pos (.piston d sticky angry next false)
  pure { cx with st }

/-- One piston's turn (the body of Rust's per-piston loop). -/
def pistonTurn (c : Config) (cx : Ctx) (pos : Pos) : Except Err Ctx :=
  match cx.st.get pos with
  | some (.piston d sticky angry state false) =>
    match state.val with
    | 0 =>
      if cx.powered.contains pos || angry then do
        match ← startExtension c cx pos d sticky with
        | some cx' => pure cx'
        | none => pure { cx with st := cx.st.set pos (.piston d sticky true 0 false) }
      else pure cx
    | 1 => finishMovement c cx pos d sticky angry 2
    | 2 => if cx.powered.contains pos then pure cx else startRetraction c cx pos d sticky angry
    | _ => finishMovement c cx pos d sticky angry 0
  | _ => pure cx

/-! ## Ticks, oracles and runs -/

/-- The distinct world chunks that contain a block, sorted. -/
def occupiedChunks (c : Config) (s : St) : List Chunk :=
  (s.world.foldl (fun acc p _ => acc.insert (c.chunkOf p)) (∅ : ExtTreeSet Chunk)).toList

/-- The pistons a chunk's turn visits, read when the turn starts: nonmoving pistons in it. -/
def candidates (c : Config) (s : St) (ch : Chunk) : List Pos :=
  s.world.toList.filterMap fun (p, b) =>
    if b.isPiston && !b.moving && c.chunkOf p == ch then some p else none

/-- The choices Rust makes with its RNG during one tick. Any permutation is allowed, and
the choice may depend on the current state. -/
structure TickOracle where
  chunks : St → (l : List Chunk) → { l' : List Chunk // l'.Perm l }
  pistons : St → Chunk → (l : List Pos) → { l' : List Pos // l'.Perm l }

/-- Rust `Flyer::tick`: power stage, angry clearing, then every occupied chunk's turn in
the oracle's order, each visiting its pistons in the oracle's order. -/
def tick (c : Config) (o : TickOracle) (s : St) : Except Err St := do
  let (s, pw) := powerStage s
  let s := clearAngry s pw
  let order := (o.chunks s (occupiedChunks c s)).val
  let cx ← order.foldlM (init := (⟨s, pw⟩ : Ctx)) fun cx ch =>
    let ps := (o.pistons cx.st ch (candidates c cx.st ch)).val
    ps.foldlM (pistonTurn c) cx
  pure cx.st

/-- An oracle for a whole run: one per tick. -/
abbrev Oracle := Nat → TickOracle

/-- The state after `n` ticks. -/
def run (c : Config) (o : Oracle) (s : St) : Nat → Except Err St
  | 0 => .ok s
  | n + 1 => do tick c (o n) (← run c o s n)

end FF
