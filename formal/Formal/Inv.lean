/-
The bookkeeping invariant of valid states, and the buildable start states.

`Buildable` = a state one can build: nothing moving, no piston lists, every piston
retracted or extended with its own arm in front. `Wf` holds on buildable states and is
kept by every tick (`Formal/Lemmas/InvTick.lean`), so it holds on every state reachable
from a buildable one, under every oracle.
-/
import Formal.Lemmas.MoveLists

namespace FF

open Std

/-- Piston states 1 and 2: the arm is out. -/
def armOut (k : Fin 4) : Prop := k.val = 1 ∨ k.val = 2

instance (k : Fin 4) : Decidable (armOut k) := inferInstanceAs (Decidable (_ ∨ _))

structure Wf (s : St) : Prop where
  /-- Lists belong to nonmoving pistons in state 1 or 3. -/
  list_owner : ∀ (p : Pos) (L : List Pos), s.lists[p]? = some L →
    ∃ d st an k, s.get p = some (.piston d st an k false) ∧ (k.val = 1 ∨ k.val = 3)
  /-- List entries hold moving blocks. -/
  list_moving : ∀ (p : Pos) (L : List Pos) (q : Pos), s.lists[p]? = some L → q ∈ L → ∃ b, s.get q = some b ∧ b.moving = true
  /-- No cell is in two lists. -/
  list_disjoint : ∀ (p p' : Pos) (L L' : List Pos) (q : Pos), s.lists[p]? = some L → s.lists[p']? = some L' → q ∈ L →
    q ∈ L' → p = p'
  /-- Only retracted pistons can be moving. -/
  moving_piston : ∀ (p : Pos) (d : Dir) (st an : Bool) (k : Fin 4), s.get p = some (.piston d st an k true) → k.val = 0
  /-- Arms never move. -/
  arm_still : ∀ p : Pos, s.get p ≠ some (.plain .arm true)
  /-- A piston whose arm is out has an arm in front. -/
  arm_front : ∀ (p : Pos) (d : Dir) (st an : Bool) (k : Fin 4) (mv : Bool), s.get p = some (.piston d st an k mv) → armOut k →
    s.get (p.add d) = some (.plain .arm false)
  /-- Two pistons with their arms out never share the arm cell. -/
  front_unique : ∀ (p p' : Pos) (d d' : Dir) (st st' an an' : Bool) (k k' : Fin 4) (mv mv' : Bool),
    s.get p = some (.piston d st an k mv) → s.get p' = some (.piston d' st' an' k' mv') →
    armOut k → armOut k' → p.add d = p'.add d' → p = p'

structure Buildable (s : St) : Prop where
  no_lists : ∀ p : Pos, s.lists[p]? = none
  not_moving : ∀ (p : Pos) (b : Block), s.get p = some b → b.moving = false
  piston_state : ∀ (p : Pos) (d : Dir) (st an : Bool) (k : Fin 4) (mv : Bool), s.get p = some (.piston d st an k mv) → k.val = 0 ∨ k.val = 2
  arm_front : ∀ (p : Pos) (d : Dir) (st an : Bool) (k : Fin 4) (mv : Bool), s.get p = some (.piston d st an k mv) → k.val = 2 →
    s.get (p.add d) = some (.plain .arm false)
  front_unique : ∀ (p p' : Pos) (d d' : Dir) (st st' an an' : Bool) (k k' : Fin 4) (mv mv' : Bool),
    s.get p = some (.piston d st an k mv) → s.get p' = some (.piston d' st' an' k' mv') →
    k.val = 2 → k'.val = 2 → p.add d = p'.add d' → p = p'

theorem Buildable.wf {s : St} (h : Buildable s) : Wf s where
  list_owner p L hL := by rw [h.no_lists p] at hL; cases hL
  list_moving p L q hL := by rw [h.no_lists p] at hL; cases hL
  list_disjoint p p' L L' q hL := by rw [h.no_lists p] at hL; cases hL
  moving_piston p d st an k hp := by have := h.not_moving _ _ hp; simp [Block.moving] at this
  arm_still p hp := by have := h.not_moving _ _ hp; simp [Block.moving] at this
  arm_front p d st an k mv hp hk := by
    rcases h.piston_state _ _ _ _ _ _ hp with h0 | h2
    · rcases hk with h1 | h1 <;> omega
    · exact h.arm_front _ _ _ _ _ _ hp h2
  front_unique p p' d d' st st' an an' k k' mv mv' hp hp' hk hk' he := by
    have e1 := h.piston_state _ _ _ _ _ _ hp
    have e2 := h.piston_state _ _ _ _ _ _ hp'
    have k2 : k.val = 2 := by rcases hk with h1 | h1 <;> rcases e1 with h3 | h3 <;> omega
    have k2' : k'.val = 2 := by rcases hk' with h1 | h1 <;> rcases e2 with h3 | h3 <;> omega
    exact h.front_unique _ _ _ _ _ _ _ _ _ _ _ _ hp hp' k2 k2' he

/-! ### Consequences -/

section
variable {s : St} (hI : Wf s)
include hI

/-- A cell with a list holds a nonmoving piston in state 1 or 3. -/
theorem Wf.no_list_of {p : Pos}
    (h : ∀ (d : Dir) (st an : Bool) (k : Fin 4), s.get p = some (.piston d st an k false) → k.val = 1 ∨ k.val = 3 → False) :
    s.lists[p]? = none := by
  cases hl : s.lists[p]? with
  | none => rfl
  | some L =>
    obtain ⟨d, st, an, k, hp, hk⟩ := hI.list_owner p L hl
    exact (h d st an k hp hk).elim

theorem Wf.no_list_empty {p : Pos} (h : s.get p = none) : s.lists[p]? = none :=
  hI.no_list_of fun _ _ _ _ hp _ => by rw [h] at hp; cases hp

/-- A movable cell carries no list. -/
theorem Wf.no_list_movable {p : Pos} {b : Block} {o : Option Pos} (hb : s.get p = some b)
    (hm : immovable o p b = false) : s.lists[p]? = none :=
  hI.no_list_of fun d st an k hp hk => by
    rw [hb] at hp; cases hp
    simp [immovable, Block.isPiston, Block.kind, Block.state] at hm
    rcases hk with h | h <;> omega

end

end FF
