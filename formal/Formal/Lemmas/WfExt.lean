/-
A successful extension keeps `Wf`.
-/
import Formal.Lemmas.MoveWorld

namespace FF

open Std

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {S : List Pos}

/-- The facts about the state after a successful extension that the invariant needs. -/
structure ExtResult (cx cx' : Ctx) (pos : Pos) (d : Dir) (st : Bool) (S : List Pos) : Prop where
  get : ∀ q, cx'.st.get q =
    if q = pos then some (.piston d st false 1 false)
    else if q = pos.add d then some (.plain .arm false) else moveWorld cx.st S d q
  lists_ne : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?
  lists_pos : ∀ L, cx'.st.lists[pos]? = some L → L.Perm (S.map (·.add d))
  lists_some : S ≠ [] → ∃ L, cx'.st.lists[pos]? = some L

theorem ext_result (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hfire : (cx.powered.contains pos || an) = true)
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧ ExtResult cx cx' pos d st S ∧
      (∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) := by
  obtain ⟨cx', h1, h2, h3, h4, h5, h6⟩ := ext_spec hW hb hfire hS
  refine ⟨cx', h1, ⟨h2, h3, ?_, fun h => (h5 h).imp fun _ h' => h'.1⟩, h6⟩
  intro L hL
  by_cases hS0 : S = []
  · rw [h4 hS0] at hL; cases hL
  · obtain ⟨L', hL', hperm⟩ := h5 hS0
    rw [hL] at hL'; cases hL'
    exact hperm

variable (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
  (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
  (hR : ExtResult cx cx' pos d st S)
include hW hb hS hR

/-- An immovable cell other than the piston keeps its block. -/
theorem ext_keep {q : Pos} {b : Block} (hq : cx.st.get q = some b)
    (hi : immovable (some pos) q b = true) (hne : q ≠ pos) : cx'.st.get q = some b := by
  rw [hR.get, if_neg hne]
  have hnf : q ≠ pos.add d := by
    rintro rfl
    have hm := discover_first_mem hS (by rw [hq]; rfl)
    exact mw_not_mem_of_immovable (discover_moveOK hS) hq hi hm
  rw [if_neg hnf]
  exact mw_immovable (discover_moveOK hS) hq hi

/-- Every occupied cell after the extension. -/
theorem ext_cases {q : Pos} {b' : Block} (h : cx'.st.get q = some b') :
    (q = pos ∧ b' = .piston d st false 1 false) ∨ (q = pos.add d ∧ b' = .plain .arm false) ∨
    (q ≠ pos ∧ q ≠ pos.add d ∧ cx.st.get q = some b') ∨
    (∃ b, q.add d.opp ∈ S ∧ cx.st.get (q.add d.opp) = some b ∧
      immovable (some pos) (q.add d.opp) b = false ∧ b' = b.startMoving) := by
  rw [hR.get] at h
  split at h
  · rename_i hq; cases h; exact Or.inl ⟨hq, rfl⟩
  · rename_i hq
    split at h
    · rename_i hf; cases h; exact Or.inr (Or.inl ⟨hf, rfl⟩)
    · rename_i hf
      rcases mw_cases (discover_moveOK hS) h with ⟨h1, -, -⟩ | h2
      · exact Or.inr (Or.inr (Or.inl ⟨hq, hf, h1⟩))
      · exact Or.inr (Or.inr (Or.inr h2))

theorem ext_wf : Wf cx'.st := by
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable (discover_moveOK hS) hb hposI
  -- a destination is never the piston or its front
  have hdest_ne_pos : ∀ r ∈ S, r.add d ≠ pos := by
    intro r hr he
    exact mw_src_not_mem_of_immovable (discover_moveOK hS) hb hposI (by rw [← he, Pos.add_add_opp]; exact hr)
  have hdest_ne_front : ∀ r ∈ S, r.add d ≠ pos.add d := by
    intro r hr he; rw [Pos.add_inj] at he; subst he; exact hposS hr
  -- the front holds nothing immovable
  have hfront_mov : ∀ b, cx.st.get (pos.add d) = some b →
      immovable (some pos) (pos.add d) b = false := by
    intro b hb'
    obtain ⟨b'', hb'', hm⟩ := discover_mem hS (discover_first_mem hS (by rw [hb']; rfl))
    rw [hb'] at hb''; cases hb''; exact hm
  -- the new list holds moved blocks
  have hnewlist : ∀ L, cx'.st.lists[pos]? = some L → ∀ q ∈ L,
      ∃ r ∈ S, q = r.add d ∧ ∃ b, cx'.st.get q = some b.startMoving ∧
        cx.st.get r = some b ∧ immovable (some pos) r b = false := by
    intro L hL q hq
    obtain ⟨r, hr, rfl⟩ := List.mem_map.mp ((hR.lists_pos L hL).mem_iff.mp hq)
    obtain ⟨b, hb', hi⟩ := discover_mem hS hr
    refine ⟨r, hr, rfl, b, ?_, hb', hi⟩
    rw [hR.get, if_neg (hdest_ne_pos r hr), if_neg (hdest_ne_front r hr), mw_dest hr, hb']
    rfl
  constructor
  · -- list_owner
    intro p L hL
    by_cases hp : p = pos
    · subst hp
      exact ⟨d, st, false, 1, by rw [hR.get]; simp, Or.inl rfl⟩
    · rw [hR.lists_ne p hp] at hL
      obtain ⟨d', st', an', k, hpk, hk⟩ := hW.list_owner p L hL
      refine ⟨d', st', an', k, ?_, hk⟩
      exact ext_keep hW hb hS hR hpk (by
        simp only [immovable, Block.isPiston, Block.kind, Block.state, Block.moving]
        rcases hk with h | h <;> simp [h]) hp
  · -- list_moving
    intro p L q hL hq
    by_cases hp : p = pos
    · subst hp
      obtain ⟨r, -, -, b, hget, -, -⟩ := hnewlist L hL q hq
      exact ⟨_, hget, by simp⟩
    · rw [hR.lists_ne p hp] at hL
      obtain ⟨b, hqb, hm⟩ := hW.list_moving p L q hL hq
      have hqpos : q ≠ pos := by
        rintro rfl; rw [hb] at hqb; cases hqb; simp [Block.moving] at hm
      exact ⟨b, ext_keep hW hb hS hR hqb (by simp [immovable, hm]) hqpos, hm⟩
  · -- list_disjoint
    intro p p' L L' q hL hL' hq hq'
    -- a cell of the new list is not in an old list
    have key : ∀ (p₁ : Pos) (L₁ : List Pos), p₁ ≠ pos → cx'.st.lists[p₁]? = some L₁ → q ∈ L₁ →
        ∀ L₀, cx'.st.lists[pos]? = some L₀ → q ∈ L₀ → False := by
      intro p₁ L₁ hp₁ hL₁ hq₁ L₀ hL₀ hq₀
      rw [hR.lists_ne p₁ hp₁] at hL₁
      obtain ⟨b, hqb, hm⟩ := hW.list_moving p₁ L₁ q hL₁ hq₁
      obtain ⟨r, hr, hqr, -⟩ := hnewlist L₀ hL₀ _ hq₀
      subst hqr
      have := discover_dest_mem hS hr (by rw [hqb]; rfl)
      exact mw_not_mem_of_immovable (discover_moveOK hS) hqb (by simp [immovable, hm]) this
    by_cases hp : p = pos <;> by_cases hp' : p' = pos
    · rw [hp, hp']
    · exact (key p' L' hp' hL' hq' L (hp ▸ hL) hq).elim
    · exact (key p L hp hL hq L' (hp' ▸ hL') hq').elim
    · rw [hR.lists_ne p hp] at hL; rw [hR.lists_ne p' hp'] at hL'
      exact hW.list_disjoint p p' L L' q hL hL' hq hq'
  · -- moving_piston
    intro p d' st' an' k hp
    rcases ext_cases hW hb hS hR hp with ⟨-, h⟩ | ⟨-, h⟩ | ⟨-, -, h⟩ | ⟨b, -, -, hi, h⟩
    · cases h
    · cases h
    · exact hW.moving_piston p d' st' an' k h
    · exact (Block.startMoving_piston hi h.symm).1
  · -- arm_still
    intro p hp
    rcases ext_cases hW hb hS hR hp with ⟨-, h⟩ | ⟨-, h⟩ | ⟨-, -, h⟩ | ⟨b, -, -, hi, h⟩
    · cases h
    · cases h
    · exact hW.arm_still p h
    · exact Block.startMoving_not_arm hi h.symm
  · -- arm_front
    intro p d' st' an' k mv hp hk
    rcases ext_cases hW hb hS hR hp with ⟨rfl, h⟩ | ⟨-, h⟩ | ⟨hp1, -, h⟩ | ⟨b, -, -, hi, h⟩
    · cases h; rw [hR.get]; simp [Pos.add_ne_self]
    · cases h
    · have harm := hW.arm_front p d' st' an' k mv h hk
      have hne : p.add d' ≠ pos := by rintro he; rw [he, hb] at harm; cases harm
      exact ext_keep hW hb hS hR harm (by simp [immovable, Block.kind]) hne
    · have := (Block.startMoving_piston hi h.symm).1
      rcases hk with h1 | h1 <;> omega
  · -- front_unique
    have hout : ∀ (p : Pos) (d' : Dir) (st' an' : Bool) (k : Fin 4) (mv : Bool),
        cx'.st.get p = some (.piston d' st' an' k mv) → armOut k →
        (p = pos ∧ d' = d) ∨ (p ≠ pos ∧ cx.st.get p = some (.piston d' st' an' k mv)) := by
      intro p d' st' an' k mv hp hk
      rcases ext_cases hW hb hS hR hp with ⟨rfl, h⟩ | ⟨-, h⟩ | ⟨hp1, -, h⟩ | ⟨b, -, -, hi, h⟩
      · cases h; exact Or.inl ⟨rfl, rfl⟩
      · cases h
      · exact Or.inr ⟨hp1, h⟩
      · have := (Block.startMoving_piston hi h.symm).1
        rcases hk with h1 | h1 <;> omega
    intro p p' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 hp hp' hk1 hk2 he
    rcases hout _ _ _ _ _ _ hp hk1 with ⟨rfl, rfl⟩ | ⟨hp1, h1⟩ <;>
      rcases hout _ _ _ _ _ _ hp' hk2 with ⟨rfl, rfl⟩ | ⟨hp2, h2⟩
    · rfl
    · -- the other piston's arm would sit on the front: then the extension failed
      have harm := hW.arm_front p' d2 st2 an2 k2 mv2 h2 hk2
      rw [← he] at harm
      exact absurd (hfront_mov _ harm) (by simp [immovable, Block.kind])
    · have harm := hW.arm_front p d1 st1 an1 k1 mv1 h1 hk1
      rw [he] at harm
      exact absurd (hfront_mov _ harm) (by simp [immovable, Block.kind])
    · exact hW.front_unique p p' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 h1 h2 hk1 hk2 he

end

end FF
