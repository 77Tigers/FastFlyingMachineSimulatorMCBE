/-
What `moveBlocks` does to the world: every source block appears, marked moving, one cell
further along the direction; sources not refilled become empty; all else is unchanged.
-/
import Formal.Lemmas.St

namespace FF

open Std

@[simp] theorem Pos.add_add_opp (p : Pos) (d : Dir) : (p.add d).add d.opp = p := by
  cases p; cases d <;> simp only [Pos.add, Dir.opp, Dir.dx, Dir.dy, Dir.dz, Pos.mk.injEq] <;> omega

@[simp] theorem Pos.add_opp_add (p : Pos) (d : Dir) : (p.add d.opp).add d = p := by
  cases p; cases d <;> simp only [Pos.add, Dir.opp, Dir.dx, Dir.dy, Dir.dz, Pos.mk.injEq] <;> omega

theorem Pos.add_inj {p q : Pos} {d : Dir} : p.add d = q.add d ↔ p = q := by
  constructor
  · intro h; simpa using congrArg (fun r => r.add d.opp) h
  · rintro rfl; rfl

theorem Pos.add_eq_iff {p q : Pos} {d : Dir} : p.add d = q ↔ p = q.add d.opp := by
  constructor
  · rintro rfl; simp
  · rintro rfl; simp

/-! ### Folds of `set` / `remove` -/

theorem St.get_foldl_remove (ps : List Pos) (s : St) (q : Pos) :
    (ps.foldl (fun s p => s.remove p) s).get q = if q ∈ ps then none else s.get q := by
  induction ps generalizing s with
  | nil => simp
  | cons p ps ih =>
    simp only [List.foldl_cons, ih, St.get_remove, List.mem_cons]
    by_cases h1 : q ∈ ps
    · simp [h1]
    · by_cases h2 : p = q
      · simp [h1, h2]
      · simp only [h1, h2, ite_false, or_false]
        rw [if_neg (fun e => h2 e.symm)]

