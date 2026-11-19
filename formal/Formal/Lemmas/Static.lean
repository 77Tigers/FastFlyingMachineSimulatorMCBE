/-
Counting inside one well-formed state:
* the listed cells are at most `pushLimit` per piston in state 1 or 3;
* listed cells and pistons in states 1, 2, 3 are distinct blocks of the body.
-/
import Formal.Lemmas.Tick

namespace FF

open Std

/-- The cells holding a nonmoving piston in state `k`. -/
def St.stateCells (s : St) (k : Fin 4) : Finset Pos :=
  s.cellsWith fun _ b => match b with
    | .piston _ _ _ k' false => k' == k
    | _ => false

theorem St.mem_stateCells {s : St} {k : Fin 4} {q : Pos} :
    q ∈ s.stateCells k ↔ HasState s q k := by
  unfold St.stateCells HasState
  rw [St.mem_cellsWith]
  constructor
  · rintro ⟨b, hb, hP⟩
    cases b with
    | piston d st an k' mv =>
      cases mv
      · simp at hP; subst hP; exact ⟨d, st, an, hb⟩
      · simp at hP
    | _ => simp at hP
  · rintro ⟨d, st, an, h⟩
    exact ⟨_, h, by simp⟩

/-- Number of nonmoving pistons in state `k`. -/
def St.nState (s : St) (k : Fin 4) : Nat := (s.stateCells k).card

/-- The cells in piston lists. -/
def St.listCells (s : St) : Finset Pos := s.lists.keys.toFinset.biUnion fun p => (s.list p).toFinset

theorem St.list_of_key {s : St} {p : Pos} (h : p ∈ s.lists.keys.toFinset) :
    ∃ L, s.lists[p]? = some L ∧ s.list p = L := by
  rw [List.mem_toFinset, ExtTreeMap.mem_keys] at h
  obtain ⟨L, hL⟩ := Option.isSome_iff_exists.mp (ExtTreeMap.isSome_getElem?_iff_mem.mpr h)
  exact ⟨L, hL, by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hL]⟩

