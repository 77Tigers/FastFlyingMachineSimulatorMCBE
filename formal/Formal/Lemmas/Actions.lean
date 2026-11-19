/-
What each piston action does, on a well-formed state (`Wf`): the action succeeds (no Rust
error), the new contents of every cell, the piston lists, and that cached power only
shrinks.
-/
import Formal.Inv
import Formal.Lemmas.Closure
import Mathlib.Tactic.Set

namespace FF

open Std

@[simp] theorem Dir.opp_opp (d : Dir) : d.opp.opp = d := by cases d <;> rfl

theorem Pos.add_ne_self (p : Pos) (d : Dir) : p.add d ≠ p := by
  intro h
  cases p; cases d <;> simp only [Pos.add, Dir.dx, Dir.dy, Dir.dz, Pos.mk.injEq] at h <;> omega

/-- The world after moving the cells `S` one step along `d`. -/
def moveWorld (s : St) (S : List Pos) (d : Dir) (q : Pos) : Option Block :=
  if q.add d.opp ∈ S then (s.get (q.add d.opp)).map Block.startMoving
  else if q ∈ S then none else s.get q

/-- No piston list sits on an empty or a movable cell. -/
def NoStray (s : St) : Prop :=
  (∀ q, s.get q = none → s.lists[q]? = none) ∧
  (∀ q b o, s.get q = some b → immovable o q b = false → s.lists[q]? = none)

theorem Wf.noStray {s : St} (hW : Wf s) : NoStray s :=
  ⟨fun _ h => hW.no_list_empty h, fun _ _ _ h hm => hW.no_list_movable h hm⟩

theorem NoStray.remove {s : St} (h : NoStray s) (f : Pos) : NoStray (s.remove f) := by
  constructor
  · intro q hq
    rw [St.lists_remove]
    split
    · rfl
    · rename_i hfq
      rw [St.get_remove_ne hfq] at hq
      exact h.1 q hq
  · intro q b o hq hm
    rw [St.lists_remove]
    split
    · rfl
    · rename_i hfq
      rw [St.get_remove_ne hfq] at hq
      exact h.2 q b o hq hm

section Discovered
variable {c : Config} {s : St} {first : Pos} {d : Dir} {o : Option Pos} {pl : Bool}
  {S : List Pos}

theorem discover_occ (h : discover c s first d o pl = some S) :
    ∀ p ∈ S, (s.get p).isSome := by
  intro p hp
  obtain ⟨b, hb, -⟩ := discover_mem h hp
  simp [hb]

theorem discover_no_list (hW : NoStray s) (h : discover c s first d o pl = some S) :
    ∀ p ∈ S, s.lists[p]? = none := by
  intro p hp
  obtain ⟨b, hb, hm⟩ := discover_mem h hp
  exact hW.2 _ _ _ hb hm

theorem discover_no_list_dest (hW : NoStray s) (h : discover c s first d o pl = some S) :
    ∀ p ∈ S, s.lists[p.add d]? = none := by
  intro p hp
  cases hg : s.get (p.add d) with
  | none => exact hW.1 _ hg
  | some _ => exact discover_no_list hW h _ (discover_dest_mem h hp (by simp [hg]))

theorem discover_no_list_first (hW : NoStray s) (h : discover c s first d o pl = some S) :
    s.lists[first]? = none := by
  cases hg : s.get first with
  | none => exact hW.1 _ hg
  | some _ => exact discover_no_list hW h _ (discover_first_mem h (by simp [hg]))

theorem discover_dests_nodup (h : discover c s first d o pl = some S) :
    (S.map (·.add d)).Nodup :=
  List.Pairwise.map _ (fun _ _ hab heq => hab (Pos.add_inj.mp heq)) (discover_nodup h)

end Discovered

