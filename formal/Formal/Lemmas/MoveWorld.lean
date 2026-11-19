/-
Cell-by-cell facts about `moveWorld` for a discovered move: immovable cells stay, a
destination holds the moved block (marked moving), and every other cell is either
unchanged or emptied.
-/
import Formal.Lemmas.Actions

namespace FF

/-! ### Blocks -/

@[simp] theorem Block.startMoving_moving (b : Block) : b.startMoving.moving = true := by
  cases b <;> simp [Block.startMoving, Block.withMoving, Block.moving]

@[simp] theorem Block.startMoving_kind (b : Block) : b.startMoving.kind = b.kind := by
  cases b with
  | plain k m => cases k <;> rfl
  | _ => rfl

/-- A movable piston is retracted; `startMoving` keeps a piston's facing and state. -/
theorem Block.startMoving_piston {b : Block} {o : Option Pos} {p : Pos} {d : Dir}
    {st an mv : Bool} {k : Fin 4} (hm : immovable o p b = false)
    (h : b.startMoving = .piston d st an k mv) : k.val = 0 ∧ mv = true ∧
      ∃ an' mv', b = .piston d st an' k mv' := by
  cases b with
  | piston d' st' an' k' mv' =>
    simp only [Block.startMoving, Block.withMoving, Block.piston.injEq] at h
    obtain ⟨rfl, rfl, rfl, rfl, rfl⟩ := h
    simp [immovable, Block.isPiston, Block.kind, Block.state] at hm
    exact ⟨by omega, rfl, an', mv', rfl⟩
  | plain k m => cases k <;> simp [Block.startMoving, Block.withMoving] at h
  | observer => simp [Block.startMoving] at h
  | rod => simp [Block.startMoving, Block.withMoving] at h

theorem Block.startMoving_not_arm {b : Block} {o : Option Pos} {p : Pos} {m : Bool}
    (hm : immovable o p b = false) : b.startMoving ≠ .plain .arm m := by
  intro h
  cases b with
  | plain k m' =>
    cases k <;> simp [Block.startMoving, Block.withMoving] at h
    simp [immovable, Block.kind] at hm
  | observer => simp [Block.startMoving] at h
  | rod => simp [Block.startMoving, Block.withMoving] at h
  | piston => simp [Block.startMoving, Block.withMoving] at h

/-! ### `moveWorld` on a discovered set -/

/-- What the cell lemmas need from a moved set: its cells are occupied and movable, and it
contains the occupied destination of each of its cells. -/
def MoveOK (s : St) (S : List Pos) (dir : Dir) (o : Option Pos) : Prop :=
  (∀ p ∈ S, ∃ b, s.get p = some b ∧ immovable o p b = false) ∧
  (∀ p ∈ S, (s.get (p.add dir)).isSome → p.add dir ∈ S)

theorem discover_moveOK {c : Config} {s : St} {first : Pos} {dir : Dir} {o : Option Pos}
    {pl : Bool} {S : List Pos} (hS : discover c s first dir o pl = some S) : MoveOK s S dir o :=
  ⟨fun _ hp => discover_mem hS hp, fun _ hp hd => discover_dest_mem hS hp hd⟩

theorem moveOK_nil {s : St} {dir : Dir} {o : Option Pos} : MoveOK s [] dir o :=
  ⟨fun _ h => by simp at h, fun _ h => by simp at h⟩

section
variable {s : St} {dir : Dir} {o : Option Pos} {S : List Pos} (hS : MoveOK s S dir o)
include hS

theorem mw_not_mem_of_immovable {q : Pos} {b : Block} (hq : s.get q = some b)
    (hi : immovable o q b = true) : q ∉ S := by
  intro hm
  obtain ⟨b', hb', hm'⟩ := hS.1 q hm
  rw [hq] at hb'; cases hb'
  rw [hi] at hm'; cases hm'

theorem mw_src_not_mem_of_immovable {q : Pos} {b : Block} (hq : s.get q = some b)
    (hi : immovable o q b = true) : q.add dir.opp ∉ S := by
  intro hm
  have := hS.2 _ hm (by rw [Pos.add_opp_add, hq]; rfl)
  rw [Pos.add_opp_add] at this
  exact mw_not_mem_of_immovable hS hq hi this

/-- Immovable cells keep their block. -/
theorem mw_immovable {q : Pos} {b : Block} (hq : s.get q = some b)
    (hi : immovable o q b = true) : moveWorld s S dir q = some b := by
  unfold moveWorld
  rw [if_neg (mw_src_not_mem_of_immovable hS hq hi), if_neg (mw_not_mem_of_immovable hS hq hi),
    hq]

omit hS in
/-- A destination holds the moved block. -/
theorem mw_dest {r : Pos} (hr : r ∈ S) :
    moveWorld s S dir (r.add dir) = (s.get r).map Block.startMoving := by
  unfold moveWorld
  rw [Pos.add_add_opp, if_pos hr]

/-- Every occupied cell after the move: unchanged and not involved, or a moved block. -/
theorem mw_cases {q : Pos} {b' : Block} (h : moveWorld s S dir q = some b') :
    (s.get q = some b' ∧ q ∉ S ∧ q.add dir.opp ∉ S) ∨
      (∃ b, q.add dir.opp ∈ S ∧ s.get (q.add dir.opp) = some b ∧
        immovable o (q.add dir.opp) b = false ∧ b' = b.startMoving) := by
  unfold moveWorld at h
  split at h
  · rename_i hm
    obtain ⟨b, hb, hi⟩ := hS.1 _ hm
    rw [hb] at h; cases h
    exact Or.inr ⟨b, hm, hb, hi, rfl⟩
  · rename_i hm
    split at h
    · cases h
    · rename_i hq
      exact Or.inl ⟨h, hq, hm⟩

end

end FF
