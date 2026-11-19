/-
Failed extensions, finishing and retraction keep `Wf`.
-/
import Formal.Lemmas.WfExt

namespace FF

open Std

@[simp] theorem Block.finished_moving (b : Block) : b.finished.moving = false := by
  cases b <;> simp [Block.finished, Block.withMoving, Block.moving]

theorem Block.finished_piston {b : Block} {d : Dir} {st an mv : Bool} {k : Fin 4}
    (h : b.finished = .piston d st an k mv) : ∃ an' mv', b = .piston d st an' k mv' := by
  cases b with
  | piston d' st' an' k' mv' =>
    simp only [Block.finished, Block.withMoving, Block.piston.injEq] at h
    obtain ⟨rfl, rfl, rfl, rfl, -⟩ := h
    exact ⟨an', mv', rfl⟩
  | plain k m => cases k <;> simp [Block.finished, Block.withMoving] at h
  | observer => simp [Block.finished] at h
  | rod => simp [Block.finished, Block.withMoving] at h

/-! ### Changing only a piston's `angry` bit -/

theorem Wf.set_angry {s : St} (hW : Wf s) {p : Pos} {d : Dir} {st an an' : Bool} {k : Fin 4}
    {mv : Bool} (hp : s.get p = some (.piston d st an k mv)) :
    Wf (s.set p (.piston d st an' k mv)) := by
  have hl : ∀ q : Pos, (s.set p (.piston d st an' k mv)).lists[q]? = s.lists[q]? := by
    intro q; rw [St.lists_set]; simp [Block.isPiston, Block.kind]
  -- every cell holds what it held, up to `angry`
  have hg : ∀ q b', (s.set p (.piston d st an' k mv)).get q = some b' →
      (q = p ∧ b' = .piston d st an' k mv) ∨ (q ≠ p ∧ s.get q = some b') := by
    intro q b' h
    rw [St.get_set] at h
    split at h
    · rename_i h1; cases h; exact Or.inl ⟨h1.symm, rfl⟩
    · rename_i h1; exact Or.inr ⟨fun e => h1 e.symm, h⟩
  have hkeep : ∀ q b', q ≠ p → s.get q = some b' → (s.set p (.piston d st an' k mv)).get q = some b' := by
    intro q b' hq h; rw [St.get_set_ne (fun e => hq e.symm), h]
  constructor
  · intro q L hL
    rw [hl] at hL
    obtain ⟨d', st', an'', k', hq, hk⟩ := hW.list_owner q L hL
    by_cases hqp : q = p
    · subst hqp; rw [hp] at hq; cases hq
      exact ⟨d, st, an', k, by simp, hk⟩
    · exact ⟨d', st', an'', k', hkeep _ _ hqp hq, hk⟩
  · intro q L r hL hr
    rw [hl] at hL
    obtain ⟨b, hb, hm⟩ := hW.list_moving q L r hL hr
    by_cases hrp : r = p
    · subst hrp; rw [hp] at hb; cases hb
      exact ⟨.piston d st an' k mv, by simp, by simpa [Block.moving] using hm⟩
    · exact ⟨b, hkeep _ _ hrp hb, hm⟩
  · intro q q' L L' r hL hL'
    rw [hl] at hL hL'
    exact hW.list_disjoint q q' L L' r hL hL'
  · intro q d' st' an'' k' h
    rcases hg _ _ h with ⟨rfl, h'⟩ | ⟨-, h'⟩
    · cases h'; exact hW.moving_piston _ _ _ _ _ hp
    · exact hW.moving_piston _ _ _ _ _ h'
  · intro q h
    rcases hg _ _ h with ⟨-, h'⟩ | ⟨-, h'⟩
    · cases h'
    · exact hW.arm_still _ h'
  · intro q d' st' an'' k' mv' h hk
    have hq : s.get q = some (.piston d' st' an'' k' mv') ∨
        (q = p ∧ d' = d ∧ k' = k ∧ s.get q = some (.piston d st an k mv)) := by
      rcases hg _ _ h with ⟨rfl, h'⟩ | ⟨-, h'⟩
      · cases h'; exact Or.inr ⟨rfl, rfl, rfl, hp⟩
      · exact Or.inl h'
    have harm : s.get (q.add d') = some (.plain .arm false) := by
      rcases hq with h' | ⟨rfl, rfl, rfl, h'⟩
      · exact hW.arm_front _ _ _ _ _ _ h' hk
      · exact hW.arm_front _ _ _ _ _ _ h' hk
    have hne : q.add d' ≠ p := by intro e; rw [e, hp] at harm; cases harm
    exact hkeep _ _ hne harm
  · intro q q' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 h1 h2 hk1 hk2 he
    have back : ∀ (r : Pos) (d₀ : Dir) (st₀ an₀ : Bool) (k₀ : Fin 4) (mv₀ : Bool),
        (s.set p (.piston d st an' k mv)).get r = some (.piston d₀ st₀ an₀ k₀ mv₀) →
        ∃ an₁, s.get r = some (.piston d₀ st₀ an₁ k₀ mv₀) := by
      intro r d₀ st₀ an₀ k₀ mv₀ h
      rcases hg _ _ h with ⟨rfl, h'⟩ | ⟨-, h'⟩
      · cases h'; exact ⟨an, hp⟩
      · exact ⟨an₀, h'⟩
    obtain ⟨_, h1'⟩ := back _ _ _ _ _ _ h1
    obtain ⟨_, h2'⟩ := back _ _ _ _ _ _ h2
    exact hW.front_unique _ _ _ _ _ _ _ _ _ _ _ _ h1' h2' hk1 hk2 he

/-! ### Finishing -/

section Finish
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {k next : Fin 4}

theorem finish_wf (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an k false))
    (hk : k.val = 1 ∨ k.val = 3) (hnext : next.val = if k.val = 1 then 2 else 0)
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q)
    (hl : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?)
    (hlp : cx'.st.lists[pos]? = none) : Wf cx'.st := by
  set L := cx.st.list pos with hL
  have hLm : ∀ q ∈ L, ∃ b, cx.st.get q = some b ∧ b.moving = true := by
    intro q hq
    cases hl' : cx.st.lists[pos]? with
    | none => simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl'] at hq
    | some L' =>
      have : L = L' := by simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl']
      exact hW.list_moving pos L' q hl' (this ▸ hq)
  -- the listed cells as a list of `pos`, if any
  have hLin : ∀ q ∈ L, ∃ L', cx.st.lists[pos]? = some L' ∧ q ∈ L' := by
    intro q hq
    cases hl' : cx.st.lists[pos]? with
    | none => simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl'] at hq
    | some L' =>
      have : L = L' := by simp [hL, St.list, ExtTreeMap.getD_eq_getD_getElem?, hl']
      exact ⟨L', rfl, this ▸ hq⟩
  -- a nonmoving cell other than `pos` keeps its block
  have hkeep : ∀ q b, q ≠ pos → cx.st.get q = some b → b.moving = false →
      cx'.st.get q = some b := by
    intro q b hq hb' hm
    rw [hget, if_neg hq, if_neg]
    · exact hb'
    · intro hqL
      obtain ⟨b', hb'', hm'⟩ := hLm q hqL
      rw [hb'] at hb''; cases hb''; rw [hm] at hm'; cases hm'
  have hcases : ∀ q b', cx'.st.get q = some b' →
      (q = pos ∧ b' = .piston d st an next false) ∨
      (q ≠ pos ∧ q ∈ L ∧ ∃ b, cx.st.get q = some b ∧ b.moving = true ∧ b' = b.finished) ∨
      (q ≠ pos ∧ q ∉ L ∧ cx.st.get q = some b') := by
    intro q b' h
    rw [hget] at h
    split at h
    · rename_i hq; cases h; exact Or.inl ⟨hq, rfl⟩
    · rename_i hq
      split at h
      · rename_i hqL
        obtain ⟨b, hb', hm⟩ := hLm q hqL
        rw [hb'] at h; cases h
        exact Or.inr (Or.inl ⟨hq, hqL, b, hb', hm, rfl⟩)
      · rename_i hqL; exact Or.inr (Or.inr ⟨hq, hqL, h⟩)
  have hposNotL : pos ∉ L := by
    intro h; obtain ⟨b, hb', hm⟩ := hLm pos h
    rw [hb] at hb'; cases hb'; simp [Block.moving] at hm
  constructor
  · intro p L' hL'
    by_cases hp : p = pos
    · subst hp; rw [hlp] at hL'; cases hL'
    · rw [hl p hp] at hL'
      obtain ⟨d', st', an', k', hq, hk'⟩ := hW.list_owner p L' hL'
      exact ⟨d', st', an', k', hkeep _ _ hp hq rfl, hk'⟩
  · intro p L' q hL' hq
    by_cases hp : p = pos
    · subst hp; rw [hlp] at hL'; cases hL'
    · rw [hl p hp] at hL'
      obtain ⟨b, hb', hm⟩ := hW.list_moving p L' q hL' hq
      have hqpos : q ≠ pos := by
        rintro rfl; rw [hb] at hb'; cases hb'; simp [Block.moving] at hm
      have hqL : q ∉ L := by
        intro hqL
        obtain ⟨L₀, hL₀, hq₀⟩ := hLin q hqL
        exact hp (hW.list_disjoint p pos L' L₀ q hL' hL₀ hq hq₀)
      refine ⟨b, ?_, hm⟩
      rw [hget, if_neg hqpos, if_neg hqL, hb']
  · intro p p' L1 L2 q h1 h2
    have hp : p ≠ pos := by rintro rfl; rw [hlp] at h1; cases h1
    have hp' : p' ≠ pos := by rintro rfl; rw [hlp] at h2; cases h2
    rw [hl p hp] at h1; rw [hl p' hp'] at h2
    exact hW.list_disjoint p p' L1 L2 q h1 h2
  · intro p d' st' an' k' h
    rcases hcases _ _ h with ⟨-, h'⟩ | ⟨-, -, b, -, -, h'⟩ | ⟨-, -, h'⟩
    · cases h'
    · have := congrArg Block.moving h'; rw [Block.finished_moving] at this; simp [Block.moving] at this
    · exact hW.moving_piston _ _ _ _ _ h'
  · intro p h
    rcases hcases _ _ h with ⟨-, h'⟩ | ⟨-, -, b, -, -, h'⟩ | ⟨-, -, h'⟩
    · cases h'
    · have := congrArg Block.moving h'; rw [Block.finished_moving] at this; simp [Block.moving] at this
    · exact hW.arm_still _ h'
  · intro p d' st' an' k' mv' h hk'
    rcases hcases _ _ h with ⟨hpp, h'⟩ | ⟨-, -, b, hb', hm, h'⟩ | ⟨hp, -, h'⟩
    · cases h'
      rw [hpp]
      -- next = 2, so k = 1
      have hk1 : k.val = 1 := by
        rcases hk with h1 | h1
        · exact h1
        · unfold armOut at hk'; rw [hnext, h1] at hk'; simp at hk'
      have harm := hW.arm_front pos d st an k false hb (Or.inl hk1)
      exact hkeep _ _ (Pos.add_ne_self pos d) harm rfl
    · obtain ⟨an₁, mv₁, rfl⟩ := Block.finished_piston h'.symm
      have hmv : mv₁ = true := by simpa [Block.moving] using hm
      subst hmv
      have := hW.moving_piston _ _ _ _ _ hb'
      rcases hk' with h1 | h1 <;> omega
    · have harm := hW.arm_front _ _ _ _ _ _ h' hk'
      have hne : p.add d' ≠ pos := by intro e; rw [e, hb] at harm; cases harm
      exact hkeep _ _ hne harm rfl
  · have back : ∀ (r : Pos) (d₀ : Dir) (st₀ an₀ : Bool) (k₀ : Fin 4) (mv₀ : Bool),
        cx'.st.get r = some (.piston d₀ st₀ an₀ k₀ mv₀) → armOut k₀ →
        ∃ k₁ an₁ mv₁, armOut k₁ ∧ cx.st.get r = some (.piston d₀ st₀ an₁ k₁ mv₁) := by
      intro r d₀ st₀ an₀ k₀ mv₀ h hk₀
      rcases hcases _ _ h with ⟨hrp, h'⟩ | ⟨-, -, b, hb', hm, h'⟩ | ⟨-, -, h'⟩
      · cases h'
        rw [hrp]
        have hk1 : k.val = 1 := by
          rcases hk with h1 | h1
          · exact h1
          · unfold armOut at hk₀; rw [hnext, h1] at hk₀; simp at hk₀
        exact ⟨k, an, false, Or.inl hk1, hb⟩
      · obtain ⟨an₁, mv₁, rfl⟩ := Block.finished_piston h'.symm
        have hmv : mv₁ = true := by simpa [Block.moving] using hm
        subst hmv
        have := hW.moving_piston _ _ _ _ _ hb'
        rcases hk₀ with h1 | h1 <;> omega
      · exact ⟨k₀, an₀, mv₀, hk₀, h'⟩
    intro p p' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 h1 h2 hk1 hk2 he
    obtain ⟨k1', _, _, hk1', h1'⟩ := back _ _ _ _ _ _ h1 hk1
    obtain ⟨k2', _, _, hk2', h2'⟩ := back _ _ _ _ _ _ h2 hk2
    exact hW.front_unique _ _ _ _ _ _ _ _ _ _ _ _ h1' h2' hk1' hk2' he

end Finish

/-! ### Retraction -/

section Retract
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem pulled_moveOK :
    MoveOK (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp (some pos) := by
  rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := d) (st := st) with h | h
  · rw [h]; exact moveOK_nil
  · exact discover_moveOK h

theorem retract_wf (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hl : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp))) : Wf cx'.st := by
  set S := pulled c cx.st pos d st with hS
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hfront : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hW1get : ∀ q, q ≠ pos.add d → W1.get q = cx.st.get q := fun q hq =>
    St.get_remove_ne (Ne.symm hq)
  have hpos1 : W1.get pos = some (.piston d st an 2 false) := by rw [hW1get pos (Ne.symm hfront), hb]
  have hposI : immovable (some pos) pos (.piston d st an 2 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hpos1 hposI
  have hfrontS : pos.add d ∉ S := by
    intro h; obtain ⟨b, hb', -⟩ := hM.1 _ h; simp [hW1] at hb'
  -- an immovable cell other than the piston and its front keeps its block
  have hkeep : ∀ q b, q ≠ pos → q ≠ pos.add d → cx.st.get q = some b →
      immovable (some pos) q b = true → cx'.st.get q = some b := by
    intro q b hq hf hqb hi
    rw [hget, if_neg hq]
    exact mw_immovable hM (by rw [hW1get q hf, hqb]) hi
  have hcases : ∀ q b', cx'.st.get q = some b' →
      (q = pos ∧ b' = .piston d st an 3 false) ∨
      (q ≠ pos ∧ q ≠ pos.add d ∧ cx.st.get q = some b') ∨
      (∃ b, q.add d.opp.opp ∈ S ∧ W1.get (q.add d.opp.opp) = some b ∧
        immovable (some pos) (q.add d.opp.opp) b = false ∧ b' = b.startMoving) := by
    intro q b' h
    rw [hget] at h
    split at h
    · rename_i hq; cases h; exact Or.inl ⟨hq, rfl⟩
    · rename_i hq
      rcases mw_cases hM h with ⟨h1, -, -⟩ | h2
      · have hf : q ≠ pos.add d := by rintro rfl; simp [hW1] at h1
        exact Or.inr (Or.inl ⟨hq, hf, by rw [← hW1get q hf]; exact h1⟩)
      · exact Or.inr (Or.inr h2)
  have hdest_ne_pos : ∀ r ∈ S, r.add d.opp ≠ pos := by
    intro r hr he
    have : r = pos.add d := by rw [← he]; simp
    exact hfrontS (this ▸ hr)
  have hnewlist : ∀ L, cx'.st.lists[pos]? = some L → ∀ q ∈ L,
      ∃ r ∈ S, q = r.add d.opp ∧ ∃ b, cx'.st.get q = some b.startMoving ∧
        W1.get r = some b ∧ immovable (some pos) r b = false := by
    intro L hL q hq
    obtain ⟨r, hr, rfl⟩ := List.mem_map.mp ((hlp L hL).mem_iff.mp hq)
    obtain ⟨b, hb', hi⟩ := hM.1 r hr
    refine ⟨r, hr, rfl, b, ?_, hb', hi⟩
    rw [hget, if_neg (hdest_ne_pos r hr), mw_dest hr, hb']
    rfl
  have harmI : immovable (some pos) (pos.add d) (.plain .arm false) = true := by
    simp [immovable, Block.kind]
  constructor
  · intro p L hL
    by_cases hp : p = pos
    · subst hp; exact ⟨d, st, an, 3, by rw [hget]; simp, Or.inr rfl⟩
    · rw [hl p hp] at hL
      obtain ⟨d', st', an', k, hpk, hk⟩ := hW.list_owner p L hL
      have hpf : p ≠ pos.add d := by intro e; rw [e, harm] at hpk; cases hpk
      refine ⟨d', st', an', k, hkeep _ _ hp hpf hpk ?_, hk⟩
      simp only [immovable, Block.isPiston, Block.kind, Block.state, Block.moving]
      rcases hk with h | h <;> simp [h]
  · intro p L q hL hq
    by_cases hp : p = pos
    · subst hp
      obtain ⟨r, -, -, b, hget', -, -⟩ := hnewlist L hL q hq
      exact ⟨_, hget', by simp⟩
    · rw [hl p hp] at hL
      obtain ⟨b, hqb, hm⟩ := hW.list_moving p L q hL hq
      have hqpos : q ≠ pos := by
        rintro rfl; rw [hb] at hqb; cases hqb; simp [Block.moving] at hm
      have hqf : q ≠ pos.add d := by
        intro e; rw [e, harm] at hqb; cases hqb; simp [Block.moving] at hm
      exact ⟨b, hkeep _ _ hqpos hqf hqb (by simp [immovable, hm]), hm⟩
  · intro p p' L L' q hL hL' hq hq'
    have key : ∀ (p₁ : Pos) (L₁ : List Pos), p₁ ≠ pos → cx'.st.lists[p₁]? = some L₁ → q ∈ L₁ →
        ∀ L₀, cx'.st.lists[pos]? = some L₀ → q ∈ L₀ → False := by
      intro p₁ L₁ hp₁ hL₁ hq₁ L₀ hL₀ hq₀
      rw [hl p₁ hp₁] at hL₁
      obtain ⟨b, hqb, hm⟩ := hW.list_moving p₁ L₁ q hL₁ hq₁
      obtain ⟨r, hr, hqr, -⟩ := hnewlist L₀ hL₀ _ hq₀
      have hqf : q ≠ pos.add d := by
        intro e; rw [e, harm] at hqb; cases hqb; simp [Block.moving] at hm
      have hq1 : W1.get q = some b := by rw [hW1get q hqf, hqb]
      subst hqr
      have := hM.2 r hr (by rw [hq1]; rfl)
      exact mw_not_mem_of_immovable hM hq1 (by simp [immovable, hm]) this
    by_cases hp : p = pos <;> by_cases hp' : p' = pos
    · rw [hp, hp']
    · exact (key p' L' hp' hL' hq' L (hp ▸ hL) hq).elim
    · exact (key p L hp hL hq L' (hp' ▸ hL') hq').elim
    · rw [hl p hp] at hL; rw [hl p' hp'] at hL'
      exact hW.list_disjoint p p' L L' q hL hL' hq hq'
  · intro p d' st' an' k h
    rcases hcases _ _ h with ⟨-, h'⟩ | ⟨-, -, h'⟩ | ⟨b, -, -, hi, h'⟩
    · cases h'
    · exact hW.moving_piston _ _ _ _ _ h'
    · exact (Block.startMoving_piston hi h'.symm).1
  · intro p h
    rcases hcases _ _ h with ⟨-, h'⟩ | ⟨-, -, h'⟩ | ⟨b, -, -, hi, h'⟩
    · cases h'
    · exact hW.arm_still _ h'
    · exact Block.startMoving_not_arm hi h'.symm
  · intro p d' st' an' k mv h hk
    rcases hcases _ _ h with ⟨-, h'⟩ | ⟨hp, hpf, h'⟩ | ⟨b, -, -, hi, h'⟩
    · cases h'; exact absurd hk (by decide)
    · have harm' := hW.arm_front _ _ _ _ _ _ h' hk
      have hne : p.add d' ≠ pos := by intro e; rw [e, hb] at harm'; cases harm'
      have hnf : p.add d' ≠ pos.add d := by
        intro e
        exact hp (hW.front_unique _ _ _ _ _ _ _ _ _ _ _ _ h' hb hk (Or.inr rfl) e)
      exact hkeep _ _ hne hnf harm' (by simp [immovable, Block.kind])
    · have := (Block.startMoving_piston hi h'.symm).1
      rcases hk with h1 | h1 <;> omega
  · have back : ∀ (r : Pos) (d₀ : Dir) (st₀ an₀ : Bool) (k₀ : Fin 4) (mv₀ : Bool),
        cx'.st.get r = some (.piston d₀ st₀ an₀ k₀ mv₀) → armOut k₀ →
        cx.st.get r = some (.piston d₀ st₀ an₀ k₀ mv₀) := by
      intro r d₀ st₀ an₀ k₀ mv₀ h hk₀
      rcases hcases _ _ h with ⟨-, h'⟩ | ⟨-, -, h'⟩ | ⟨b, -, -, hi, h'⟩
      · cases h'; exact absurd hk₀ (by decide)
      · exact h'
      · have := (Block.startMoving_piston hi h'.symm).1
        rcases hk₀ with h1 | h1 <;> omega
    intro p p' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 h1 h2 hk1 hk2 he
    exact hW.front_unique _ _ _ _ _ _ _ _ _ _ _ _ (back _ _ _ _ _ _ h1 hk1)
      (back _ _ _ _ _ _ h2 hk2) hk1 hk2 he

end Retract

end FF
