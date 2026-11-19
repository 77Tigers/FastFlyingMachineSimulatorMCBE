/-
Counting a class of blocks (by kind, e.g. the pistons): every piston action keeps the
number of blocks of the class, and raises the sum of their X coordinates by at most the
number of class blocks it moved (those now in the acting piston's list).
-/
import Formal.Lemmas.Turn

namespace FF

open Std

/-- The cells holding a block whose kind satisfies `P`. -/
def St.cls (s : St) (P : Kind → Bool) : Finset Pos := s.cellsWith fun _ b => P b.kind

/-- The sum of the X coordinates of those cells. -/
def St.xsum (s : St) (P : Kind → Bool) : Int := ∑ q ∈ s.cls P, q.x

/-- The class cells among the cells of `p`'s list. -/
def St.lcount (s : St) (P : Kind → Bool) (p : Pos) : Nat :=
  ((s.cls P).filter (· ∈ s.list p)).card

theorem St.mem_cls {s : St} {P : Kind → Bool} {q : Pos} :
    q ∈ s.cls P ↔ ∃ b, s.get q = some b ∧ P b.kind = true := by
  unfold St.cls; rw [St.mem_cellsWith]

/-- A move along `d` of the cells `S` maps the class injectively; the X sum rises by at most
the number of class cells among the destinations. -/
theorem cls_shift {s s' : St} {P : Kind → Bool} {S : List Pos} {d : Dir}
    (hdest : ∀ a ∈ S, ∀ b ∈ s.cls P, b ∉ S → a.add d ≠ b)
    (hmem : ∀ q, q ∈ s'.cls P ↔ ∃ r ∈ s.cls P, (if r ∈ S then r.add d else r) = q) :
    (s'.cls P).card = (s.cls P).card ∧
      s'.xsum P ≤ s.xsum P + ((s'.cls P).filter (· ∈ S.map (·.add d))).card := by
  classical
  set σ : Pos → Pos := fun r => if r ∈ S then r.add d else r with hσ
  have hocc : ∀ r ∈ s.cls P, (s.get r).isSome := by
    intro r hr; obtain ⟨b, hb, -⟩ := St.mem_cls.mp hr; simp [hb]
  have hinjOn : Set.InjOn σ (s.cls P) := by
    intro a ha b hb h
    simp only [hσ] at h
    by_cases haS : a ∈ S <;> by_cases hbS : b ∈ S <;> simp only [haS, hbS, ite_true, ite_false] at h
    · exact Pos.add_inj.mp h
    · exact absurd h (hdest a haS b hb hbS)
    · exact absurd h.symm (hdest b hbS a ha haS)
    · exact h
  have himg : s'.cls P = (s.cls P).image σ := by
    ext q; rw [hmem, Finset.mem_image]
  -- the class cells among the destinations are the images of the moved class cells
  have hfil : (s'.cls P).filter (· ∈ S.map (·.add d)) = ((s.cls P).filter (· ∈ S)).image σ := by
    ext q
    simp only [Finset.mem_filter, Finset.mem_image, himg, List.mem_map]
    constructor
    · rintro ⟨⟨r, hr, rfl⟩, ⟨a, haS, ha⟩⟩
      by_cases hrS : r ∈ S
      · exact ⟨r, ⟨hr, hrS⟩, rfl⟩
      · simp only [hσ, hrS, ite_false] at ha
        exact absurd ha (hdest a haS r hr hrS)
    · rintro ⟨r, ⟨hr, hrS⟩, rfl⟩
      exact ⟨⟨r, hr, rfl⟩, ⟨r, hrS, by simp [hσ, hrS]⟩⟩
  refine ⟨by rw [himg, Finset.card_image_of_injOn hinjOn], ?_⟩
  rw [hfil, Finset.card_image_of_injOn (hinjOn.mono (Finset.filter_subset _ _)), St.xsum,
    St.xsum, himg, Finset.sum_image hinjOn]
  have hle : ∀ r ∈ s.cls P, (σ r).x ≤ r.x + (if r ∈ S then 1 else 0) := by
    intro r _
    simp only [hσ]
    split
    · rw [Pos.add_x]; have := Dir.dx_le_one d; omega
    · simp
  calc ∑ r ∈ s.cls P, (σ r).x
      ≤ ∑ r ∈ s.cls P, (r.x + (if r ∈ S then (1 : Int) else 0)) := Finset.sum_le_sum hle
    _ = ∑ r ∈ s.cls P, r.x + (((s.cls P).filter (· ∈ S)).card : Int) := by
        rw [Finset.sum_add_distrib, ← Finset.sum_filter]; simp

theorem list_mem_of_perm {s : St} {p : Pos} {D : List Pos}
    (h : ∀ L, s.lists[p]? = some L → L.Perm D) (hs : D ≠ [] → ∃ L, s.lists[p]? = some L)
    (q : Pos) : q ∈ s.list p ↔ q ∈ D := by
  unfold St.list
  rw [ExtTreeMap.getD_eq_getD_getElem?]
  cases hl : s.lists[p]? with
  | none =>
    by_cases hD : D = []
    · simp [hD]
    · obtain ⟨L, hL⟩ := hs hD; rw [hl] at hL; cases hL
  | some L =>
    simp only [Option.getD_some]
    exact (h L hl).mem_iff

/-! ### Per action -/

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {S : List Pos}
  {P : Kind → Bool}

theorem cls_ext (hP0 : P .arm = false) (hP1 : P .piston = true)
    (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) :
    (cx'.st.cls P).card = (cx.st.cls P).card ∧
      cx'.st.xsum P ≤ cx.st.xsum P + cx'.st.lcount P pos := by
  have hM := discover_moveOK hS
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hb hposI
  have hdest_ne_pos : ∀ r ∈ S, r.add d ≠ pos := by
    intro r hr he
    exact mw_src_not_mem_of_immovable hM hb hposI (by rw [← he, Pos.add_add_opp]; exact hr)
  have hdest_ne_front : ∀ r ∈ S, r.add d ≠ pos.add d := by
    intro r hr he; rw [Pos.add_inj] at he; subst he; exact hposS hr
  have hlc : cx'.st.lcount P pos = ((cx'.st.cls P).filter (· ∈ S.map (·.add d))).card := by
    unfold St.lcount
    congr 1
    apply Finset.filter_congr
    intro q _
    exact list_mem_of_perm hR.lists_pos (fun h => hR.lists_some (by simpa using h)) q
  rw [hlc]
  refine cls_shift (d := d) ?_ ?_
  · intro a haS b hbc hbS he
    obtain ⟨bb, hbb, -⟩ := St.mem_cls.mp hbc
    exact hbS (he ▸ discover_dest_mem hS haS (by rw [he, hbb]; rfl))
  · intro q
    constructor
    · intro hq
      obtain ⟨b', hb', hk⟩ := St.mem_cls.mp hq
      rcases ext_cases hW hb hS hR hb' with ⟨rfl, -⟩ | ⟨-, h⟩ | ⟨-, -, h⟩ | ⟨b, hS', hb'', hi, h⟩
      · exact ⟨q, St.mem_cls.mpr ⟨_, hb, by simpa [Block.kind] using hP1⟩, by simp [hposS]⟩
      · subst h; simp [Block.kind, hP0] at hk
      · refine ⟨q, St.mem_cls.mpr ⟨b', h, hk⟩, ?_⟩
        have : q ∉ S := by
          intro hqS
          obtain ⟨b0, hb0, hi0⟩ := discover_mem hS hqS
          rw [h] at hb0; cases hb0
          have hq1 : q ≠ pos := by rintro rfl; exact hposS hqS
          have hq2 : q ≠ pos.add d := by
            rintro rfl
            rw [hR.get, if_neg (Pos.add_ne_self pos d), if_pos rfl] at hb'
            cases hb'; simp [Block.kind, hP0] at hk
          rw [hR.get, if_neg hq1, if_neg hq2] at hb'
          unfold moveWorld at hb'
          split at hb'
          · cases hsrc : cx.st.get (q.add d.opp) with
            | none => rw [hsrc] at hb'; cases hb'
            | some x =>
              rw [hsrc] at hb'
              simp only [Option.map_some, Option.some.injEq] at hb'
              have hm : b'.moving = true := by rw [← hb']; simp
              simp [immovable, hm] at hi0
          · simp [hqS] at hb'
        simp [this]
      · refine ⟨q.add d.opp, St.mem_cls.mpr ⟨b, hb'', ?_⟩, by simp [hS']⟩
        rw [h, Block.startMoving_kind] at hk; exact hk
    · rintro ⟨r, hr, rfl⟩
      obtain ⟨b, hb', hk⟩ := St.mem_cls.mp hr
      by_cases hrS : r ∈ S
      · simp only [hrS, ite_true]
        refine St.mem_cls.mpr ⟨b.startMoving, ?_, by simpa using hk⟩
        rw [hR.get, if_neg (hdest_ne_pos r hrS), if_neg (hdest_ne_front r hrS), mw_dest hrS, hb']
        rfl
      · simp only [hrS, ite_false]
        by_cases hrp : r = pos
        · subst hrp
          exact St.mem_cls.mpr ⟨.piston d st false 1 false, by rw [hR.get]; simp,
            by simpa [Block.kind] using hP1⟩
        · have hrf : r ≠ pos.add d := by
            rintro rfl; exact hrS (discover_first_mem hS (by rw [hb']; rfl))
          refine St.mem_cls.mpr ⟨b, ?_, hk⟩
          rw [hR.get, if_neg hrp, if_neg hrf]
          unfold moveWorld
          have hsrc : r.add d.opp ∉ S := by
            intro h
            have := discover_dest_mem hS h (by rw [Pos.add_opp_add, hb']; rfl)
            rw [Pos.add_opp_add] at this; exact hrS this
          rw [if_neg hsrc, if_neg hrS, hb']

theorem cls_retract (hP0 : P .arm = false) (hP1 : P .piston = true)
    (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)))
    (hls : pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L) :
    (cx'.st.cls P).card = (cx.st.cls P).card ∧
      cx'.st.xsum P ≤ cx.st.xsum P + cx'.st.lcount P pos := by
  set S := pulled c cx.st pos d st with hS
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hfront : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hW1get : ∀ q, q ≠ pos.add d → W1.get q = cx.st.get q := fun q hq =>
    St.get_remove_ne (Ne.symm hq)
  have hpos1 : W1.get pos = some (.piston d st an 2 false) := by
    rw [hW1get pos (Ne.symm hfront), hb]
  have hposI : immovable (some pos) pos (.piston d st an 2 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hpos1 hposI
  have hfrontS : pos.add d ∉ S := by
    intro h; obtain ⟨b, hb', -⟩ := hM.1 _ h; simp [hW1] at hb'
  have hdest_ne_pos : ∀ r ∈ S, r.add d.opp ≠ pos := by
    intro r hr he
    have : r = pos.add d := by rw [← he]; simp
    exact hfrontS (this ▸ hr)
  have hnf : ∀ q, q ∈ cx.st.cls P → q ≠ pos.add d := by
    intro q hq e
    obtain ⟨b, hb', hk⟩ := St.mem_cls.mp hq
    rw [e, harm] at hb'; cases hb'; simp [Block.kind, hP0] at hk
  have hlc : cx'.st.lcount P pos = ((cx'.st.cls P).filter (· ∈ S.map (·.add d.opp))).card := by
    unfold St.lcount
    congr 1
    apply Finset.filter_congr
    intro q _
    exact list_mem_of_perm hlp (fun h => hls (by simpa using h)) q
  rw [hlc]
  refine cls_shift (d := d.opp) ?_ ?_
  · intro a haS b hbc hbS he
    obtain ⟨bb, hbb, -⟩ := St.mem_cls.mp hbc
    have h1 : W1.get b = some bb := by rw [hW1get b (hnf b hbc), hbb]
    exact hbS (he ▸ hM.2 a haS (by rw [he, h1]; rfl))
  · intro q
    constructor
    · intro hq
      obtain ⟨b', hb', hk⟩ := St.mem_cls.mp hq
      rw [hget] at hb'
      split at hb'
      · rename_i e; subst e
        exact ⟨q, St.mem_cls.mpr ⟨_, hb, by simpa [Block.kind] using hP1⟩, by simp [hposS]⟩
      · rcases mw_cases hM hb' with ⟨h1, hqS, -⟩ | ⟨b, hS', hb'', hi, h⟩
        · have hqf : q ≠ pos.add d := by rintro rfl; simp [hW1] at h1
          refine ⟨q, St.mem_cls.mpr ⟨b', by rw [← hW1get q hqf]; exact h1, hk⟩, by simp [hqS]⟩
        · have hrf : q.add d.opp.opp ≠ pos.add d := by
            rintro e; rw [e] at hS'; exact hfrontS hS'
          refine ⟨q.add d.opp.opp, St.mem_cls.mpr ⟨b, by rw [← hW1get _ hrf]; exact hb'', ?_⟩,
            by rw [if_pos hS']; exact Pos.add_opp_add q d.opp⟩
          rw [h, Block.startMoving_kind] at hk; exact hk
    · rintro ⟨r, hr, rfl⟩
      obtain ⟨b, hb', hk⟩ := St.mem_cls.mp hr
      have hrf := hnf r hr
      by_cases hrS : r ∈ S
      · simp only [hrS, ite_true]
        refine St.mem_cls.mpr ⟨b.startMoving, ?_, by simpa using hk⟩
        rw [hget, if_neg (hdest_ne_pos r hrS), mw_dest hrS, hW1get r hrf, hb']
        rfl
      · simp only [hrS, ite_false]
        by_cases hrp : r = pos
        · subst hrp
          exact St.mem_cls.mpr ⟨.piston d st an 3 false, by rw [hget]; simp,
            by simpa [Block.kind] using hP1⟩
        · refine St.mem_cls.mpr ⟨b, ?_, hk⟩
          rw [hget, if_neg hrp]
          unfold moveWorld
          have h1 : W1.get r = some b := by rw [hW1get r hrf, hb']
          have hsrc : r.add d.opp.opp ∉ S := by
            intro h
            have := hM.2 _ h (by rw [Pos.add_opp_add, h1]; rfl)
            rw [Pos.add_opp_add] at this; exact hrS this
          rw [if_neg hsrc, if_neg hrS, h1]

theorem cls_finish {k next : Fin 4} (hb : cx.st.get pos = some (.piston d st an k false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q) :
    cx'.st.cls P = cx.st.cls P := by
  ext q
  rw [St.mem_cls, St.mem_cls, hget]
  split
  · rename_i e; subst e; simp [hb, Block.kind]
  · split
    · cases cx.st.get q <;> simp
    · rfl

theorem cls_fail (hb : cx.st.get pos = some (.piston d st an 0 false)) :
    (cx.st.set pos (.piston d st true 0 false)).cls P = cx.st.cls P := by
  ext q
  rw [St.mem_cls, St.mem_cls, St.get_set]
  split
  · rename_i e; subst e; simp [hb, Block.kind]
  · rfl

end

end FF