section
variable {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
include hW hL

theorem listTotal_le : s.listTotal ≤ c.pushLimit * (s.nState 1 + s.nState 3) := by
  unfold St.listTotal St.nState
  calc ∑ p ∈ s.lists.keys.toFinset, (s.list p).length
      ≤ ∑ _p ∈ s.lists.keys.toFinset, c.pushLimit := by
        apply Finset.sum_le_sum
        intro p hp
        obtain ⟨L, hL', hl⟩ := St.list_of_key hp
        rw [hl]; exact (hL p L hL').1
    _ = c.pushLimit * s.lists.keys.toFinset.card := by
        rw [Finset.sum_const_nat (fun _ _ => rfl), Nat.mul_comm]
    _ ≤ c.pushLimit * (s.stateCells 1 ∪ s.stateCells 3).card := by
        apply Nat.mul_le_mul_left
        apply Finset.card_le_card
        intro p hp
        obtain ⟨L, hL', -⟩ := St.list_of_key hp
        obtain ⟨d, st, an, k, hk, h13⟩ := hW.list_owner p L hL'
        rw [Finset.mem_union, St.mem_stateCells, St.mem_stateCells]
        rcases h13 with h | h
        · left; exact ⟨d, st, an, by rw [hk]; congr; exact Fin.ext h⟩
        · right; exact ⟨d, st, an, by rw [hk]; congr; exact Fin.ext h⟩
    _ ≤ c.pushLimit * ((s.stateCells 1).card + (s.stateCells 3).card) :=
        Nat.mul_le_mul_left _ (Finset.card_union_le _ _)

theorem listTotal_eq_card : s.listTotal = s.listCells.card := by
  unfold St.listTotal St.listCells
  rw [Finset.card_biUnion]
  · apply Finset.sum_congr rfl
    intro p hp
    obtain ⟨L, hL', hl⟩ := St.list_of_key hp
    rw [hl, List.toFinset_card_of_nodup (hL p L hL').2]
  · intro p hp p' hp' hne
    obtain ⟨L, hL1, hl1⟩ := St.list_of_key hp
    obtain ⟨L', hL2, hl2⟩ := St.list_of_key hp'
    show Disjoint (s.list p).toFinset (s.list p').toFinset
    rw [hl1, hl2, Finset.disjoint_left]
    intro q hq hq'
    exact hne (hW.list_disjoint p p' L L' q hL1 hL2 (List.mem_toFinset.mp hq)
      (List.mem_toFinset.mp hq'))

theorem mem_listCells_moving {q : Pos} (h : q ∈ s.listCells) :
    ∃ b, s.get q = some b ∧ b.moving = true := by
  unfold St.listCells at h
  obtain ⟨p, hp, hq⟩ := Finset.mem_biUnion.mp h
  obtain ⟨L, hL', hl⟩ := St.list_of_key hp
  rw [hl] at hq
  exact hW.list_moving p L q hL' (List.mem_toFinset.mp hq)

/-- Listed cells and pistons in states 1, 2 and 3 are distinct non-arm blocks. -/
theorem listTotal_add_le :
    s.listTotal + s.nState 1 + s.nState 2 + s.nState 3 ≤ s.N := by
  rw [listTotal_eq_card hW hL]
  unfold St.nState St.N
  have hsub : ∀ k : Fin 4, s.stateCells k ⊆ s.body := by
    intro k q hq
    obtain ⟨d, st, an, h⟩ := St.mem_stateCells.mp hq
    exact St.mem_body.mpr ⟨_, h, by simp [Block.kind]⟩
  have hLsub : s.listCells ⊆ s.body := by
    intro q hq
    obtain ⟨b, hb, hm⟩ := mem_listCells_moving hW hL hq
    refine St.mem_body.mpr ⟨b, hb, ?_⟩
    intro hk
    cases b with
    | plain k m =>
      cases k <;> simp [Block.kind] at hk
      simp [Block.moving] at hm; subst hm
      exact hW.arm_still q hb
    | _ => simp [Block.kind] at hk
  have hdisL : ∀ k : Fin 4, Disjoint s.listCells (s.stateCells k) := by
    intro k
    rw [Finset.disjoint_left]
    intro q hq hq'
    obtain ⟨b, hb, hm⟩ := mem_listCells_moving hW hL hq
    obtain ⟨d, st, an, h⟩ := St.mem_stateCells.mp hq'
    rw [hb] at h; cases h; simp [Block.moving] at hm
  have hdisS : ∀ k k' : Fin 4, k ≠ k' → Disjoint (s.stateCells k) (s.stateCells k') := by
    intro k k' hne
    rw [Finset.disjoint_left]
    intro q hq hq'
    obtain ⟨d, st, an, h⟩ := St.mem_stateCells.mp hq
    obtain ⟨d', st', an', h'⟩ := St.mem_stateCells.mp hq'
    rw [h] at h'; cases h'; exact hne rfl
  have e1 := Finset.card_union_of_disjoint (hdisL 1)
  have e2 := Finset.card_union_of_disjoint
    (s := s.listCells ∪ s.stateCells 1) (t := s.stateCells 2)
    (Finset.disjoint_union_left.mpr ⟨hdisL 2, hdisS 1 2 (by decide)⟩)
  have e3 := Finset.card_union_of_disjoint
    (s := s.listCells ∪ s.stateCells 1 ∪ s.stateCells 2) (t := s.stateCells 3)
    (Finset.disjoint_union_left.mpr ⟨Finset.disjoint_union_left.mpr
      ⟨hdisL 3, hdisS 1 3 (by decide)⟩, hdisS 2 3 (by decide)⟩)
  have hle : (s.listCells ∪ s.stateCells 1 ∪ s.stateCells 2 ∪ s.stateCells 3).card ≤
      s.body.card :=
    Finset.card_le_card (Finset.union_subset (Finset.union_subset
      (Finset.union_subset hLsub (hsub 1)) (hsub 2)) (hsub 3))
  omega

end

/-! ### From one tick to the next -/

theorem TickResult.n1_le {c : Config} {s s' : St} (h : TickResult c s s') :
    s.nState 1 ≤ s'.nState 2 := by
  apply Finset.card_le_card
  intro q hq
  exact St.mem_stateCells.mpr (h.one_two q (St.mem_stateCells.mp hq))

theorem TickResult.n3_le {c : Config} {s s' : St} (h : TickResult c s s') :
    s'.nState 3 ≤ s.nState 2 := by
  apply Finset.card_le_card
  intro q hq
  exact St.mem_stateCells.mpr (h.three_two q (St.mem_stateCells.mp hq))

end FF
