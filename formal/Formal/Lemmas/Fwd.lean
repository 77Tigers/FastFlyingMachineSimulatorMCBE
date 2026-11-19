/-
Forward moves: only the push of a `+X` piston and the pull of a `-X` piston raise the X sum.
Static bound on the forward cells, and the state flow of the pistons facing one direction.
-/
import Formal.Lemmas.RestTick

namespace FF

open Std

/-- The cells holding a nonmoving piston facing `d` in state `k`. -/
def St.sdCells (s : St) (k : Fin 4) (d : Dir) : Finset Pos :=
  s.cellsWith fun _ b => match b with
    | .piston d' _ _ k' false => k' == k && d' == d
    | _ => false

theorem St.mem_sdCells {s : St} {k : Fin 4} {d : Dir} {q : Pos} :
    q ∈ s.sdCells k d ↔ ∃ st an, s.get q = some (.piston d st an k false) := by
  unfold St.sdCells
  rw [St.mem_cellsWith]
  constructor
  · rintro ⟨b, hb, hP⟩
    cases b with
    | piston d' st an k' mv =>
      cases mv
      · simp at hP; obtain ⟨rfl, rfl⟩ := hP; exact ⟨st, an, hb⟩
      · simp at hP
    | _ => simp at hP
  · rintro ⟨st, an, h⟩
    exact ⟨_, h, by simp⟩

/-- Number of nonmoving pistons facing `d` in state `k`. -/
def St.nSD (s : St) (k : Fin 4) (d : Dir) : Nat := (s.sdCells k d).card

theorem sdCells_sub (s : St) (k : Fin 4) (d : Dir) : s.sdCells k d ⊆ s.stateCells k := by
  intro q hq
  obtain ⟨st, an, h⟩ := St.mem_sdCells.mp hq
  exact St.mem_stateCells.mpr ⟨d, st, an, h⟩

/-- The pistons in state `k` facing `+X` and those facing `-X` are among those in state `k`. -/
theorem nSD_px_nx_le (s : St) (k : Fin 4) : s.nSD k .px + s.nSD k .nx ≤ s.nState k := by
  classical
  have hd : Disjoint (s.sdCells k .px) (s.sdCells k .nx) := by
    rw [Finset.disjoint_left]; intro q h1 h2
    obtain ⟨_, _, e1⟩ := St.mem_sdCells.mp h1
    obtain ⟨_, _, e2⟩ := St.mem_sdCells.mp h2
    rw [e1] at e2; cases e2
  have := Finset.card_le_card (Finset.union_subset (sdCells_sub s k .px) (sdCells_sub s k .nx))
  rw [Finset.card_union_of_disjoint hd] at this
  exact this