/-- Setting distinct cells: each listed cell gets its block. -/
theorem St.get_foldl_set (L : List (Pos × Block)) (hnd : (L.map Prod.fst).Nodup) (s : St)
    (q : Pos) :
    (L.foldl (fun s e => s.set e.1 e.2) s).get q =
      match L.find? (·.1 == q) with
      | some e => some e.2
      | none => s.get q := by
  induction L generalizing s with
  | nil => simp
  | cons e L ih =>
    simp only [List.map_cons, List.nodup_cons] at hnd
    simp only [List.foldl_cons, ih hnd.2, List.find?_cons]
    by_cases h : e.1 = q
    · subst h
      have : L.find? (·.1 == e.1) = none := by
        rw [List.find?_eq_none]
        intro x hx hxe
        exact hnd.1 (List.mem_map.mpr ⟨x, hx, by simpa using hxe⟩)
      simp [this]
    · have h' : (e.1 == q) = false := by simpa using h
      simp only [h']
      cases hf : L.find? (·.1 == q) <;> simp [St.get_set_ne h]

/-! ### `moveBlocks` -/

theorem Ctx.foldl_removeIndexed_st {α} (L : List α) (f : α → Pos) (cx : Ctx) :
    (L.foldl (fun cx e => cx.removeIndexed (f e)) cx).st =
      (L.map f).foldl (fun s p => s.remove p) cx.st := by
  induction L generalizing cx with
  | nil => rfl
  | cons e L ih => simp only [List.foldl_cons, List.map_cons, ih]; rfl

theorem Ctx.foldl_placeIndexed_st {α} (L : List α) (f : α → Pos) (g : α → Block) (cx : Ctx) :
    (L.foldl (fun cx e => cx.placeIndexed (f e) (g e)) cx).st =
      (L.map fun e => (f e, g e)).foldl (fun s e => s.set e.1 e.2) cx.st := by
  induction L generalizing cx with
  | nil => rfl
  | cons e L ih => simp only [List.foldl_cons, List.map_cons, ih]; rfl

/-- The list-carrying pass of `moveBlocks` leaves the world alone. -/
theorem foldlM_setList_world {α} (L : List α) (f : Ctx → α → Except Err Ctx)
    (hf : ∀ cx e cx', f cx e = .ok cx' → cx'.st.world = cx.st.world) :
    ∀ cx cx', L.foldlM f cx = .ok cx' → cx'.st.world = cx.st.world := by
  induction L with
  | nil => intro cx cx' h; cases h; rfl
  | cons e L ih =>
    intro cx cx' h
    simp only [List.foldlM_cons] at h
    cases hfe : f cx e with
    | error err => rw [hfe] at h; cases h
    | ok cx1 =>
      rw [hfe] at h
      exact (ih cx1 cx' h).trans (hf cx e cx1 hfe)

/-- The entry list of `moveBlocks`. -/
def moveEntries (cx : Ctx) (l : List Pos) : List (Pos × Block × List Pos) :=
  l.filterMap fun p => (cx.st.get p).map fun b => (p, b, cx.st.list p)

theorem moveEntries_fst {cx : Ctx} {l : List Pos} (hocc : ∀ p ∈ l, (cx.st.get p).isSome) :
    (moveEntries cx l).map Prod.fst = l := by
  induction l with
  | nil => rfl
  | cons p ps ih =>
    have hp := hocc p (by simp)
    have ih := ih (fun q hq => hocc q (by simp [hq]))
    unfold moveEntries at ih ⊢
    cases hg : cx.st.get p with
    | none => rw [hg] at hp; cases hp
    | some b => simp [hg, ih]

theorem moveEntries_get {cx : Ctx} {l : List Pos} {e : Pos × Block × List Pos}
    (he : e ∈ moveEntries cx l) : cx.st.get e.1 = some e.2.1 := by
  unfold moveEntries at he
  obtain ⟨p, -, hp⟩ := List.mem_filterMap.mp he
  cases hg : cx.st.get p with
  | none => rw [hg] at hp; cases hp
  | some b => rw [hg] at hp; cases hp; exact hg

variable {c : Config} {cx cx' : Ctx} {l ds : List Pos} {dir : Dir}

/-- `moveBlocks` unfolded: the world after it is the world after removing and placing. -/
theorem moveBlocks_ok (h : moveBlocks c cx l dir = .ok (cx', ds)) :
    ds = (moveEntries cx l).map (fun e => e.1.add dir) ∧
    cx'.st.world =
      (((moveEntries cx l).map fun e => (e.1.add dir, e.2.1.startMoving)).foldl
        (fun s e => s.set e.1 e.2)
        (((moveEntries cx l).map Prod.fst).foldl (fun s p => s.remove p) cx.st)).world := by
  unfold moveBlocks at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  split at h
  · cases h
  · rename_i cx2 hfold
    cases h
    refine ⟨rfl, ?_⟩
    rw [foldlM_setList_world _ _ ?_ _ _ hfold]
    · rw [Ctx.foldl_placeIndexed_st, Ctx.foldl_removeIndexed_st]
      rfl
    · intro cx e cx' he
      split at he
      · try simp only [bind, Except.bind, pure, Except.pure] at he
        split at he
        · cases he
        · rename_i st hst
          cases he
          exact St.setList_world hst
      · cases he; rfl

theorem moveBlocks_spec (h : moveBlocks c cx l dir = .ok (cx', ds))
    (hocc : ∀ p ∈ l, (cx.st.get p).isSome) (hnd : l.Nodup) (q : Pos) :
    cx'.st.get q =
      if q.add dir.opp ∈ l then (cx.st.get (q.add dir.opp)).map Block.startMoving
      else if q ∈ l then none else cx.st.get q := by
  obtain ⟨-, hw⟩ := moveBlocks_ok h
  have hfst := moveEntries_fst hocc
  have hget : cx'.st.get q = _ := congrArg (fun w => w[q]?) hw
  rw [hget]
  have hnd' : (((moveEntries cx l).map fun e => (e.1.add dir, e.2.1.startMoving)).map
      Prod.fst).Nodup := by
    rw [List.map_map]
    have : (Prod.fst ∘ fun e : Pos × Block × List Pos => (e.1.add dir, e.2.1.startMoving)) =
        (fun p : Pos => p.add dir) ∘ Prod.fst := rfl
    rw [this, ← List.map_map, hfst]
    exact List.Pairwise.map _ (fun a b hab heq => hab (Pos.add_inj.mp heq)) hnd
  have := St.get_foldl_set _ hnd'
    (((moveEntries cx l).map Prod.fst).foldl (fun s p => s.remove p) cx.st) q
  simp only [St.get] at this
  rw [this, hfst]
  split
  · rename_i x hx
    have hxq := List.find?_some hx
    have hxm := List.mem_of_find?_eq_some hx
    obtain ⟨e, he, rfl⟩ := List.mem_map.mp hxm
    have he1 : e.1.add dir = q := by simpa using hxq
    have hel : e.1 ∈ l := hfst ▸ List.mem_map_of_mem he
    have hq' : q.add dir.opp = e.1 := by rw [← he1]; simp
    rw [if_pos (hq' ▸ hel), hq']
    rw [moveEntries_get he]; rfl
  · rename_i hnone
    rw [List.find?_eq_none] at hnone
    have hnot : q.add dir.opp ∉ l := by
      intro hm
      rw [← hfst] at hm
      obtain ⟨e, he, he1⟩ := List.mem_map.mp hm
      apply hnone (e.1.add dir, e.2.1.startMoving) (List.mem_map_of_mem he)
      simp [he1]
    rw [if_neg hnot]
    have := St.get_foldl_remove l cx.st q
    simp only [St.get] at this
    exact this

end FF
