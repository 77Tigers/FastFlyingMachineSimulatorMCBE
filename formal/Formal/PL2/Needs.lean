/-
At push limit 2 (or 1), slime and honey cannot drag a block from behind the pusher: a push along
`+X` moves only blocks ahead of the pusher, and a pull by a `-X` piston only blocks at least two
cells behind it. So the rearmost layer advances only by pulls of sticky `-X` pistons and the
frontmost only by pushes of `+X` pistons. Hence a flyer at push limit 2 needs both
(`pl2_needs_P`, `pl2_needs_Q`).
-/
import Formal.PL1.Needs

namespace FF

open Std

/-! ### What `expand` can add -/

/-- `q` is added to a moved set by its member `p`: as `p`'s occupied destination, or as a
movable neighbour that slime/honey `p` sticks to. -/
def AddStep (s : St) (dir : Dir) (owner : Option Pos) (p q : Pos) : Prop :=
  ((s.get (p.add dir)).isSome ∧ q = p.add dir) ∨
    (∃ b e nb, s.get p = some b ∧ isGlue b = true ∧ q = p.add e ∧ s.get (p.add e) = some nb ∧
      immovable owner (p.add e) nb = false)

theorem foldl_upper {α : Type} {f : ExtTreeSet Pos → α → ExtTreeSet Pos} (R : α → Pos → Prop)
    (hf : ∀ acc a q, q ∈ f acc a → q ∈ acc ∨ R a q) :
    ∀ (l : List α) (acc : ExtTreeSet Pos) (q : Pos), q ∈ l.foldl f acc → q ∈ acc ∨ ∃ a ∈ l, R a q := by
  intro l
  induction l with
  | nil => intro acc q h; exact Or.inl h
  | cons x xs ih =>
    intro acc q h
    simp only [List.foldl_cons] at h
    rcases ih _ _ h with h1 | ⟨a, ha, h1⟩
    · rcases hf _ _ _ h1 with h2 | h2
      · exact Or.inl h2
      · exact Or.inr ⟨x, by simp, h2⟩
    · exact Or.inr ⟨a, by simp [ha], h1⟩

section
variable {s : St} {dir : Dir} {owner : Option Pos}

theorem mem_adhStep {p : Pos} {b : Block} {acc : ExtTreeSet Pos} {e : Dir} {q : Pos}
    (h : q ∈ adhStep s owner p b acc e) :
    q ∈ acc ∨ (q = p.add e ∧ ∃ nb, s.get (p.add e) = some nb ∧ immovable owner (p.add e) nb = false) := by
  unfold adhStep at h
  split at h
  · rename_i nb hnb
    split at h
    · rename_i hc
      rcases ExtTreeSet.mem_insert_pos.mp h with h | h
      · right
        refine ⟨h.symm, nb, hnb, ?_⟩
        simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
        exact hc.1
      · exact Or.inl h
    · exact Or.inl h
  · exact Or.inl h

theorem mem_adhesion {acc : ExtTreeSet Pos} {p q : Pos} (h : q ∈ adhesion s owner acc p) :
    q ∈ acc ∨ ∃ b e nb, s.get p = some b ∧ isGlue b = true ∧ q = p.add e ∧
      s.get (p.add e) = some nb ∧ immovable owner (p.add e) nb = false := by
  unfold adhesion at h
  split at h
  · rename_i b hb
    split at h
    · rename_i hg
      rcases foldl_upper (f := adhStep s owner p b)
          (fun e q => q = p.add e ∧ ∃ nb, s.get (p.add e) = some nb ∧ immovable owner (p.add e) nb = false)
          (fun _ _ _ h => mem_adhStep h) _ _ _ h with h1 | ⟨e, -, h1, nb, h2, h3⟩
      · exact Or.inl h1
      · exact Or.inr ⟨b, e, nb, hb, hg, h1, h2, h3⟩
    · exact Or.inl h
  · exact Or.inl h