section Ext
variable {c : Config} {cx : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {S : List Pos}

/-- A successful extension. -/
theorem ext_spec (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hfire : (cx.powered.contains pos || an) = true)
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧
      (∀ q, cx'.st.get q =
        if q = pos then some (.piston d st false 1 false)
        else if q = pos.add d then some (.plain .arm false) else moveWorld cx.st S d q) ∧
      (∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?) ∧
      (S = [] → cx'.st.lists[pos]? = none) ∧
      (S ≠ [] → ∃ L, cx'.st.lists[pos]? = some L ∧ L.Perm (S.map (·.add d))) ∧
      (∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) := by
  have hocc := discover_occ hS
  have hnd := discover_nodup hS
  have hno := discover_no_list hW.noStray hS
  have hdest := discover_no_list_dest hW.noStray hS
  have hfront := discover_no_list_first hW.noStray hS
  have hmove := moveBlocks_eq (c := c) (dir := d) hocc hno
  set m := movedCtx cx S d with hm
  set cx1 := m.placeIndexed (pos.add d) (.plain .arm false) with hcx1
  set st2 := cx1.st.set pos (.piston d st false 1 false) with hst2
  have hlen : (S.map (·.add d)).length ≤ c.pushLimit := by
    simpa using discover_length_le hS
  obtain ⟨s3, hs3, hw3, hl3, he3, hne3⟩ :=
    St.setList_ok (c := c) (s := st2) (p := pos) (b := .piston d st false 1 false)
      (by simp [hst2]) rfl hlen (discover_dests_nodup hS)
  refine ⟨{ cx1 with st := s3 }, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · unfold pistonTurn
    rw [hb]
    simp only [Fin.val_zero, hfire, ite_true]
    unfold startExtension
    simp only [hS, bind, Except.bind, pure, Except.pure]
    rw [hmove]
    simp only
    rw [← hcx1, ← hst2, hs3]
  · intro q
    show s3.world[q]? = _
    rw [hw3]
    show st2.get q = _
    rw [hst2, St.get_set]
    by_cases hq : q = pos
    · subst hq; simp
    · rw [if_neg (fun h => hq h.symm), if_neg hq, hcx1, Ctx.placeIndexed_st, St.get_set]
      by_cases hf : q = pos.add d
      · subst hf; simp
      · rw [if_neg (fun h => hf h.symm), if_neg hf]
        unfold moveWorld
        exact movedCtx_get (dir := d) hocc hnd hno q
  · intro q hq
    rw [hl3 q hq, hst2, St.lists_set, hcx1, Ctx.placeIndexed_st, St.lists_set]
    simp only [Block.isPiston, Block.kind, show (Kind.piston == Kind.piston) = true from rfl,
      show (Kind.arm == Kind.piston) = false from rfl, Bool.true_eq_false, and_false, and_true,
      if_false]
    rw [hm, movedCtx_lists hocc hno hdest]
    by_cases hf : pos.add d = q
    · subst hf; simp [hfront]
    · simp [hf]
  · intro he
    exact he3 (by simp [he])
  · intro hne
    exact hne3 (by simpa using hne)
  · intro q hq
    exact movedCtx_powered (Ctx.placeIndexed_powered_le (b := .plain .arm false) hq)

/-- A failed extension: the piston becomes angry, nothing else changes. -/
theorem extFail_spec (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hfire : (cx.powered.contains pos || an) = true)
    (hS : discover c cx.st (pos.add d) d (some pos) false = none) :
    pistonTurn c cx pos = .ok { cx with st := cx.st.set pos (.piston d st true 0 false) } := by
  unfold pistonTurn
  rw [hb]
  simp only [Fin.val_zero, hfire, ite_true]
  unfold startExtension
  simp only [hS, bind, Except.bind, pure, Except.pure]

end Ext

/-! ### Finishing a movement -/

/-- What finishing does to one block. -/
def Block.finished : Block → Block
  | .observer d _ _ => .observer d true false
  | b => b.withMoving false

theorem finishMovedBlock_get (s : St) (p q : Pos) :
    (finishMovedBlock s p).get q = if p = q then (s.get q).map Block.finished else s.get q := by
  unfold finishMovedBlock
  by_cases h : p = q
  · subst h
    split <;> rename_i hg <;> simp [hg, Block.finished]
  · simp only [h, if_false]
    split <;> simp [St.get_set_ne h]

theorem Block.finished_finished (b : Block) : b.finished.finished = b.finished := by
  cases b <;> simp [Block.finished, Block.withMoving]

theorem foldl_finish_get (L : List Pos) (s : St) (q : Pos) :
    (L.foldl finishMovedBlock s).get q = if q ∈ L then (s.get q).map Block.finished else s.get q := by
  induction L generalizing s with
  | nil => simp
  | cons p L ih =>
    simp only [List.foldl_cons, ih, finishMovedBlock_get, List.mem_cons]
    by_cases h1 : q ∈ L
    · by_cases h2 : p = q
      · subst h2; simp [Option.map_map, Function.comp_def, Block.finished_finished]
      · simp [h1, h2]
    · by_cases h2 : p = q
      · subst h2; simp [h1]
      · simp [h1, h2]; intro e; exact absurd e.symm h2

theorem foldl_finish_lists (L : List Pos) (s : St) (q : Pos)
    (h : ∀ p ∈ L, s.lists[p]? = none) :
    (L.foldl finishMovedBlock s).lists[q]? = s.lists[q]? := by
  induction L generalizing s with
  | nil => rfl
  | cons p L ih =>
    simp only [List.foldl_cons]
    have hp : (finishMovedBlock s p).lists[q]? = s.lists[q]? := by
      unfold finishMovedBlock
      split
      · rw [St.lists_set]; split
        · rename_i hh; rw [← hh.1]; exact (h p (by simp)).symm
        · rfl
      · rw [St.lists_set]; split
        · rename_i hh; rw [← hh.1]; exact (h p (by simp)).symm
        · rfl
      · rfl
    rw [ih, hp]
    intro p' hp'
    have : (finishMovedBlock s p).lists[p']? = s.lists[p']? := by
      unfold finishMovedBlock
      split
      · rw [St.lists_set]; split
        · rename_i hh; rw [← hh.1]; exact (h p (by simp)).symm
        · rfl
      · rw [St.lists_set]; split
        · rename_i hh; rw [← hh.1]; exact (h p (by simp)).symm
        · rfl
      · rfl
    rw [this]; exact h p' (by simp [hp'])

theorem foldl_finish_world_preserves {L : List Pos} {s : St} {q : Pos} (hq : q ∉ L) :
    (L.foldl finishMovedBlock s).get q = s.get q := by
  rw [foldl_finish_get]; simp [hq]

section Finish
variable {c : Config} {cx : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {k next : Fin 4}

/-- Finishing (state 1 to 2, or 3 to 0): the listed blocks stop moving, the list is cleared. -/
theorem finish_spec (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an k false))
    (hk : k.val = 1 ∨ k.val = 3) (hnext : next.val = if k.val = 1 then 2 else 0) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧
      (∀ q, cx'.st.get q =
        if q = pos then some (.piston d st an next false)
        else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q) ∧
      (∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?) ∧
      cx'.st.lists[pos]? = none ∧
      cx'.powered = cx.powered := by
  set L := cx.st.list pos with hL
  -- the listed cells hold moving blocks, so they are not `pos` and carry no list
  have hLm : ∀ q ∈ L, ∃ b, cx.st.get q = some b ∧ b.moving = true := by
    intro q hq
    cases hl : cx.st.lists[pos]? with
    | none =>
      simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl] at hq
    | some L' =>
      have : L = L' := by simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl]
      exact hW.list_moving pos L' q hl (this ▸ hq)
  have hposL : pos ∉ L := by
    intro h
    obtain ⟨b, hb', hm⟩ := hLm pos h
    rw [hb] at hb'; cases hb'; simp [Block.moving] at hm
  have hLl : ∀ q ∈ L, cx.st.lists[q]? = none := by
    intro q hq
    obtain ⟨b, hb', hm⟩ := hLm q hq
    exact hW.no_list_of fun _ _ _ _ hp _ => by rw [hb'] at hp; cases hp; simp [Block.moving] at hm
  set s1 := L.foldl finishMovedBlock cx.st with hs1
  have hs1pos : s1.get pos = some (.piston d st an k false) := by
    rw [hs1, foldl_finish_world_preserves hposL, hb]
  obtain ⟨s2, hs2, hw2, hl2, he2, -⟩ :=
    St.setList_ok (c := c) (l := []) hs1pos rfl (by simp) List.nodup_nil
  refine ⟨{ cx with st := s2.set pos (.piston d st an next false) }, ?_, ?_, ?_, ?_, rfl⟩
  · unfold pistonTurn
    rw [hb]
    rcases hk with hk | hk
    · have hn : next = 2 := Fin.ext (by simp [hnext, hk])
      subst hn
      simp only [hk]
      unfold finishMovement
      simp only [bind, Except.bind, pure, Except.pure]
      rw [← hL, ← hs1, hs2]
    · have hn : next = 0 := Fin.ext (by simp [hnext, hk])
      subst hn
      simp only [hk]
      unfold finishMovement
      simp only [bind, Except.bind, pure, Except.pure]
      rw [← hL, ← hs1, hs2]
  · intro q
    rw [St.get_set]
    by_cases hq : q = pos
    · subst hq; simp
    · rw [if_neg (fun h => hq h.symm), if_neg hq]
      show s2.world[q]? = _
      rw [hw2]
      show s1.get q = _
      rw [hs1, foldl_finish_get]
  · intro q hq
    rw [St.lists_set]
    simp only [Block.isPiston, Block.kind, show (Kind.piston == Kind.piston) = true from rfl,
      Bool.true_eq_false, and_false, if_false]
    rw [hl2 q hq, hs1, foldl_finish_lists _ _ _ hLl]
  · rw [St.lists_set]
    simp only [Block.isPiston, Block.kind, show (Kind.piston == Kind.piston) = true from rfl,
      Bool.true_eq_false, and_false, if_false]
    exact he2 rfl

end Finish

/-! ### Retraction -/

/-- The cells a retraction pulls: empty for a normal piston or a failed pull. -/
def pulled (c : Config) (s : St) (pos : Pos) (d : Dir) (sticky : Bool) : List Pos :=
  if sticky then
    (discover c (s.remove (pos.add d)) ((pos.add d).add d) d.opp (some pos) true).getD []
  else []

section Retract
variable {c : Config} {cx : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem pulled_cases :
    pulled c cx.st pos d st = [] ∨
      discover c (cx.st.remove (pos.add d)) ((pos.add d).add d) d.opp (some pos) true =
        some (pulled c cx.st pos d st) := by
  unfold pulled
  cases st
  · simp
  · simp only [ite_true]
    cases h : discover c (cx.st.remove (pos.add d)) ((pos.add d).add d) d.opp (some pos) true
    · simp
    · simp

/-- The middle of a retraction: after removing the arm, the pull. -/
theorem retract_mid (hNS : NoStray (cx.removeIndexed (pos.add d)).st) :
    ∃ cx2 : Ctx,
      retractPull c (cx.removeIndexed (pos.add d)) pos d st =
        .ok (cx2, (pulled c cx.st pos d st).map (·.add d.opp)) ∧
      (∀ q : Pos, cx2.st.get q = moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) ∧
      (∀ q : Pos, cx2.st.lists[q]? = (cx.st.remove (pos.add d)).lists[q]?) ∧
      (∀ q : Pos, cx2.powered.contains q = true → (cx.removeIndexed (pos.add d)).powered.contains q = true) := by
  set cx1 := cx.removeIndexed (pos.add d) with hcx1
  have hst1 : cx1.st = cx.st.remove (pos.add d) := rfl
  have base : ∀ q, cx1.st.get q = moveWorld (cx.st.remove (pos.add d)) [] d.opp q := by
    intro q; simp [moveWorld, hst1]
  unfold retractPull
  cases st
  · refine ⟨cx1, by simp [pulled]; rfl, ?_, fun q => by rw [hst1], fun q h => h⟩
    intro q; rw [base]; simp [pulled]
  · simp only [ite_true]
    cases hd : discover c cx1.st ((pos.add d).add d) d.opp (some pos) true with
    | none =>
      have hp : pulled c cx.st pos d true = [] := by
        simp [pulled, ← hst1, hd]
      refine ⟨cx1, by simp [hp]; rfl, ?_, fun q => by rw [hst1], fun q h => h⟩
      intro q; rw [base, hp]
    | some S =>
      have hp : pulled c cx.st pos d true = S := by
        simp [pulled, ← hst1, hd]
      have hocc := discover_occ hd
      have hnd := discover_nodup hd
      have hno := discover_no_list hNS hd
      have hdest := discover_no_list_dest hNS hd
      refine ⟨movedCtx cx1 S d.opp, ?_, ?_, ?_, ?_⟩
      · simp only [hp]; exact moveBlocks_eq hocc hno
      · intro q; rw [hp]; unfold moveWorld; rw [← hst1]; exact movedCtx_get hocc hnd hno q
      · intro q; rw [movedCtx_lists hocc hno hdest, hst1]
      · intro q h; exact movedCtx_powered h

theorem pulled_length :
    (pulled c cx.st pos d st).length ≤ c.pushLimit ∧ (pulled c cx.st pos d st).Nodup := by
  rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := d) (st := st) with h | h
  · rw [h]; simp
  · exact ⟨discover_length_le h, discover_nodup h⟩

/-- A retraction (state 2, unpowered): the arm cell is cleared, a sticky piston pulls. -/
theorem retract_spec (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hpw : cx.powered.contains pos = false) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧
      (∀ q, cx'.st.get q =
        if q = pos then some (.piston d st an 3 false)
        else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) ∧
      (∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?) ∧
      (pulled c cx.st pos d st = [] → cx'.st.lists[pos]? = none) ∧
      (pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L ∧
        L.Perm ((pulled c cx.st pos d st).map (·.add d.opp))) ∧
      (∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) := by
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hfl : cx.st.lists[pos.add d]? = none :=
    hW.no_list_of fun _ _ _ _ hp _ => by rw [harm] at hp; cases hp
  have hNS : NoStray (cx.removeIndexed (pos.add d)).st := hW.noStray.remove _
  obtain ⟨cx2, hmid, hget2, hl2, hpw2⟩ := retract_mid (c := c) (st := st) hNS
  set S := pulled c cx.st pos d st with hS
  have hne : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hpos2 : cx2.st.get pos = some (.piston d st an 2 false) := by
    rw [hget2]
    unfold moveWorld
    -- `pos` is the owner, so it is neither pulled nor a destination of the pull
    rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := d) (st := st) with h | h
    · rw [← hS] at h; rw [h]; simp [St.get_remove_ne hne, hb]
    · rw [← hS] at h
      have hposS : pos ∉ S := by
        intro hm
        obtain ⟨b, hb', hm'⟩ := discover_mem h hm
        simp [immovable] at hm'
      have hopp : pos.add d ∉ S := by
        intro hm
        obtain ⟨b, hb', -⟩ := discover_mem h hm
        simp at hb'
      simp [Dir.opp_opp, hposS, hopp, St.get_remove_ne hne, hb]
  set st3 := cx2.st.set pos (.piston d st an 3 false) with hst3
  have hlen := pulled_length (c := c) (cx := cx) (pos := pos) (d := d) (st := st)
  obtain ⟨s4, hs4, hw4, hl4, he4, hne4⟩ :=
    St.setList_ok (c := c) (s := st3) (p := pos) (b := .piston d st an 3 false)
      (by simp [hst3]) rfl (by simpa using hlen.1)
      (List.Pairwise.map _ (fun _ _ hab heq => hab (Pos.add_inj.mp heq)) hlen.2)
  refine ⟨{ cx2 with st := s4 }, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · unfold pistonTurn
    rw [hb]
    simp only [show (2 : Fin 4).val = 2 from rfl, hpw, Bool.false_eq_true, ite_false]
    unfold startRetraction
    simp only [bind, Except.bind, pure, Except.pure]
    rw [hmid]
    simp only
    rw [← hst3, hs4]
  · intro q
    show s4.world[q]? = _
    rw [hw4]
    show st3.get q = _
    rw [hst3, St.get_set]
    by_cases hq : q = pos
    · subst hq; simp
    · rw [if_neg (fun h => hq h.symm), if_neg hq, hget2]
  · intro q hq
    rw [hl4 q hq, hst3, St.lists_set]
    simp only [Block.isPiston, Block.kind, show (Kind.piston == Kind.piston) = true from rfl,
      Bool.true_eq_false, and_false, if_false]
    rw [hl2, St.lists_remove]
    split
    · rename_i h; rw [← h]; exact hfl.symm
    · rfl
  · intro h; exact he4 (by rw [← hS, h]; rfl)
  · intro h; exact hne4 (by rw [← hS]; simpa using h)
  · intro q h
    exact Ctx.removeIndexed_powered_le (hpw2 q h)

end Retract

end FF
