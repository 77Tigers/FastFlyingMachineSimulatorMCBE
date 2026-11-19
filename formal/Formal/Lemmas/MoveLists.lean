/-
`moveBlocks` and `setList` when no moved cell carries a piston list (the situation in
every valid state): they succeed, lists elsewhere are unchanged, power only shrinks.
-/
import Formal.Lemmas.Move

namespace FF

open Std

/-! ### `setList` -/

theorem St.lists_set {s : St} {p q : Pos} {b : Block} :
    (s.set p b).lists[q]? = if p = q ∧ b.isPiston = false then none else s.lists[q]? := by
  unfold St.set
  by_cases hb : b.isPiston = true
  · simp [hb]
  · simp only [hb, Bool.false_eq_true, if_false]
    rw [ExtTreeMap.getElem?_erase]
    by_cases h : p = q <;> simp [h]

theorem St.lists_remove {s : St} {p q : Pos} :
    (s.remove p).lists[q]? = if p = q then none else s.lists[q]? := by
  unfold St.remove
  simp only
  rw [ExtTreeMap.getElem?_erase]
  by_cases h : p = q <;> simp [h]

/-- `setList` on a piston with a short duplicate-free list succeeds; it stores a
permutation of the list at the owner (nothing if empty) and changes nothing else. -/
theorem St.setList_ok {c : Config} {s : St} {p : Pos} {b : Block} {l : List Pos}
    (hp : s.get p = some b) (hb : b.isPiston = true) (hl : l.length ≤ c.pushLimit)
    (hn : l.Nodup) :
    ∃ s', s.setList c p l = .ok s' ∧ s'.world = s.world ∧
      (∀ q, q ≠ p → s'.lists[q]? = s.lists[q]?) ∧
      (l = [] → s'.lists[p]? = none) ∧
      (l ≠ [] → ∃ L, s'.lists[p]? = some L ∧ ∀ q, q ∈ L ↔ q ∈ l) := by
  have hperm := List.mergeSort_perm l (fun a b => compare a b != .gt)
  have hnd : (l.mergeSort fun a b => compare a b != .gt).Nodup := hperm.nodup_iff.mpr hn
  by_cases he : l = []
  · subst he
    refine ⟨{ s with lists := s.lists.erase p }, ?_, rfl, ?_, ?_, ?_⟩
    · simp [St.setList, hp, hb]
    · intro q hq
      simp only
      rw [ExtTreeMap.getElem?_erase]
      simp [Ne.symm hq]
    · intro _; simp
    · intro h; exact absurd rfl h
  · have hne : (l.mergeSort fun a b => compare a b != .gt).isEmpty = false := by
      cases hm : l.mergeSort (fun a b => compare a b != .gt) with
      | nil => exact absurd (List.Perm.eq_nil (hm ▸ hperm).symm) he
      | cons _ _ => rfl
    refine ⟨{ s with lists := s.lists.insert p (l.mergeSort fun a b => compare a b != .gt) },
      ?_, rfl, ?_, ?_, ?_⟩
    · have hgt : ¬ l.length > c.pushLimit := by omega
      simp [St.setList, hp, hb, hgt, hnd, hne]
    · intro q hq
      simp only
      rw [ExtTreeMap.getElem?_insert]
      simp [Ne.symm hq]
    · intro h; exact absurd h he
    · intro _
      refine ⟨_, by simp, fun q => hperm.mem_iff⟩

/-! ### `moveBlocks` without lists on the moved cells -/

theorem foldlM_pure_of {α} (L : List α) (f : Ctx → α → Except Err Ctx) (g : Ctx → α → Ctx)
    (hf : ∀ cx e, e ∈ L → f cx e = .ok (g cx e)) (cx : Ctx) :
    L.foldlM f cx = .ok (L.foldl g cx) := by
  induction L generalizing cx with
  | nil => rfl
  | cons e L ih =>
    simp only [List.foldlM_cons, List.foldl_cons]
    rw [hf cx e (by simp)]
    exact ih (fun cx e he => hf cx e (by simp [he])) _

/-- The context after the remove and place passes of `moveBlocks`. -/
def movedCtx (cx : Ctx) (l : List Pos) (dir : Dir) : Ctx :=
  (moveEntries cx l).foldl (fun cx e => cx.placeIndexed (e.1.add dir) e.2.1.startMoving)
    ((moveEntries cx l).foldl (fun cx e => cx.removeIndexed e.1) cx)

theorem moveEntries_list {cx : Ctx} {l : List Pos} {e : Pos × Block × List Pos}
    (he : e ∈ moveEntries cx l) : e.2.2 = cx.st.list e.1 := by
  unfold moveEntries at he
  obtain ⟨p, -, hp⟩ := List.mem_filterMap.mp he
  cases hg : cx.st.get p with
  | none => rw [hg] at hp; cases hp
  | some b => rw [hg] at hp; cases hp; rfl

variable {c : Config} {cx : Ctx} {l : List Pos} {dir : Dir}

theorem foldl_id' {α β} (L : List α) (x : β) : L.foldl (fun x _ => x) x = x := by
  induction L generalizing x with
  | nil => rfl
  | cons _ _ ih => exact ih x

theorem moveBlocks_eq (hocc : ∀ p ∈ l, (cx.st.get p).isSome)
    (hno : ∀ p ∈ l, cx.st.lists[p]? = none) :
    moveBlocks c cx l dir = .ok (movedCtx cx l dir, l.map (·.add dir)) := by
  unfold moveBlocks
  rw [show (l.filterMap fun p => (cx.st.get p).map fun b => (p, b, cx.st.list p)) =
    moveEntries cx l from rfl]
  simp only [bind, Except.bind, pure, Except.pure]
  have hfst := moveEntries_fst hocc
  rw [foldlM_pure_of _ _ (fun cx _ => cx)]
  · rw [foldl_id']
    have : (moveEntries cx l).map (fun e => e.1.add dir) = l.map (·.add dir) := by
      have := congrArg (List.map (·.add dir)) hfst
      rw [List.map_map] at this
      exact this
    rw [this]; rfl
  · intro cx' e he
    have hl := moveEntries_list he
    have hel : e.1 ∈ l := hfst ▸ List.mem_map_of_mem he
    have : cx.st.list e.1 = [] := by
      unfold St.list; rw [ExtTreeMap.getD_eq_getD_getElem?, hno _ hel]; rfl
    rw [hl, this]
    simp

theorem foldl_removeIndexed_powered {α} (L : List α) (f : α → Pos) (cx : Ctx) (q : Pos)
    (h : (L.foldl (fun cx e => cx.removeIndexed (f e)) cx).powered.contains q = true) :
    cx.powered.contains q = true := by
  induction L generalizing cx with
  | nil => exact h
  | cons e L ih => exact Ctx.removeIndexed_powered_le (ih _ h)

theorem foldl_placeIndexed_powered {α} (L : List α) (f : α → Pos) (g : α → Block) (cx : Ctx)
    (q : Pos)
    (h : (L.foldl (fun cx e => cx.placeIndexed (f e) (g e)) cx).powered.contains q = true) :
    cx.powered.contains q = true := by
  induction L generalizing cx with
  | nil => exact h
  | cons e L ih => exact Ctx.placeIndexed_powered_le (ih _ h)

theorem movedCtx_powered {q : Pos} (h : (movedCtx cx l dir).powered.contains q = true) :
    cx.powered.contains q = true :=
  foldl_removeIndexed_powered _ _ _ _ (foldl_placeIndexed_powered _ _ _ _ _ h)

theorem movedCtx_get (hocc : ∀ p ∈ l, (cx.st.get p).isSome) (hnd : l.Nodup)
    (hno : ∀ p ∈ l, cx.st.lists[p]? = none) (q : Pos) :
    (movedCtx cx l dir).st.get q =
      if q.add dir.opp ∈ l then (cx.st.get (q.add dir.opp)).map Block.startMoving
      else if q ∈ l then none else cx.st.get q :=
  moveBlocks_spec (c := ⟨0, 0, 0⟩) (moveBlocks_eq hocc hno) hocc hnd q

theorem St.lists_foldl_remove (ps : List Pos) (s : St) (q : Pos) :
    (ps.foldl (fun s p => s.remove p) s).lists[q]? = if q ∈ ps then none else s.lists[q]? := by
  induction ps generalizing s with
  | nil => simp
  | cons p ps ih =>
    simp only [List.foldl_cons, ih, St.lists_remove, List.mem_cons]
    by_cases h1 : q ∈ ps
    · simp [h1]
    · by_cases h2 : p = q
      · simp [h1, h2]
      · simp only [h1, h2, or_false, if_false]
        rw [if_neg (fun e => h2 e.symm)]

theorem St.lists_foldl_set (L : List (Pos × Block)) (s : St) (q : Pos)
    (h : ∀ e ∈ L, e.1 = q → s.lists[q]? = none) :
    (L.foldl (fun s e => s.set e.1 e.2) s).lists[q]? = s.lists[q]? := by
  induction L generalizing s with
  | nil => rfl
  | cons e L ih =>
    simp only [List.foldl_cons]
    rw [ih]
    · rw [St.lists_set]
      split
      · rename_i hh; exact (h e (by simp) hh.1).symm
      · rfl
    · intro e' he' hq
      rw [St.lists_set]
      split
      · rfl
      · exact h e' (by simp [he']) hq

/-- With no lists on sources or destinations, the lists are unchanged by the move. -/
theorem movedCtx_lists (hocc : ∀ p ∈ l, (cx.st.get p).isSome)
    (hno : ∀ p ∈ l, cx.st.lists[p]? = none)
    (hdest : ∀ p ∈ l, cx.st.lists[p.add dir]? = none) (q : Pos) :
    (movedCtx cx l dir).st.lists[q]? = cx.st.lists[q]? := by
  unfold movedCtx
  rw [Ctx.foldl_placeIndexed_st, Ctx.foldl_removeIndexed_st]
  have hfst := moveEntries_fst hocc
  rw [St.lists_foldl_set, hfst, St.lists_foldl_remove]
  · split
    · rename_i hq; exact (hno q hq).symm
    · rfl
  · intro e he hq
    obtain ⟨e', he', rfl⟩ := List.mem_map.mp he
    have hel : e'.1 ∈ l := hfst ▸ List.mem_map_of_mem he'
    rw [hfst, St.lists_foldl_remove]
    split
    · rfl
    · simp only at hq; rw [← hq]; exact hdest _ hel

end FF