theorem mem_expandStep {acc : ExtTreeSet Pos} {p q : Pos} (h : q ∈ expandStep s dir owner acc p) :
    q ∈ acc ∨ AddStep s dir owner p q := by
  unfold expandStep at h
  dsimp only at h
  split at h
  · rename_i hd
    rcases ExtTreeSet.mem_insert_pos.mp h with h | h
    · exact Or.inr (Or.inl ⟨hd, h.symm⟩)
    · rcases mem_adhesion h with h | h
      · exact Or.inl h
      · exact Or.inr (Or.inr h)
  · rcases mem_adhesion h with h | h
    · exact Or.inl h
    · exact Or.inr (Or.inr h)

theorem mem_expand {S : ExtTreeSet Pos} {q : Pos} (h : q ∈ expand s dir owner S) :
    q ∈ S ∨ ∃ p ∈ S, AddStep s dir owner p q := by
  rw [expand_eq] at h
  rcases foldl_upper (f := expandStep s dir owner) (AddStep s dir owner)
      (fun _ _ _ h => mem_expandStep h) _ _ _ h with h1 | ⟨p, hp, h1⟩
  · exact Or.inl h1
  · exact Or.inr ⟨p, ExtTreeSet.mem_toList.mp hp, h1⟩

end

theorem three_le_size {t : ExtTreeSet Pos} {a b c : Pos} (ha : a ∈ t) (hb : b ∈ t) (hc : c ∈ t)
    (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c) : 3 ≤ t.size := by
  classical
  have hnd : t.toList.Nodup := by
    refine (ExtTreeSet.distinct_toList (t := t)).imp ?_
    intro x y h e; subst e; exact h Std.ReflCmp.compare_self
  rw [← ExtTreeSet.length_toList, ← List.toFinset_card_of_nodup hnd]
  have hsub : ({a, b, c} : Finset Pos) ⊆ t.toList.toFinset := by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_singleton] at hx
    rw [List.mem_toFinset, ExtTreeSet.mem_toList]
    rcases hx with rfl | rfl | rfl <;> assumption
  have := Finset.card_le_card hsub
  rw [Finset.card_insert_of_notMem (by simp [hab, hac]), Finset.card_insert_of_notMem (by simp [hbc]),
    Finset.card_singleton] at this
  exact this

/-! ### The moved set stays on one side, at push limit 2 -/

theorem closure_none_of_big {c : Config} {s : St} {dir : Dir} {owner : Option Pos} :
    ∀ (n : Nat) (S : ExtTreeSet Pos), c.pushLimit < S.size → closure c s dir owner n S = none := by
  intro n S h
  cases n with
  | zero => rfl
  | succ n => unfold closure; rw [if_pos h]

theorem closure_inv {c : Config} {s : St} {dir : Dir} {owner : Option Pos}
    (Inv : ExtTreeSet Pos → Prop)
    (hstep : ∀ S, S.size ≤ c.pushLimit → Inv S →
      Inv (expand s dir owner S) ∨ c.pushLimit < (expand s dir owner S).size) :
    ∀ (n : Nat) (S T : ExtTreeSet Pos), closure c s dir owner n S = some T → Inv S → Inv T := by
  intro n
  induction n with
  | zero => intro S T h; simp [closure] at h
  | succ n ih =>
    intro S T h hS
    unfold closure at h
    split at h
    · cases h
    · rename_i hsz
      dsimp only at h
      split at h
      · cases h; exact hS
      · rcases hstep S (by omega) hS with h1 | h1
        · exact ih _ _ h h1
        · rw [closure_none_of_big n _ h1] at h; cases h

