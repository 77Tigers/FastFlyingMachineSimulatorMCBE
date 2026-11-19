/-
Rows along X at any push limit, for machines whose pistons all face `+X` or `-X` and that have
no slime or honey. Every move is along X and every moved set is closed under occupied
destinations, so each row keeps its blocks in order (a relabelling, `Formal/PL1/Lane.lean`).
Without glue a pull moves exactly one block, so the rearmost block of a row can only be moved
forward by a sticky `-X` piston that is the next block of the row, two cells ahead: in such a
machine, a row whose second block is not a sticky `-X` piston has a rear block that never
advances (`rows_need_Q`).
-/
import Formal.PL2.Needs

namespace FF

open Std

/-- A move of the cells `S` one step along `d = ±X`, closed under occupied destinations, is a
relabelling. -/
theorem relabel_shift {s s' : St} {S : List Pos} {d : Dir} (hd : d = .px ∨ d = .nx)
    (hSb : ∀ r ∈ S, r ∈ s.body)
    (hdest : ∀ r ∈ S, r.add d ∈ s.body → r.add d ∈ S)
    (hmem : ∀ q, q ∈ s'.body ↔ ∃ r ∈ s.body, (if r ∈ S then r.add d else r) = q)
    (hsig : ∀ r ∈ s.body, (s'.get (if r ∈ S then r.add d else r)).map Block.sig =
      (s.get r).map Block.sig) :
    Relabel s s' (fun r => if r ∈ S then r.add d else r) := by
  classical
  obtain ⟨hdy, hdz, hdx⟩ := xdir hd
  refine ⟨hmem, ?_, hsig, ?_, ?_⟩
  · intro a ha b hb e
    split at e <;> split at e
    · exact Pos.add_inj.mp e
    · rename_i h1 h2; exact absurd (hdest a h1 (e ▸ hb)) (e ▸ h2)
    · rename_i h1 h2; exact absurd (hdest b h2 (e.symm ▸ ha)) (e.symm ▸ h1)
    · exact e
  · intro r _
    split
    · rw [Pos.add_y, Pos.add_z, hdy, hdz]; simp
    · exact ⟨rfl, rfl⟩
  · intro a ha b hb ey ez
    have same : ∀ p q : Pos, p.y = q.y → p.z = q.z → p.x = q.x → p = q :=
      fun p q h1 h2 h3 => Pos.eq_of_xyz h3 h1 h2
    have hda : ∀ p : Pos, (p.add d).x = p.x + d.dx := fun p => rfl
    split <;> split
    · rename_i h1 h2; rw [hda, hda]; omega
    · rename_i h1 h2
      rw [hda]
      have hne : b ≠ a.add d := by
        rintro rfl; exact h2 (hdest a h1 hb)
      have hbx : b.x ≠ a.x + d.dx := by
        intro hx; apply hne
        exact same _ _ (by rw [Pos.add_y, hdy]; simp [ey]) (by rw [Pos.add_z, hdz]; simp [ez])
          (by rw [hda]; exact hx)
      have hab : a.x ≠ b.x := by
        intro hx; apply h2; rw [← same a b ey ez hx]; exact h1
      rcases hdx with h | h <;> rw [h] at hbx ⊢ <;> omega
    · rename_i h1 h2
      rw [hda]
      have hne : a ≠ b.add d := by
        rintro rfl; exact h1 (hdest b h2 ha)
      have hax : a.x ≠ b.x + d.dx := by
        intro hx; apply hne
        exact same _ _ (by rw [Pos.add_y, hdy]; simp [ey]) (by rw [Pos.add_z, hdz]; simp [ez])
          (by rw [hda]; exact hx)
      have hab : a.x ≠ b.x := by
        intro hx; apply h1; rw [same a b ey ez hx]; exact h2
      rcases hdx with h | h <;> rw [h] at hax ⊢ <;> omega
    · exact Iff.rfl

/-- The rear block `r` of its row could be moved forward: the block of rank 1 in its row is a
sticky `-X` piston. -/
def RearMover (s : St) (r : Pos) : Prop :=
  ∃ p ∈ s.body, p.y = r.y ∧ p.z = r.z ∧ s.rk p = 1 ∧ s.tyAt p = .Q

def RelR (s s' : St) : Prop :=
  ∃ σ, Relabel s s' σ ∧ ∀ r ∈ s.body, s.rk r = 0 → r.x < (σ r).x → RearMover s r

theorem RelR.refl (s : St) : RelR s s :=
  ⟨id, Relabel.refl s, fun r _ _ h => absurd h (lt_irrefl _)⟩

theorem RelR.trans {s1 s2 s3 : St} (h1 : RelR s1 s2) (h2 : RelR s2 s3) : RelR s1 s3 := by
  obtain ⟨σ, hσ, hm1⟩ := h1
  obtain ⟨τ, hτ, hm2⟩ := h2
  refine ⟨τ ∘ σ, hσ.trans hτ, fun r hr hk hlt => ?_⟩
  by_cases h : r.x < (σ r).x
  · exact hm1 r hr hk h
  · have hk' : s2.rk (σ r) = 0 := by rw [hσ.rk hr, hk]
    obtain ⟨p', hp', hy, hz, hrk, hty⟩ :=
      hm2 _ (hσ.mem hr) hk' (by simp only [Function.comp_apply] at hlt; omega)
    obtain ⟨p, hp, rfl⟩ := (hσ.body p').mp hp'
    obtain ⟨py, pz⟩ := hσ.lane p hp
    obtain ⟨ry, rz⟩ := hσ.lane r hr
    exact ⟨p, hp, by rw [← py, hy, ry], by rw [← pz, hz, rz], by rw [← hσ.rk hp, hrk],
      by rw [← hσ.tyAt hp, hty]⟩

theorem Relabel.xOnly {s s' : St} {σ : Pos → Pos} (hσ : Relabel s s' σ) (hx : XOnly s) :
    XOnly s' := by
  intro q b hq hk
  have hqb : q ∈ s'.body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, hk]⟩
  obtain ⟨r, hr, rfl⟩ := (hσ.body q).mp hqb
  have hs := hσ.sig r hr
  rw [hq] at hs
  cases hb : s.get r with
  | none => rw [hb] at hs; cases hs
  | some b0 =>
    rw [hb] at hs
    simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hs
    obtain ⟨e1, e2, -⟩ := hs
    rw [hk] at e1
    have := hx r b0 hb e1.symm
    simp only [hk, e1.symm, ite_true] at e2
    rw [e2]; exact this

theorem Relabel.noGlue {s s' : St} {σ : Pos → Pos} (hσ : Relabel s s' σ) (hn : NoGlue s) :
    NoGlue s' := by
  intro q b hq
  by_cases harm : b.kind = .arm
  · cases b with
    | plain k m => cases k <;> simp_all [isGlue, Block.kind]
    | _ => simp [Block.kind] at harm
  · have hqB : q ∈ s'.body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, harm]⟩
    obtain ⟨r, hr, rfl⟩ := (hσ.body _).mp hqB
    have h1 := hσ.sig r hr
    rw [hq] at h1
    cases h2 : s.get r with
    | none => rw [h2] at h1; cases h1
    | some b0 =>
      rw [h2] at h1
      simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at h1
      have := hn r b0 h2
      simp only [isGlue] at this ⊢
      rw [h1.1]; exact this


theorem relR_sig {s s' : St} (hs : ∀ q, (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    RelR s s' :=
  ⟨id, { body := fun q => by
            rw [body_iff_of_sig (hs q)]; exact ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩
         inj := fun _ _ _ _ h => h
         sig := fun q _ => hs q
         lane := fun _ _ => ⟨rfl, rfl⟩
         order := fun _ _ _ _ _ _ => Iff.rfl },
    fun r _ _ h => absurd h (lt_irrefl _)⟩

theorem one_le_rk {s : St} {p r : Pos} (hp : p ∈ s.body) (hy : p.y = r.y) (hz : p.z = r.z)
    (hx : p.x < r.x) : 1 ≤ s.rk r := by
  unfold St.rk
  exact Finset.card_pos.mpr ⟨p, Finset.mem_filter.mpr ⟨hp, hy, hz, hx⟩⟩

/-- Without glue, a push along `+X` moves only blocks of the pusher's row, ahead of it. -/
theorem push_row {c : Config} {s : St} {pos : Pos} {S : List Pos} (hG : NoGlue s)
    (hS : discover c s (pos.add .px) .px (some pos) false = some S) :
    ∀ r ∈ S, r.y = pos.y ∧ r.z = pos.z ∧ pos.x < r.x := by
  refine discover_all (fun r => r.y = pos.y ∧ r.z = pos.z ∧ pos.x < r.x)
    (by simp [Pos.add, Dir.dx, Dir.dy, Dir.dz]) ?_ hS
  intro p q hp hq
  rcases hq with ⟨-, rfl⟩ | ⟨b, e, nb, hb, hg, -⟩
  · simp only [Pos.add, Dir.dx, Dir.dy, Dir.dz]; omega
  · rw [hG _ _ hb] at hg; cases hg

/-- Without glue, a pull moves only the block two cells ahead. -/
theorem pull_single {c : Config} {s : St} {pos : Pos} {d : Dir} {S : List Pos} (hG : NoGlue s)
    (harm : s.get (pos.add d) = none)
    (hS : discover c s ((pos.add d).add d) d.opp (some pos) true = some S) :
    ∀ r ∈ S, r = (pos.add d).add d := by
  refine discover_all (fun r => r = (pos.add d).add d) rfl ?_ hS
  intro p q hp hq
  subst hp
  rcases hq with ⟨hd, -⟩ | ⟨b, e, nb, hb, hg, -⟩
  · rw [Pos.add_add_opp, harm] at hd; cases hd
  · rw [hG _ _ hb] at hg; cases hg

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem relR_ext {S : List Pos} (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : RelR cx.st cx'.st := by
  classical
  have hd : d = .px ∨ d = .nx := hx pos _ hb rfl
  have hM := discover_moveOK hS
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hb hposI
  have hdest_ne_pos : ∀ r ∈ S, r.add d ≠ pos := by
    intro r hr he
    exact mw_src_not_mem_of_immovable hM hb hposI (by rw [← he, Pos.add_add_opp]; exact hr)
  have hdest_ne_front : ∀ r ∈ S, r.add d ≠ pos.add d := by
    intro r hr he; rw [Pos.add_inj] at he; subst he; exact hposS hr
  refine ⟨_, relabel_shift hd ?_ ?_ (ext_body hW hb hS hR) ?_, ?_⟩
  · intro r hr
    obtain ⟨b, hb', hi⟩ := discover_mem hS hr
    exact St.mem_body.mpr ⟨b, hb', by simpa [isNonArm] using immovable_arm hi⟩
  · intro r hr hrb
    obtain ⟨b, hb', -⟩ := St.mem_body.mp hrb
    exact hM.2 r hr (by rw [hb']; rfl)
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
  · intro r hr hk hlt
    exfalso
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true, Pos.add_x] at hlt
      rcases hd with rfl | rfl
      · obtain ⟨hy, hz, hxx⟩ := push_row hG hS r hrS
        have := one_le_rk (s := cx.st) (body_of_piston hb) hy.symm hz.symm hxx
        omega
      · simp [Dir.dx] at hlt
    · simp only [hrS, ite_false] at hlt; exact lt_irrefl _ hlt

theorem relR_retract (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)))
    (hls : pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L) :
    RelR cx.st cx'.st := by
  classical
  have hd : d = .px ∨ d = .nx := hx pos _ hb rfl
  have hdo : d.opp = .px ∨ d.opp = .nx := by rcases hd with rfl | rfl <;> simp [Dir.opp]
  set S := pulled c cx.st pos d st with hSdef
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
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
  refine ⟨_, relabel_shift hdo ?_ ?_ (retract_body hW hb hget hlp hls) ?_, ?_⟩
  · intro r hr
    obtain ⟨b, hb', hi⟩ := hM.1 r hr
    have hrf : r ≠ pos.add d := by rintro rfl; exact hfrontS hr
    exact St.mem_body.mpr ⟨b, by rw [← hW1get r hrf]; exact hb', by
      simpa [isNonArm] using immovable_arm hi⟩
  · intro r hr hrb
    obtain ⟨b, hb', -⟩ := St.mem_body.mp hrb
    exact hM.2 r hr (by rw [hW1get _ (hnf _ hrb), hb']; rfl)
  · intro r hr
    obtain ⟨br, hbr, -⟩ := St.mem_body.mp hr
    have hrf := hnf r hr
    by_cases hrS : r ∈ S
    · simp only [show r ∈ pulled c cx.st pos d st from hrS, ite_true]
      rw [hget, if_neg (hdest_ne_pos r hrS), mw_dest hrS, hW1get r hrf, hbr]
      simp [Block.sig_startMoving]
    · simp only [show r ∉ pulled c cx.st pos d st from hrS, ite_false]
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
  · intro r hr hk hlt
    by_cases hrS : r ∈ S
    · simp only [show r ∈ pulled c cx.st pos d st from hrS, ite_true, Pos.add_x] at hlt
      rcases hd with rfl | rfl
      · simp [Dir.dx, Dir.opp] at hlt
      · have hst : st = true := by
          cases st
          · simp [hSdef, pulled] at hrS
          · rfl
        subst hst
        have hdisc : discover c W1 ((pos.add .nx).add .nx) Dir.nx.opp (some pos) true = some S := by
          rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := .nx) (st := true) with h | h
          · rw [← hSdef] at h; rw [h] at hrS; simp at hrS
          · exact h
        have hre := pull_single (noGlue_remove hG _) (by simp [hW1]) hdisc r hrS
        have ey : pos.y = r.y := by rw [hre]; simp [Pos.add, Dir.dy]
        have ez : pos.z = r.z := by rw [hre]; simp [Pos.add, Dir.dz]
        have ex : pos.x = r.x + 2 := by rw [hre]; simp [Pos.add, Dir.dx]; omega
        refine ⟨pos, body_of_piston hb, ey, ez, ?_, ?_⟩
        · have := rk_succ2 (s := cx.st) hr ey ez ex (by
            have : (⟨r.x + 1, r.y, r.z⟩ : Pos) = pos.add .nx :=
              Pos.eq_of_xyz (by simp [Pos.add, Dir.dx]; omega) (by simp [Pos.add, Dir.dy, ey])
                (by simp [Pos.add, Dir.dz, ez])
            rw [this]; exact not_body_of_arm harm)
          omega
        · rw [tyAt_piston hb]; rfl
    · simp only [show r ∉ pulled c cx.st pos d st from hrS, ite_false] at hlt; exact absurd hlt (lt_irrefl _)

theorem turn_relR (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (h : pistonTurn c cx pos = .ok cx') : RelR cx.st cx'.st := by
  have hid : cx' = cx → RelR cx.st cx'.st := fun e => e ▸ RelR.refl _
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
              refine relR_sig fun q => ?_
              rw [St.get_set]
              split
              · rename_i e; subst e; rw [hg]; rfl
              · rfl
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              exact relR_ext hx hG hW hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          refine relR_sig fun q => ?_
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
            refine relR_retract hx hG hW hg h2 ?_ (fun h => (h5 h).imp fun _ h' => h'.1)
            intro L hL'
            by_cases hS0 : pulled c cx.st pos d st = []
            · rw [h4 hS0] at hL'; cases hL'
            · obtain ⟨L', hL'', hperm⟩ := h5 hS0
              rw [hL'] at hL''; cases hL''
              exact hperm
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          refine relR_sig fun q => ?_
          rw [h2]
          split
          · rename_i e; subst e; rw [hg]; rfl
          · split
            · rw [Option.map_map]; congr 1; funext b; simp [Block.sig_finished]
            · rfl
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

/-! ### Ticks and runs -/

section
variable {c : Config}

theorem turns_relR : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st →
    XOnly cx.st → NoGlue cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    RelR cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st ∧ NoGlue cx'.st
  | [], cx, cx', hW, hL, hx, hG, h => by cases h; exact ⟨RelR.refl _, hW, hL, hx, hG⟩
  | p :: ps, cx, cx', hW, hL, hx, hG, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    have hr1 := turn_relR hx hG hW h1
    obtain ⟨σ, hσ, -⟩ := hr1
    obtain ⟨hr, hW', hL', hx', hG'⟩ :=
      turns_relR ps cx1 cx' hE.wf hE.lok (hσ.xOnly hx) (hσ.noGlue hG) h
    exact ⟨(turn_relR hx hG hW h1).trans hr, hW', hL', hx', hG'⟩

theorem chunks_relR (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → XOnly cx.st → NoGlue cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    RelR cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st ∧ NoGlue cx'.st
  | [], cx, cx', hW, hL, hx, hG, h => by cases h; exact ⟨RelR.refl _, hW, hL, hx, hG⟩
  | ch :: order, cx, cx', hW, hL, hx, hG, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1, hG1⟩ := turns_relR _ cx cx1 hW hL hx hG hf
      obtain ⟨hr, hW', hL', hx', hG'⟩ := chunks_relR o order cx1 cx' hW1 hL1 hx1 hG1 h
      exact ⟨hr1.trans hr, hW', hL', hx', hG'⟩

theorem tick_relR {o : TickOracle} {s s' : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) (h : tick c o s = .ok s') : RelR s s' ∧ XOnly s' ∧ NoGlue s' := by
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hr0 : RelR s s0 := relR_sig fun q => by
    rw [hs0, tickStart_get, Option.map_map]
    congr 1
    funext b
    exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b
  obtain ⟨σ0, hσ0, -⟩ := hr0
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
    obtain ⟨hr, -, -, hx', hG'⟩ := chunks_relR o order ⟨s0, pw⟩ cx' hW0 hL0 (hσ0.xOnly hx)
      (hσ0.noGlue hG) hfold
    have hr0 : RelR s s0 := relR_sig fun q => by
      rw [hs0, tickStart_get, Option.map_map]
      congr 1
      funext b
      exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b
    exact ⟨hr0.trans hr, hx', hG'⟩

theorem stateAt_relR {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) : ∀ t, RelR s (stateAt c o s t) ∧ XOnly (stateAt c o s t) ∧
      NoGlue (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨RelR.refl _, hx, hG⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx', hG'⟩ := tick_relR hWt hLt ih.2.1 ih.2.2 h
    exact ⟨ih.1.trans hr, hx', hG'⟩

end

/-- **Rows need a puller.** At any push limit, in a machine with only X-facing pistons and no
slime or honey, if the rear block of some row is not followed in that row by a sticky `-X`
piston (as the row's second block), that rear block never moves forward: speed 0 under every
update order. -/
theorem rows_need_Q {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) {r0 : Pos} (hr0 : r0 ∈ s.body) (hk : s.rk r0 = 0) (hno : ¬ RearMover s r0) :
    AlwaysAtMost c s 0 := by
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨r0, hr0⟩
  refine alwaysAtMost_zero_of hW hL hN r0.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -, -⟩ := stateAt_relR (o := o) hW hL hx hG t
  have hle : (σ r0).x ≤ r0.x := by
    by_contra h
    exact hno (hmv r0 hr0 hk (by omega))
  exact (keys_x_ge hxm (hσ.mem hr0)).trans hle


/-! ### The front of a row -/

/-- `r` is the front block of its row. -/
def Front (s : St) (r : Pos) : Prop := ∀ q ∈ s.body, q.y = r.y → q.z = r.z → q.x ≤ r.x

/-- The front block `r` of its row could be pushed forward: a `+X` piston among the `PL` blocks
just behind it in its row. -/
def FrontMover (PL : Nat) (s : St) (r : Pos) : Prop :=
  ∃ p ∈ s.body, p.y = r.y ∧ p.z = r.z ∧ s.rk p < s.rk r ∧ s.rk r ≤ s.rk p + PL ∧ s.tyAt p = .P

def RelF (PL : Nat) (s s' : St) : Prop :=
  ∃ σ, Relabel s s' σ ∧ ∀ r ∈ s.body, Front s r → r.x < (σ r).x → FrontMover PL s r

theorem Relabel.front {s s' : St} {σ : Pos → Pos} (h : Relabel s s' σ) {r : Pos}
    (hr : r ∈ s.body) (hf : Front s r) : Front s' (σ r) := by
  intro q' hq' hy hz
  obtain ⟨q, hq, rfl⟩ := (h.body q').mp hq'
  obtain ⟨qy, qz⟩ := h.lane q hq
  obtain ⟨ry, rz⟩ := h.lane r hr
  have hy' : q.y = r.y := by rw [← qy, ← ry]; exact hy
  have hz' : q.z = r.z := by rw [← qz, ← rz]; exact hz
  have := hf q hq hy' hz'
  by_contra hlt
  push_neg at hlt
  have := (h.order r hr q hq hy'.symm hz'.symm).mpr hlt
  omega

theorem RelF.refl (PL : Nat) (s : St) : RelF PL s s :=
  ⟨id, Relabel.refl s, fun r _ _ h => absurd h (lt_irrefl _)⟩

theorem RelF.trans {PL : Nat} {s1 s2 s3 : St} (h1 : RelF PL s1 s2) (h2 : RelF PL s2 s3) :
    RelF PL s1 s3 := by
  obtain ⟨σ, hσ, hm1⟩ := h1
  obtain ⟨τ, hτ, hm2⟩ := h2
  refine ⟨τ ∘ σ, hσ.trans hτ, fun r hr hf hlt => ?_⟩
  by_cases h : r.x < (σ r).x
  · exact hm1 r hr hf h
  · obtain ⟨p', hp', hy, hz, hlt1, hle, hty⟩ :=
      hm2 _ (hσ.mem hr) (hσ.front hr hf) (by simp only [Function.comp_apply] at hlt; omega)
    obtain ⟨p, hp, rfl⟩ := (hσ.body p').mp hp'
    obtain ⟨py, pz⟩ := hσ.lane p hp
    obtain ⟨ry, rz⟩ := hσ.lane r hr
    rw [hσ.rk hp, hσ.rk hr] at hlt1 hle
    exact ⟨p, hp, by rw [← py, hy, ry], by rw [← pz, hz, rz], hlt1, hle,
      by rw [← hσ.tyAt hp, hty]⟩

/-- Without glue, a push along `+X` moves an unbroken run of the pusher's row. -/
theorem push_run {c : Config} {s : St} {pos : Pos} {S : List Pos} (hG : NoGlue s)
    (hS : discover c s (pos.add .px) .px (some pos) false = some S) :
    ∀ r ∈ S, r.y = pos.y ∧ r.z = pos.z ∧ pos.x < r.x ∧
      ∀ x', pos.x < x' → x' ≤ r.x → (⟨x', pos.y, pos.z⟩ : Pos) ∈ S := by
  have key : ∀ T, closure c s .px (some pos) (s.world.size + 1) {pos.add .px} = some T →
      ∀ r ∈ T, r.y = pos.y ∧ r.z = pos.z ∧ pos.x < r.x ∧
        ∀ x', pos.x < x' → x' ≤ r.x → (⟨x', pos.y, pos.z⟩ : Pos) ∈ T := by
    intro T hT
    refine closure_inv (fun S => ∀ r ∈ S, r.y = pos.y ∧ r.z = pos.z ∧ pos.x < r.x ∧
        ∀ x', pos.x < x' → x' ≤ r.x → (⟨x', pos.y, pos.z⟩ : Pos) ∈ S) ?_ _ _ _ hT ?_
    · intro S _ hS
      left
      intro q hq
      rcases mem_expand hq with h1 | ⟨p, hp, hst⟩
      · obtain ⟨a, b, c', d'⟩ := hS q h1
        exact ⟨a, b, c', fun x' h1' h2' => mem_expand_self (d' x' h1' h2')⟩
      · rcases hst with ⟨-, rfl⟩ | ⟨b, e, nb, hb, hg, -⟩
        · obtain ⟨a, b', c', d'⟩ := hS p hp
          refine ⟨by simp [Pos.add, Dir.dy, a], by simp [Pos.add, Dir.dz, b'],
            by simp [Pos.add, Dir.dx]; omega, fun x' h1' h2' => ?_⟩
          by_cases hx : x' ≤ p.x
          · exact mem_expand_self (d' x' h1' hx)
          · have : (⟨x', pos.y, pos.z⟩ : Pos) = p.add .px :=
              Pos.eq_of_xyz (by simp [Pos.add, Dir.dx] at h2' ⊢; omega)
                (by simp [Pos.add, Dir.dy, a]) (by simp [Pos.add, Dir.dz, b'])
            rw [this]; exact hq
        · rw [hG _ _ hb] at hg; cases hg
    · intro r hr
      simp at hr; subst hr
      refine ⟨by simp [Pos.add, Dir.dy], by simp [Pos.add, Dir.dz], by simp [Pos.add, Dir.dx],
        fun x' h1 h2 => ?_⟩
      have : (⟨x', pos.y, pos.z⟩ : Pos) = pos.add .px :=
        Pos.eq_of_xyz (by simp [Pos.add, Dir.dx] at h2 ⊢; omega) (by simp [Pos.add, Dir.dy])
          (by simp [Pos.add, Dir.dz])
      rw [this]; simp
  unfold discover at hS
  split at hS
  · cases hS; simp
  · split at hS
    · cases hS
    · split at hS
      · cases hS
      · rename_i T hT
        dsimp only at hS
        split at hS
        · cases hS
        · cases hS
          intro r hr
          obtain ⟨a, b, c', d'⟩ := key T hT r (ExtTreeSet.mem_toList.mp hr)
          exact ⟨a, b, c', fun x' h1 h2 => ExtTreeSet.mem_toList.mpr (d' x' h1 h2)⟩

/-- The rank of `r` is at most the pusher's rank plus the size of the pushed run. -/
theorem rk_le_of_run {s : St} {pos r : Pos} {S : List Pos} (hnd : S.Nodup)
    (hy : r.y = pos.y) (hz : r.z = pos.z) (hr : r ∈ S)
    (hrun : ∀ x', pos.x < x' → x' ≤ r.x → (⟨x', pos.y, pos.z⟩ : Pos) ∈ S) :
    s.rk r ≤ s.rk pos + S.length := by
  classical
  unfold St.rk
  have hsub : s.body.filter (fun p => p.y = r.y ∧ p.z = r.z ∧ p.x < r.x) ⊆
      insert pos (s.body.filter (fun p => p.y = pos.y ∧ p.z = pos.z ∧ p.x < pos.x) ∪
        (S.toFinset.erase r)) := by
    intro q hq
    simp only [Finset.mem_filter] at hq
    obtain ⟨hqb, hqy, hqz, hqx⟩ := hq
    rw [Finset.mem_insert]
    by_cases h : q.x < pos.x
    · exact Or.inr (Finset.mem_union_left _ (Finset.mem_filter.mpr ⟨hqb, hqy.trans hy, hqz.trans hz, h⟩))
    · by_cases h' : q.x = pos.x
      · exact Or.inl (Pos.eq_of_xyz h' (hqy.trans hy) (hqz.trans hz))
      · refine Or.inr (Finset.mem_union_right _ (Finset.mem_erase.mpr ⟨by rintro rfl; omega, ?_⟩))
        rw [List.mem_toFinset]
        have := hrun q.x (by omega) (by omega)
        have e : (⟨q.x, pos.y, pos.z⟩ : Pos) = q :=
          Pos.eq_of_xyz rfl (hqy.trans hy).symm (hqz.trans hz).symm
        rw [e] at this; exact this
  have h1 := (Finset.card_le_card hsub).trans (Finset.card_insert_le _ _)
  have h3 := Finset.card_union_le (s.body.filter (fun p => p.y = pos.y ∧ p.z = pos.z ∧ p.x < pos.x))
    (S.toFinset.erase r)
  have h2 : (S.toFinset.erase r).card = S.length - 1 := by
    rw [Finset.card_erase_of_mem (List.mem_toFinset.mpr hr), List.toFinset_card_of_nodup hnd]
  have hl : 1 ≤ S.length := List.length_pos_of_mem hr
  omega


theorem relF_sig {PL : Nat} {s s' : St}
    (hs : ∀ q, (s'.get q).map Block.sig = (s.get q).map Block.sig) : RelF PL s s' :=
  ⟨id, { body := fun q => by
            rw [body_iff_of_sig (hs q)]; exact ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩
         inj := fun _ _ _ _ h => h
         sig := fun q _ => hs q
         lane := fun _ _ => ⟨rfl, rfl⟩
         order := fun _ _ _ _ _ _ => Iff.rfl },
    fun r _ _ h => absurd h (lt_irrefl _)⟩

theorem rk_lt {s : St} {p r : Pos} (hp : p ∈ s.body) (hy : p.y = r.y) (hz : p.z = r.z)
    (hx : p.x < r.x) : s.rk p < s.rk r := by
  classical
  unfold St.rk
  apply Finset.card_lt_card
  refine ⟨fun q hq => ?_, fun h => ?_⟩
  · simp only [Finset.mem_filter] at hq ⊢
    exact ⟨hq.1, hq.2.1.trans hy, hq.2.2.1.trans hz, by omega⟩
  · have := h (Finset.mem_filter.mpr ⟨hp, hy, hz, hx⟩)
    simp at this

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem relF_ext {S : List Pos} (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : RelF c.pushLimit cx.st cx'.st := by
  classical
  have hd : d = .px ∨ d = .nx := hx pos _ hb rfl
  have hM := discover_moveOK hS
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hb hposI
  have hdest_ne_pos : ∀ r ∈ S, r.add d ≠ pos := by
    intro r hr he
    exact mw_src_not_mem_of_immovable hM hb hposI (by rw [← he, Pos.add_add_opp]; exact hr)
  have hdest_ne_front : ∀ r ∈ S, r.add d ≠ pos.add d := by
    intro r hr he; rw [Pos.add_inj] at he; subst he; exact hposS hr
  refine ⟨_, relabel_shift hd ?_ ?_ (ext_body hW hb hS hR) ?_, ?_⟩
  · intro r hr
    obtain ⟨b, hb', hi⟩ := discover_mem hS hr
    exact St.mem_body.mpr ⟨b, hb', by simpa [isNonArm] using immovable_arm hi⟩
  · intro r hr hrb
    obtain ⟨b, hb', -⟩ := St.mem_body.mp hrb
    exact hM.2 r hr (by rw [hb']; rfl)
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
  · intro r hr hf hlt
    by_cases hrS : r ∈ S
    · simp only [hrS, ite_true, Pos.add_x] at hlt
      rcases hd with rfl | rfl
      · obtain ⟨hy, hz, hxx, hrun⟩ := push_run hG hS r hrS
        have hlen := discover_length_le hS
        refine ⟨pos, body_of_piston hb, hy.symm, hz.symm, rk_lt (body_of_piston hb) hy.symm hz.symm hxx,
          (rk_le_of_run (discover_nodup hS) hy hz hrS hrun).trans (by omega), ?_⟩
        rw [tyAt_piston hb]; rfl
      · simp [Dir.dx] at hlt
    · simp only [hrS, ite_false] at hlt; exact absurd hlt (lt_irrefl _)
theorem relF_retract (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)))
    (hls : pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L) :
    RelF c.pushLimit cx.st cx'.st := by
  classical
  have hd : d = .px ∨ d = .nx := hx pos _ hb rfl
  have hdo : d.opp = .px ∨ d.opp = .nx := by rcases hd with rfl | rfl <;> simp [Dir.opp]
  set S := pulled c cx.st pos d st with hSdef
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
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
  refine ⟨_, relabel_shift hdo ?_ ?_ (retract_body hW hb hget hlp hls) ?_, ?_⟩
  · intro r hr
    obtain ⟨b, hb', hi⟩ := hM.1 r hr
    have hrf : r ≠ pos.add d := by rintro rfl; exact hfrontS hr
    exact St.mem_body.mpr ⟨b, by rw [← hW1get r hrf]; exact hb', by
      simpa [isNonArm] using immovable_arm hi⟩
  · intro r hr hrb
    obtain ⟨b, hb', -⟩ := St.mem_body.mp hrb
    exact hM.2 r hr (by rw [hW1get _ (hnf _ hrb), hb']; rfl)
  · intro r hr
    obtain ⟨br, hbr, -⟩ := St.mem_body.mp hr
    have hrf := hnf r hr
    by_cases hrS : r ∈ S
    · simp only [show r ∈ pulled c cx.st pos d st from hrS, ite_true]
      rw [hget, if_neg (hdest_ne_pos r hrS), mw_dest hrS, hW1get r hrf, hbr]
      simp [Block.sig_startMoving]
    · simp only [show r ∉ pulled c cx.st pos d st from hrS, ite_false]
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
  · intro r hr hf hlt
    exfalso
    by_cases hrS : r ∈ S
    · simp only [show r ∈ pulled c cx.st pos d st from hrS, ite_true, Pos.add_x] at hlt
      rcases hd with rfl | rfl
      · simp [Dir.dx, Dir.opp] at hlt
      · have hst : st = true := by
          cases st
          · simp [hSdef, pulled] at hrS
          · rfl
        subst hst
        have hdisc : discover c W1 ((pos.add .nx).add .nx) Dir.nx.opp (some pos) true = some S := by
          rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := .nx) (st := true) with h | h
          · rw [← hSdef] at h; rw [h] at hrS; simp at hrS
          · exact h
        have hre := pull_single (noGlue_remove hG _) (by simp [hW1]) hdisc r hrS
        have ey : pos.y = r.y := by rw [hre]; simp [Pos.add, Dir.dy]
        have ez : pos.z = r.z := by rw [hre]; simp [Pos.add, Dir.dz]
        have ex : pos.x = r.x + 2 := by rw [hre]; simp [Pos.add, Dir.dx]; omega
        have := hf pos (body_of_piston hb) ey ez
        omega
    · simp only [show r ∉ pulled c cx.st pos d st from hrS, ite_false] at hlt
      exact lt_irrefl _ hlt
theorem turn_relF (hx : XOnly cx.st) (hG : NoGlue cx.st) (hW : Wf cx.st)
    (h : pistonTurn c cx pos = .ok cx') : RelF c.pushLimit cx.st cx'.st := by
  have hid : cx' = cx → RelF c.pushLimit cx.st cx'.st := fun e => e ▸ RelF.refl c.pushLimit _
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
              refine relF_sig fun q => ?_
              rw [St.get_set]
              split
              · rename_i e; subst e; rw [hg]; rfl
              · rfl
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              exact relF_ext hx hG hW hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          refine relF_sig fun q => ?_
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
            refine relF_retract hx hG hW hg h2 ?_ (fun h => (h5 h).imp fun _ h' => h'.1)
            intro L hL'
            by_cases hS0 : pulled c cx.st pos d st = []
            · rw [h4 hS0] at hL'; cases hL'
            · obtain ⟨L', hL'', hperm⟩ := h5 hS0
              rw [hL'] at hL''; cases hL''
              exact hperm
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          refine relF_sig fun q => ?_
          rw [h2]
          split
          · rename_i e; subst e; rw [hg]; rfl
          · split
            · rw [Option.map_map]; congr 1; funext b; simp [Block.sig_finished]
            · rfl
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

/-! ### Ticks and runs -/

section
variable {c : Config}

theorem turns_relF : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st →
    XOnly cx.st → NoGlue cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    RelF c.pushLimit cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st ∧ NoGlue cx'.st
  | [], cx, cx', hW, hL, hx, hG, h => by cases h; exact ⟨RelF.refl c.pushLimit _, hW, hL, hx, hG⟩
  | p :: ps, cx, cx', hW, hL, hx, hG, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    have hr1 := turn_relF hx hG hW h1
    obtain ⟨σ, hσ, -⟩ := hr1
    obtain ⟨hr, hW', hL', hx', hG'⟩ :=
      turns_relF ps cx1 cx' hE.wf hE.lok (hσ.xOnly hx) (hσ.noGlue hG) h
    exact ⟨(turn_relF hx hG hW h1).trans hr, hW', hL', hx', hG'⟩

theorem chunks_relF (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → XOnly cx.st → NoGlue cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    RelF c.pushLimit cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st ∧ NoGlue cx'.st
  | [], cx, cx', hW, hL, hx, hG, h => by cases h; exact ⟨RelF.refl c.pushLimit _, hW, hL, hx, hG⟩
  | ch :: order, cx, cx', hW, hL, hx, hG, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1, hG1⟩ := turns_relF _ cx cx1 hW hL hx hG hf
      obtain ⟨hr, hW', hL', hx', hG'⟩ := chunks_relF o order cx1 cx' hW1 hL1 hx1 hG1 h
      exact ⟨hr1.trans hr, hW', hL', hx', hG'⟩

theorem tick_relF {o : TickOracle} {s s' : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) (h : tick c o s = .ok s') : RelF c.pushLimit s s' ∧ XOnly s' ∧ NoGlue s' := by
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hr0 : RelF c.pushLimit s s0 := relF_sig fun q => by
    rw [hs0, tickStart_get, Option.map_map]
    congr 1
    funext b
    exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b
  obtain ⟨σ0, hσ0, -⟩ := hr0
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
    obtain ⟨hr, -, -, hx', hG'⟩ := chunks_relF o order ⟨s0, pw⟩ cx' hW0 hL0 (hσ0.xOnly hx)
      (hσ0.noGlue hG) hfold
    have hr0 : RelF c.pushLimit s s0 := relF_sig fun q => by
      rw [hs0, tickStart_get, Option.map_map]
      congr 1
      funext b
      exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b
    exact ⟨hr0.trans hr, hx', hG'⟩

theorem stateAt_relF {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) : ∀ t, RelF c.pushLimit s (stateAt c o s t) ∧ XOnly (stateAt c o s t) ∧
      NoGlue (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨RelF.refl c.pushLimit _, hx, hG⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx', hG'⟩ := tick_relF hWt hLt ih.2.1 ih.2.2 h
    exact ⟨ih.1.trans hr, hx', hG'⟩

end

/-- **Rows need a pusher.** At any push limit, with only X-facing pistons and no slime or honey,
if none of the `PL` blocks just behind the front block of some row is a `+X` piston, that front
block never moves forward: speed 0 under every update order. -/
theorem rows_need_P {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : XOnly s)
    (hG : NoGlue s) {r0 : Pos} (hr0 : r0 ∈ s.body) (hf : Front s r0)
    (hno : ¬ FrontMover c.pushLimit s r0) : AlwaysAtMost c s 0 := by
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨r0, hr0⟩
  refine alwaysAtMost_zero_of hW hL hN r0.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -, -⟩ := stateAt_relF (o := o) hW hL hx hG t
  have hle : (σ r0).x ≤ r0.x := by
    by_contra h
    exact hno (hmv r0 hr0 hf (by omega))
  exact (keys_x_ge hxm (hσ.mem hr0)).trans hle

end FF
