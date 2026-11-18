/-
Replay check: run `FF.tick` on a trace exported by the Rust simulator
(`tools/src/bin/lean-replay-export.rs`) and compare the state after every tick.
The oracle is read from the trace: the tick's chunk order, and at each chunk's
turn the pistons that acted, in order, followed by the idle ones.
This file is test infrastructure only; nothing in the semantics depends on it.
-/
import Formal.Sim

namespace FF.Replay

open Std

structure TickRec where
  order : List Chunk
  turns : List (Chunk × List Pos)
  blocks : List (Pos × Nat)
  lists : List (Pos × List Pos)
  /-- whether the trace recorded the state after this tick -/
  checked : Bool

structure Trace where
  config : Config
  blocks : List (Pos × Nat)
  lists : List (Pos × List Pos)
  ticks : Array TickRec

def ints (ws : List String) : Except String (List Int) :=
  ws.mapM fun w => match w.toInt? with
    | some i => .ok i
    | none => .error s!"not an integer: {w}"

partial def triples : List Int → List Pos
  | x :: y :: z :: rest => ⟨x, y, z⟩ :: triples rest
  | _ => []

partial def pairs : List Int → List Chunk
  | a :: b :: rest => ⟨a, b⟩ :: pairs rest
  | _ => []

/-- Parse the exporter's text format. -/
def parse (text : String) : Except String Trace := do
  let lines := (text.splitOn "\n").filter (· ≠ "")
  let mut config : Config := ⟨0, 0, 0⟩
  let mut blocks : Array (Pos × Nat) := #[]
  let mut lists : Array (Pos × List Pos) := #[]
  let mut ticks : Array TickRec := #[]
  let mut inTick := false
  let mut cur : TickRec := ⟨[], [], [], [], false⟩
  for line in lines do
    let ws := (line.splitOn " ").filter (· ≠ "")
    match ws with
    | "P" :: rest =>
      let v ← ints rest
      match v with
      | [px, pz, pl] => config := ⟨px, pz, pl.toNat⟩
      | _ => throw s!"bad header: {line}"
    | "B" :: rest =>
      let v ← ints rest
      match v with
      | [x, y, z, cell] =>
        if inTick then cur := { cur with blocks := (⟨x, y, z⟩, cell.toNat) :: cur.blocks }
        else blocks := blocks.push (⟨x, y, z⟩, cell.toNat)
      | _ => throw s!"bad block: {line}"
    | "L" :: rest =>
      let v ← ints rest
      match v with
      | x :: y :: z :: _n :: ms =>
        let e := ((⟨x, y, z⟩ : Pos), triples ms)
        if inTick then cur := { cur with lists := e :: cur.lists }
        else lists := lists.push e
      | _ => throw s!"bad list: {line}"
    | "T" :: _ =>
      inTick := true
      cur := ⟨[], [], [], [], false⟩
    | "O" :: rest =>
      let v ← ints rest
      cur := { cur with order := pairs (v.drop 1) }
    | "K" :: rest =>
      let v ← ints rest
      match v with
      | [a, b] => cur := { cur with turns := (⟨a, b⟩, []) :: cur.turns }
      | _ => throw s!"bad chunk: {line}"
    | "A" :: rest =>
      let v ← ints rest
      match v, cur.turns with
      | [x, y, z], (ch, ps) :: more => cur := { cur with turns := (ch, ⟨x, y, z⟩ :: ps) :: more }
      | _, _ => throw s!"bad action: {line}"
    | ["S"] => cur := { cur with checked := true }
    | ["E"] =>
      ticks := ticks.push { cur with
        turns := cur.turns.reverse.map fun (ch, ps) => (ch, ps.reverse) }
      inTick := false
    | _ => throw s!"unknown line: {line}"
  return ⟨config, blocks.toList, lists.toList, ticks⟩

def posLe (a b : Pos) : Bool := compare a b != .gt

def stateOf (blocks : List (Pos × Nat)) (lists : List (Pos × List Pos)) :
    Except String St := do
  let mut world : ExtTreeMap Pos Block := ∅
  for (p, cell) in blocks do
    match Block.ofCell? cell with
    | some b => world := world.insert p b
    | none => throw s!"invalid cell {cell}"
  let mut ls : ExtTreeMap Pos (List Pos) := ∅
  for (p, l) in lists do
    ls := ls.insert p (l.mergeSort posLe)
  return ⟨world, ls⟩

/-- A permutation of `l` that follows `hint` as far as possible: the hinted elements
first (in hint order), then the rest of `l` in its order. -/
def follow [DecidableEq α] (hint l : List α) : { l' : List α // l'.Perm l } :=
  let h := hint.filter (l.contains ·) ++ l.filter (!hint.contains ·)
  if p : h.Perm l then ⟨h, p⟩ else ⟨l, List.Perm.refl l⟩

def oracleOf (r : TickRec) : TickOracle where
  chunks _ l := follow r.order l
  pistons _ ch l := follow ((r.turns.find? (·.1 == ch)).map (·.2) |>.getD []) l

def showPos (p : Pos) : String := s!"({p.x}, {p.y}, {p.z})"

/-- Compare a Lean state with the Rust state; `none` if equal. -/
def diff (s : St) (blocks : List (Pos × Nat)) (lists : List (Pos × List Pos)) : Option String :=
  let mine := s.world.toList.map fun (p, b) => (p, b.toCell)
  let theirs := blocks.mergeSort fun a b => posLe a.1 b.1
  let myLists := s.lists.toList
  let theirLists := (lists.map fun (p, l) => (p, l.mergeSort posLe)).mergeSort
    fun a b => posLe a.1 b.1
  if mine != theirs then
    let a := mine.filter (!theirs.contains ·)
    let b := theirs.filter (!mine.contains ·)
    some s!"blocks differ; Lean only: {a.take 6 |>.map fun (p, c) => (showPos p, c)}; Rust only: {b.take 6 |>.map fun (p, c) => (showPos p, c)}"
  else if myLists != theirLists then
    some s!"piston lists differ"
  else none

/-- Replay a trace; returns the number of ticks that matched, and the first mismatch. -/
def replay (t : Trace) : Except String (Nat × Option String) := do
  let mut s ← stateOf t.blocks t.lists
  let mut n := 0
  for r in t.ticks do
    match tick t.config (oracleOf r) s with
    | .error e => return (n, some s!"tick {n}: Lean error {repr e}")
    | .ok s' =>
      if r.checked then
        if let some msg := diff s' r.blocks r.lists then
          return (n, some s!"tick {n}: {msg}")
      s := s'; n := n + 1
  return (n, none)

end FF.Replay