/-- At push limit at most 2, if no block that the first block adds can violate a bound, no
block of the moved set does. -/
theorem discover_bound {c : Config} {s : St} {first : Pos} {dir : Dir} {owner : Option Pos}
    {pulling : Bool} {l : List Pos} (hPL : c.pushLimit ≤ 2) (f : Pos → Int) (lo : Int)
    (hf0 : lo ≤ f first) (hfirst : ∀ q, AddStep s dir owner first q → lo ≤ f q)
    (h : discover c s first dir owner pulling = some l) : ∀ r ∈ l, lo ≤ f r := by
  have key : ∀ T, closure c s dir owner (s.world.size + 1) {first} = some T →
      first ∈ T ∧ ∀ r ∈ T, lo ≤ f r := by
    intro T hT
    refine closure_inv (fun S => first ∈ S ∧ ∀ r ∈ S, lo ≤ f r) ?_ _ _ _ hT
      ⟨by simp, fun r hr => by simp at hr; subst hr; exact hf0⟩
    intro S hsz ⟨hfS, hS⟩
    by_cases hall : ∀ q ∈ expand s dir owner S, lo ≤ f q
    · exact Or.inl ⟨mem_expand_self hfS, hall⟩
    · right
      push_neg at hall
      obtain ⟨q, hq, hlt⟩ := hall
      rcases mem_expand hq with h1 | ⟨p, hp, hstep⟩
      · exact absurd (hS q h1) (by omega)
      · have hpf : p ≠ first := by
          rintro rfl; exact absurd (hfirst q hstep) (by omega)
        have h3 := three_le_size (mem_expand_self hfS) (mem_expand_self hp) hq (Ne.symm hpf)
          (by rintro rfl; omega) (by rintro rfl; have := hS p hp; omega)
        omega
  unfold discover at h
  split at h
  · cases h; simp
  · split at h
    · cases h
    · split at h
      · cases h
      · rename_i T hT
        dsimp only at h
        split at h
        · cases h
        · cases h
          intro r hr
          exact (key T hT).2 r (ExtTreeSet.mem_toList.mp hr)

theorem push_ahead {c : Config} {s : St} {pos : Pos} {S : List Pos} (hPL : c.pushLimit ≤ 2)
    (hS : discover c s (pos.add .px) .px (some pos) false = some S) : ∀ r ∈ S, pos.x < r.x := by
  have := discover_bound (f := fun r => r.x) (lo := pos.x + 1) hPL
    (by simp [Pos.add, Dir.dx]) ?_ hS
  · intro r hr; have := this r hr; omega
  · intro q hq
    rcases hq with ⟨-, rfl⟩ | ⟨b, e, nb, -, -, rfl, hnb, hi⟩
    · simp [Pos.add, Dir.dx]
    · cases e with
      | nx =>
        exfalso
        have : (pos.add .px).add .nx = pos := Pos.add_add_opp pos .px
        rw [this] at hi
        simp [immovable] at hi
      | _ => simp [Pos.add, Dir.dx]

theorem pull_behind {c : Config} {s : St} {pos : Pos} {S : List Pos} (hPL : c.pushLimit ≤ 2)
    (harm : s.get (pos.add .nx) = none)
    (hS : discover c s ((pos.add .nx).add .nx) .px (some pos) true = some S) :
    ∀ r ∈ S, r.x < pos.x := by
  have := discover_bound (f := fun r => -r.x) (lo := 2 - pos.x) hPL
    (by simp [Pos.add, Dir.dx]; omega) ?_ hS
  · intro r hr; have := this r hr; omega
  · intro q hq
    have hback : ((pos.add .nx).add .nx).add .px = pos.add .nx := Pos.add_add_opp _ .nx
    rcases hq with ⟨hd, rfl⟩ | ⟨b, e, nb, -, -, rfl, hnb, hi⟩
    · rw [hback, harm] at hd; cases hd
    · cases e with
      | px => rw [hback, harm] at hnb; cases hnb
      | _ => simp [Pos.add, Dir.dx]; omega

/-! ### Relabellings for moves of up to two blocks -/

/-- `r` could be moved forward: a `+X` piston behind it, or a sticky `-X` piston ahead of it. -/
def HasFwd2 (s : St) (r : Pos) : Prop :=
  (∃ p ∈ s.body, p.x < r.x ∧ s.tyAt p = .P) ∨ (∃ p ∈ s.body, r.x < p.x ∧ s.tyAt p = .Q)