section
variable {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
include hW hL

/-- The forward cells are at most `pushLimit` per `+X` piston in state 1 and per `-X` piston
in state 3. -/
theorem fwdTotal_le : s.fwdTotal ≤ c.pushLimit * (s.nSD 1 .px + s.nSD 3 .nx) := by
  classical
  set A := s.sdCells 1 .px ∪ s.sdCells 3 .nx with hA
  set Kk := s.lists.keys.toFinset with hKk
  have hf : ∀ p ∈ Kk, s.fwdLen p ≤ if p ∈ A then (c.pushLimit : Int) else 0 := by
    intro p hp
    obtain ⟨L, hL', hl⟩ := St.list_of_key hp
    obtain ⟨d, st, an, k, hk, h13⟩ := hW.list_owner p L hL'
    have hlen : ((s.list p).length : Int) ≤ c.pushLimit := by
      rw [hl]; exact_mod_cast (hL p L hL').1
    have hlen0 : (0 : Int) ≤ (s.list p).length := by omega
    unfold St.fwdLen
    rw [hk]
    rcases h13 with h1 | h3
    · have hk1 : k = 1 := Fin.ext h1
      subst hk1
      cases d with
      | px =>
        have : p ∈ A := Finset.mem_union_left _ (St.mem_sdCells.mpr ⟨st, an, hk⟩)
        rw [if_pos this]; simp [fwB, Dir.fw]; exact_mod_cast hlen
      | _ => simp [fwB, Dir.fw]; split <;> omega
    · have hk3 : k = 3 := Fin.ext h3
      subst hk3
      cases d with
      | nx =>
        have : p ∈ A := Finset.mem_union_right _ (St.mem_sdCells.mpr ⟨st, an, hk⟩)
        rw [if_pos this]; simp [fwB, Dir.fw, Dir.opp]; exact_mod_cast hlen
      | _ => simp [fwB, Dir.fw, Dir.opp]; split <;> omega
  unfold St.fwdTotal
  calc ∑ p ∈ Kk, s.fwdLen p ≤ ∑ p ∈ Kk, (if p ∈ A then (c.pushLimit : Int) else 0) :=
        Finset.sum_le_sum hf
    _ = ((Kk.filter (· ∈ A)).card : Int) * c.pushLimit := by
        rw [← Finset.sum_filter]; simp
    _ ≤ (A.card : Int) * c.pushLimit := by
        have : (Kk.filter (· ∈ A)).card ≤ A.card := by
          apply Finset.card_le_card
          intro q hq; exact (Finset.mem_filter.mp hq).2
        have h0 : (0 : Int) ≤ c.pushLimit := by omega
        have : ((Kk.filter (· ∈ A)).card : Int) ≤ A.card := by exact_mod_cast this
        exact Int.mul_le_mul_of_nonneg_right this h0
    _ ≤ ((c.pushLimit * (s.nSD 1 .px + s.nSD 3 .nx) : Nat) : Int) := by
        have := Finset.card_union_le (s.sdCells 1 .px) (s.sdCells 3 .nx)
        have h2 : (A.card : Int) ≤ s.nSD 1 .px + s.nSD 3 .nx := by
          unfold St.nSD; exact_mod_cast this
        push_cast
        have h0 : (0 : Int) ≤ c.pushLimit := by omega
        have := Int.mul_le_mul_of_nonneg_right h2 h0
        rw [Int.mul_comm (c.pushLimit : Int)]
        exact this

end

/-- Pistons facing `d` in states 2, 3 after a tick were in states 1, 2 before. -/
theorem TickResult2.hiD {s s' : St} (h : TickResult2 s s') (d : Dir) :
    s'.nSD 2 d + s'.nSD 3 d ≤ s.nSD 1 d + s.nSD 2 d := by
  classical
  have hsub : s'.sdCells 2 d ∪ s'.sdCells 3 d ⊆ s.sdCells 1 d ∪ s.sdCells 2 d := by
    intro q hq
    have hq' : q ∈ s'.stateCells 2 ∪ s'.stateCells 3 := by
      rcases Finset.mem_union.mp hq with h1 | h1
      · exact Finset.mem_union_left _ (sdCells_sub _ _ _ h1)
      · exact Finset.mem_union_right _ (sdCells_sub _ _ _ h1)
    have hk : ∃ (st an : Bool) (k : Fin 4), s'.get q = some (.piston d st an k false) ∧
        (k.val = 2 ∨ k.val = 3) := by
      rcases Finset.mem_union.mp hq with h1 | h1
      · obtain ⟨st, an, e⟩ := St.mem_sdCells.mp h1; exact ⟨st, an, 2, e, Or.inl rfl⟩
      · obtain ⟨st, an, e⟩ := St.mem_sdCells.mp h1; exact ⟨st, an, 3, e, Or.inr rfl⟩
    obtain ⟨st, an, k, e, hk⟩ := hk
    obtain ⟨st', an', k', e'⟩ := h.dirHi q d st an k e hk
    rcases Finset.mem_union.mp (h.hiSub hq') with h1 | h1
    · obtain ⟨d1, st1, an1, e1⟩ := St.mem_stateCells.mp h1
      rw [e'] at e1; cases e1
      exact Finset.mem_union_left _ (St.mem_sdCells.mpr ⟨_, _, e'⟩)
    · obtain ⟨d1, st1, an1, e1⟩ := St.mem_stateCells.mp h1
      rw [e'] at e1; cases e1
      exact Finset.mem_union_right _ (St.mem_sdCells.mpr ⟨_, _, e'⟩)
  have hd : Disjoint (s'.sdCells 2 d) (s'.sdCells 3 d) := by
    rw [Finset.disjoint_left]; intro q h1 h2
    obtain ⟨_, _, e1⟩ := St.mem_sdCells.mp h1
    obtain ⟨_, _, e2⟩ := St.mem_sdCells.mp h2
    rw [e1] at e2; cases e2
  have := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint hd] at this
  have := Finset.card_union_le (s.sdCells 1 d) (s.sdCells 2 d)
  unfold St.nSD; omega

theorem nSD_le_nState (s : St) (k : Fin 4) (d : Dir) : s.nSD k d ≤ s.nState k :=
  Finset.card_le_card (sdCells_sub s k d)

end FF