def Rel2 (s s' : St) : Prop :=
  ∃ σ : Pos → Pos, (∀ q, q ∈ s'.body ↔ ∃ r ∈ s.body, σ r = q) ∧
    (∀ r ∈ s.body, (s'.get (σ r)).map Block.sig = (s.get r).map Block.sig) ∧
    (∀ r ∈ s.body, (σ r).x ≤ r.x ∨ ((σ r).x = r.x + 1 ∧ HasFwd2 s r))

theorem rel2_sig {s s' : St} (hs : ∀ q, (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    Rel2 s s' :=
  ⟨id, fun q => by rw [body_iff_of_sig (hs q)]; exact ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩,
    fun q _ => hs q, fun r _ => Or.inl (_root_.le_refl _)⟩

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem rel2_ext {S : List Pos} (hPL : c.pushLimit ≤ 2) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : Rel2 cx.st cx'.st := by
  classical
  have hM := discover_moveOK hS
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hb hposI
  have hdest_ne_pos : ∀ r ∈ S, r.add d ≠ pos := by
    intro r hr he
    exact mw_src_not_mem_of_immovable hM hb hposI (by rw [← he, Pos.add_add_opp]; exact hr)
  have hdest_ne_front : ∀ r ∈ S, r.add d ≠ pos.add d := by
    intro r hr he; rw [Pos.add_inj] at he; subst he; exact hposS hr
  refine ⟨fun r => if r ∈ S then r.add d else r, ext_body hW hb hS hR, ?_, ?_⟩
  · intro r hr
    obtain ⟨br, hbr, -⟩ := St.mem_body.mp hr
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true]
      rw [hR.get, if_neg (hdest_ne_pos r hrS), if_neg (hdest_ne_front r hrS), mw_dest hrS, hbr]
      simp [Block.sig_startMoving]
    · simp only [hrS, ite_false]
      by_cases hrp : r = pos
      · subst hrp; rw [hR.get, hb]; simp; rfl
      · have hrf : r ≠ pos.add d := by
          rintro rfl; exact hrS (discover_first_mem hS (by rw [hbr]; rfl))
        rw [hR.get, if_neg hrp, if_neg hrf]
        unfold moveWorld
        have hsrc : r.add d.opp ∉ S := by
          intro h
          have := hM.2 _ h (by rw [Pos.add_opp_add, hbr]; rfl)
          rw [Pos.add_opp_add] at this; exact hrS this
        rw [if_neg hsrc, if_neg hrS]
  · intro r hr
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true]
      cases d with
      | px =>
        right
        refine ⟨by simp [Pos.add, Dir.dx], Or.inl ⟨pos, body_of_piston hb, ?_, ?_⟩⟩
        · exact push_ahead hPL hS r hrS
        · rw [tyAt_piston hb]; rfl
      | _ => left; simp [Pos.add, Dir.dx]
    · simp only [hrS, ite_false]; exact Or.inl (_root_.le_refl _)

theorem rel2_retract (hPL : c.pushLimit ≤ 2) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)))
    (hls : pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L) :
    Rel2 cx.st cx'.st := by
  classical
  set S := pulled c cx.st pos d st with hSdef
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hfront : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hW1get : ∀ q, q ≠ pos.add d → W1.get q = cx.st.get q := fun q hq =>
    St.get_remove_ne (Ne.symm hq)
  have hfrontS : pos.add d ∉ S := by
    intro h; obtain ⟨b, hb', -⟩ := hM.1 _ h; simp [hW1] at hb'
  have hdest_ne_pos : ∀ r ∈ S, r.add d.opp ≠ pos := by
    intro r hr he
    have : r = pos.add d := by rw [← he]; simp
    exact hfrontS (this ▸ hr)
  have hnf : ∀ q, q ∈ cx.st.body → q ≠ pos.add d := by
    intro q hq e
    obtain ⟨b, hb', hk⟩ := St.mem_body.mp hq
    rw [e, harm] at hb'; cases hb'; exact hk rfl
  refine ⟨fun r => if r ∈ S then r.add d.opp else r, retract_body hW hb hget hlp hls, ?_, ?_⟩
  · intro r hr
    obtain ⟨br, hbr, -⟩ := St.mem_body.mp hr
    have hrf := hnf r hr
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true]
      rw [hget, if_neg (hdest_ne_pos r hrS), mw_dest hrS, hW1get r hrf, hbr]
      simp [Block.sig_startMoving]
    · simp only [hrS, ite_false]
      by_cases hrp : r = pos
      · subst hrp; rw [hget, if_pos rfl, hb]; rfl
      · rw [hget, if_neg hrp]
        unfold moveWorld
        have h1 : W1.get r = some br := by rw [hW1get r hrf, hbr]
        have hsrc : r.add d.opp.opp ∉ S := by
          intro h
          have := hM.2 _ h (by rw [Pos.add_opp_add, h1]; rfl)
          rw [Pos.add_opp_add] at this; exact hrS this
        rw [if_neg hsrc, if_neg hrS, hW1get r hrf]
  · intro r hr
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true]
      cases d with
      | nx =>
        right
        have hst : st = true := by
          cases st
          · simp [hSdef, pulled] at hrS
          · rfl
        subst hst
        refine ⟨by simp [Pos.add, Dir.dx, Dir.opp], Or.inr ⟨pos, body_of_piston hb, ?_, ?_⟩⟩
        · have hdisc : discover c W1 ((pos.add .nx).add .nx) .px (some pos) true = some S := by
            rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := .nx) (st := true) with h | h
            · rw [← hSdef] at h; rw [h] at hrS; simp at hrS
            · exact h
          exact pull_behind hPL (by simp [hW1]) hdisc r hrS
        · rw [tyAt_piston hb]; rfl
      | _ => left; simp [Pos.add, Dir.dx, Dir.opp]
    · simp only [hrS, ite_false]; exact Or.inl (_root_.le_refl _)

theorem turn_rel2 (hPL : c.pushLimit ≤ 2) (hW : Wf cx.st)
    (h : pistonTurn c cx pos = .ok cx') : Rel2 cx.st cx'.st := by
  have hid : cx' = cx → Rel2 cx.st cx'.st := fun e => e ▸ rel2_sig (fun _ => rfl)
  cases hg : cx.st.get pos with
  | none => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl
      | false =>
        have hk4 := k.isLt
        rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
          hk | hk | hk | hk
        · obtain rfl : k = 0 := Fin.ext hk
          by_cases hfire : (cx.powered.contains pos || an) = true
          · cases hS : discover c cx.st (pos.add d) d (some pos) false with
            | none =>
              rw [extFail_spec hg hfire hS] at h; cases h
              refine rel2_sig fun q => ?_
              rw [St.get_set]
              split
              · rename_i e; subst e; rw [hg]; rfl
              · rfl
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              exact rel2_ext hPL hW hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          refine rel2_sig fun q => ?_
          rw [h2]
          split
          · rename_i e; subst e; rw [hg]; rfl
          · split
            · rw [Option.map_map]; congr 1; funext b; simp [Block.sig_finished]
            · rfl
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true] at h
            cases h; rfl
          · obtain ⟨cx1, h1, h2, -, h4, h5, -⟩ := retract_spec (c := c) hW hg
              (Bool.eq_false_iff.mpr hpw)
            rw [h1] at h; cases h
            refine rel2_retract hPL hW hg h2 ?_ (fun h => (h5 h).imp fun _ h' => h'.1)
            intro L hL'
            by_cases hS0 : pulled c cx.st pos d st = []
            · rw [h4 hS0] at hL'; cases hL'
            · obtain ⟨L', hL'', hperm⟩ := h5 hS0
              rw [hL'] at hL''; cases hL''
              exact hperm
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          refine rel2_sig fun q => ?_
          rw [h2]
          split
          · rename_i e; subst e; rw [hg]; rfl
          · split
            · rw [Option.map_map]; congr 1; funext b; simp [Block.sig_finished]
            · rfl
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

/-! ### Invariants, ticks and runs -/

theorem Rel2.noTy {s s' : St} {t : Ty} (h : Rel2 s s') (hn : NoTy t s) : NoTy t s' := by
  obtain ⟨σ, hb, hs, -⟩ := h
  intro q hq
  obtain ⟨r, hr, rfl⟩ := (hb q).mp hq
  have : s'.tyAt (σ r) = s.tyAt r := by unfold St.tyAt; rw [hs r hr]
  rw [this]; exact hn r hr

theorem Rel2.iQ {s s' : St} {m : Int} (h : Rel2 s s') (hI : IQ m s) : IQ m s' := by
  refine ⟨h.noTy hI.1, ?_⟩
  obtain ⟨σ, hb, -, hx⟩ := h
  obtain ⟨q, hq, hqm⟩ := hI.2
  have mem : ∀ r ∈ s.body, σ r ∈ s'.body := fun r hr => (hb _).mpr ⟨r, hr, rfl⟩
  rcases hx q hq with h1 | ⟨h1, hf⟩
  · exact ⟨σ q, mem q hq, by omega⟩
  · rcases hf with ⟨p, hp, hpx, -⟩ | ⟨p, hp, -, hpQ⟩
    · refine ⟨σ p, mem p hp, ?_⟩
      rcases hx p hp with h2 | ⟨h2, -⟩ <;> omega
    · exact absurd hpQ (hI.1 p hp)

theorem Rel2.iP {s s' : St} {M : Int} (h : Rel2 s s') (hI : IP M s) : IP M s' := by
  refine ⟨h.noTy hI.1, ?_⟩
  obtain ⟨σ, hb, -, hx⟩ := h
  intro q hq
  obtain ⟨r, hr, rfl⟩ := (hb q).mp hq
  rcases hx r hr with h1 | ⟨h1, hf⟩
  · have := hI.2 r hr; omega
  · rcases hf with ⟨p, hp, -, hpP⟩ | ⟨p, hp, hpx, -⟩
    · exact absurd hpP (hI.1 p hp)
    · have := hI.2 p hp; omega

theorem Rel2.noPow {s s' : St} (h : Rel2 s s') (hn : NoPow s) : NoPow s' := by
  obtain ⟨σ, hb, hs, -⟩ := h
  intro q b hq
  by_cases harm : b.kind = .arm
  · simp [harm]
  · have hqB : q ∈ s'.body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, harm]⟩
    obtain ⟨r, hr, rfl⟩ := (hb _).mp hqB
    have h1 := hs r hr
    rw [hq] at h1
    cases h2 : s.get r with
    | none => rw [h2] at h1; cases h1
    | some b0 =>
      rw [h2] at h1
      simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at h1
      rw [h1.1]
      exact hn r b0 h2

theorem rel2_tickStart {s : St} : Rel2 s (tickStart s) := by
  refine rel2_sig fun q => ?_
  rw [tickStart_get, Option.map_map]
  congr 1
  funext b
  exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b

section
variable {c : Config} (hPL : c.pushLimit ≤ 2) (I : St → Prop) (hI : ∀ s s', Rel2 s s' → I s → I s')
include hPL hI

theorem turns_pres2 : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st → I cx.st →
    ps.foldlM (pistonTurn c) cx = .ok cx' → Wf cx'.st ∧ ListsOK c cx'.st ∧ I cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    exact turns_pres2 ps cx1 cx' hE.wf hE.lok (hI _ _ (turn_rel2 hPL hW h1) hx) h

theorem chunks_pres2 (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → I cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    Wf cx'.st ∧ ListsOK c cx'.st ∧ I cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨hW, hL, hx⟩
  | ch :: order, cx, cx', hW, hL, hx, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hW1, hL1, hx1⟩ := turns_pres2 hPL I hI _ cx cx1 hW hL hx hf
      exact chunks_pres2 o order cx1 cx' hW1 hL1 hx1 h

theorem tick_pres2 {o : TickOracle} {s s' : St} (hW : Wf s) (hL : ListsOK c s) (hx : I s)
    (h : tick c o s = .ok s') : I s' := by
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hW0 : Wf s0 := tickStart_wf hW
  have hL0 : ListsOK c s0 := tickStart_lok hW hL
  set order := (o.chunks s0 (occupiedChunks c s0)).val with horder
  cases hfold : order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) (⟨s0, pw⟩ : Ctx) with
  | error e =>
    have : tick c o s = .error e := by
      unfold tick
      simp only [bind, Except.bind, pure, Except.pure]
      rw [show clearAngry (powerStage s).1 (powerStage s).2 = s0 from rfl]
      rw [hfold]
    rw [this] at h; cases h
  | ok cx' =>
    have : tick c o s = .ok cx'.st := by
      unfold tick
      simp only [bind, Except.bind, pure, Except.pure]
      rw [show clearAngry (powerStage s).1 (powerStage s).2 = s0 from rfl]
      rw [hfold]
    rw [this] at h; cases h
    exact (chunks_pres2 hPL I hI o order ⟨s0, pw⟩ cx' hW0 hL0 (hI _ _ rel2_tickStart hx) hfold).2.2

theorem stateAt_pres2 {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : I s) :
    ∀ t, I (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact hx
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    exact tick_pres2 hPL I hI hWt hLt ih h

end

/-- Push limit at most 2 without a sticky `-X` piston: speed 0. -/
theorem pl2_needs_Q {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hPL : c.pushLimit ≤ 2)
    (hN : 0 < s.N) (hQ : NoTy .Q s) : AlwaysAtMost c s 0 := by
  obtain ⟨q0, hq0⟩ := Finset.card_pos.mp hN
  refine alwaysAtMost_zero_of hW hL hN q0.x fun o t x hx => ?_
  have := stateAt_pres2 (o := o) hPL (IQ q0.x) (fun _ _ h hI => h.iQ hI) hW hL
    ⟨hQ, q0, hq0, _root_.le_refl _⟩ t
  obtain ⟨q, hq, hqx⟩ := this.2
  exact (keys_x_ge hx hq).trans hqx

/-- Push limit at most 2 without a `+X` piston: speed 0. -/
theorem pl2_needs_P {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hPL : c.pushLimit ≤ 2)
    (hN : 0 < s.N) (hP : NoTy .P s) : AlwaysAtMost c s 0 := by
  classical
  obtain ⟨M, hM'⟩ : ∃ M : Int, ∀ q ∈ s.body, q.x ≤ M :=
    ⟨∑ q ∈ s.body, |q.x|, fun q hq => (le_abs_self _).trans
      (Finset.single_le_sum (f := fun q => |q.x|) (fun _ _ => abs_nonneg _) hq)⟩
  refine alwaysAtMost_zero_of hW hL hN M fun o t x hx => ?_
  have hI := stateAt_pres2 (o := o) hPL (IP M) (fun _ _ h hI => h.iP hI) hW hL ⟨hP, hM'⟩ t
  have hNt : 0 < (stateAt c o s t).N := by
    have hspec := stateAt_spec (o := o) hW hL
    have : ∀ i, (stateAt c o s i).N = s.N := by
      intro i
      induction i with
      | zero => rfl
      | succ i ih => rw [(hspec i).2.2.2.count, ih]
    rw [this]; exact hN
  obtain ⟨q, hq⟩ := Finset.card_pos.mp hNt
  exact (keys_x_ge hx hq).trans (hI.2 q hq)

/-- Push limit at most 2 without a power source: speed 0. -/
theorem pl2_needs_power {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit ≤ 2) (hN : 0 < s.N) (hNP : NoPow s) : AlwaysAtMost c s 0 := by
  refine alwaysAtMost_zero_of hW hL hN ((s.phi + 4 * c.pushLimit * (s.cls isPK).card) / s.N)
    fun o t x hx => ?_
  have hNPt := stateAt_pres2 (o := o) hPL NoPow (fun _ _ h hn => h.noPow hn) hW hL hNP
  have hb := noPow_bounded hW hL hNPt t hx
  have hNi : (0 : Int) < s.N := by exact_mod_cast hN
  rw [Int.le_ediv_iff_mul_le hNi]
  linarith

/-- **What a push limit 2 flyer needs.** At push limit 2 (or 1) a machine has speed 0 under
every update order unless it has a `+X` piston, a sticky `-X` piston and a power source. -/
theorem pl2_flyer_needs {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit ≤ 2) (hN : 0 < s.N) (hmiss : NoTy .P s ∨ NoTy .Q s ∨ NoPow s) :
    AlwaysAtMost c s 0 := by
  rcases hmiss with h | h | h
  · exact pl2_needs_P hW hL hPL hN h
  · exact pl2_needs_Q hW hL hPL hN h
  · exact pl2_needs_power hW hL hPL hN h

end FF
