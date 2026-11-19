/-
The row-closure argument with facings allowed per position: `F q f` says a sideways piston facing
`f` may sit at `q`. Needed: `F` depends only on the row, and moving along a sideways facing in use
keeps `F`. Corollary: with no `±Z` sideways pistons, some Z plane must hold sideways pistons
facing both `+Y` and `-Y`.
-/
import Formal.PL1.SideClosure

namespace FF

open Std

/-- `T` is closed under steps of 1 and 2 along every direction in `F`. -/
def Closed3 (T : Int → Int → Prop) (F : Pos → Dir → Prop) : Prop :=
  ∀ (q : Pos) (f : Dir), T q.y q.z → F q f → T (q.add f).y (q.add f).z ∧ T ((q.add f).add f).y ((q.add f).add f).z

/-- What the closure argument needs from `T` and `F`. -/
structure FOK (T : Int → Int → Prop) (F : Pos → Dir → Prop) : Prop where
  closed : Closed3 T F
  row : ∀ q q' e, q'.y = q.y → q'.z = q.z → F q e → F q' e
  move : ∀ p d q f, F p d → F q f → F (q.add d) f ∧ F (q.add d.opp) f

def GoodAt3 (T : Int → Int → Prop) (F : Pos → Dir → Prop) (q : Pos) (e : Dir) : Prop :=
  F q e ∧ T (q.add e).y (q.add e).z ∧ T ((q.add e).add e).y ((q.add e).add e).z

def Good3 (T : Int → Int → Prop) (F : Pos → Dir → Prop) (s : St) : Prop :=
  ∀ q b, s.get q = some b → b.kind = .piston → b.dir = .px ∨ b.dir = .nx ∨ GoodAt3 T F q b.dir

theorem GoodAt3.lane {T : Int → Int → Prop} {F : Pos → Dir → Prop} {q q' : Pos} {e : Dir}
    (hF : FOK T F) (h : GoodAt3 T F q e)
    (hy : q'.y = q.y) (hz : q'.z = q.z) : GoodAt3 T F q' e := by
  refine ⟨hF.row q q' e hy hz h.1, ?_⟩
  have h2 := h.2
  simp only [Pos.add_y, Pos.add_z] at h2 ⊢
  rw [hy, hz]; exact h2

theorem Rel.good3 {T : Int → Int → Prop} {F : Pos → Dir → Prop} {s s' : St} (hF : FOK T F)
    (h : Rel s s') (hs : Good3 T F s) : Good3 T F s' := by
  obtain ⟨σ, hσ, -⟩ := h
  intro q b hq hk
  have hqb : q ∈ s'.body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, hk]⟩
  obtain ⟨r, hr, rfl⟩ := (hσ.body q).mp hqb
  have hsg := hσ.sig r hr
  rw [hq] at hsg
  obtain ⟨l1, l2⟩ := hσ.lane r hr
  cases hb : s.get r with
  | none => rw [hb] at hsg; cases hsg
  | some b0 =>
    rw [hb] at hsg
    simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hsg
    obtain ⟨e1, e2, -⟩ := hsg
    rw [hk] at e1
    have := hs r b0 hb e1.symm
    simp only [hk, e1.symm, ite_true] at e2
    rw [e2]
    rcases this with h1 | h1 | h1
    · exact Or.inl h1
    · exact Or.inr (Or.inl h1)
    · exact Or.inr (Or.inr (h1.lane hF l1 l2))

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {y z : Int}
  {T : Int → Int → Prop} {F : Pos → Dir → Prop}

theorem pl_ext {S : List Pos} (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) (hgp : GoodAt3 T F pos d)
    (hg : Good3 T F cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : RowRel y z cx.st cx'.st ∧ Good3 T F cx'.st := by
  have hlen := discover_length_le hS
  rw [hPL] at hlen
  have hSsub : ∀ r ∈ S, r = pos.add d := by
    intro r hr
    match S, hS, hlen, hr with
    | [r'], hS, _, hr =>
      simp at hr; subst hr
      cases h : cx.st.get (pos.add d) with
      | none => have := discover_empty hS h; simp at this
      | some _ => have := discover_first_mem hS (by rw [h]; rfl); simpa [eq_comm] using this
    | _ :: _ :: _, _, hlen, _ => simp at hlen
  constructor
  · refine rowRel_still fun q hy hz => ?_
    by_cases hqp : q = pos
    · subst hqp; rw [hR.get, hb]; simp; rfl
    · have hq1 : q ≠ pos.add d := by
        rintro rfl; exact hRo (hy ▸ hz ▸ hgp.2.1)
      rw [hR.get, if_neg hqp, if_neg hq1]
      unfold moveWorld
      have hq2 : q.add d.opp ∉ S := by
        intro h
        have := hSsub _ h
        have e : q = (pos.add d).add d := by rw [← this]; simp
        apply hRo
        rw [← hy, ← hz, e]; exact hgp.2.2
      have hq3 : q ∉ S := fun h => hq1 (hSsub q h)
      rw [if_neg hq2, if_neg hq3]
  · intro q b hq hk
    rw [hR.get] at hq
    split at hq
    · rename_i e; subst e
      cases hq
      exact Or.inr (Or.inr hgp)
    · split at hq
      · cases hq; simp [Block.kind] at hk
      · unfold moveWorld at hq
        split at hq
        · rename_i hm
          have e := hSsub _ hm
          cases h0 : cx.st.get (q.add d.opp) with
          | none => rw [h0] at hq; cases hq
          | some b0 =>
            rw [h0] at hq
            simp only [Option.map_some, Option.some.injEq] at hq
            have hs0 := Block.sig_startMoving b0
            rw [hq] at hs0
            simp only [Block.sig, Prod.mk.injEq] at hs0
            obtain ⟨k1, k2, -⟩ := hs0
            rw [hk] at k1
            rcases hg _ b0 h0 k1.symm with h1 | h1 | h1
            · left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
            · right; left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
            · right; right
              simp only [hk, k1.symm, ite_true] at k2
              have hq : q = (pos.add d).add d := by
                have := congrArg (fun p => p.add d) e; simpa using this
              rw [k2]
              have hFq : F q b0.dir := by
                have := (hT.move pos d (q.add d.opp) b0.dir hgp.1 h1.1).1
                rwa [Pos.add_opp_add] at this
              exact ⟨hFq, (hT.closed q _ (hq ▸ hgp.2.2) hFq).1, (hT.closed q _ (hq ▸ hgp.2.2) hFq).2⟩
        · split at hq
          · cases hq
          · exact hg q b hq hk

theorem pl_retract (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) (hgp : GoodAt3 T F pos d)
    (hg : Good3 T F cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    RowRel y z cx.st cx'.st ∧ Good3 T F cx'.st := by
  have hlen := (pulled_length (c := c) (cx := cx) (pos := pos) (d := d) (st := st)).1
  rw [hPL] at hlen
  have hSsub : ∀ r ∈ pulled c cx.st pos d st, r = (pos.add d).add d := by
    intro r hr
    rcases hP : pulled c cx.st pos d st with _ | ⟨r', _ | ⟨r2, rest⟩⟩
    · rw [hP] at hr; simp at hr
    · rw [hP] at hr; simp at hr; subst hr
      have hdisc : discover c (cx.st.remove (pos.add d)) ((pos.add d).add d) d.opp (some pos) true =
          some [r] := by
        rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := d) (st := st) with h | h
        · rw [hP] at h; cases h
        · rw [hP] at h; exact h
      cases h : (cx.st.remove (pos.add d)).get ((pos.add d).add d) with
      | none => have := discover_empty hdisc h; simp at this
      | some _ =>
        have := discover_first_mem hdisc (by rw [h]; rfl)
        simpa [eq_comm] using this
    · rw [hP] at hlen; simp at hlen
  have hW1 : ∀ q, q ≠ pos.add d → (cx.st.remove (pos.add d)).get q = cx.st.get q :=
    fun q hq => St.get_remove_ne (Ne.symm hq)
  constructor
  · refine rowRel_still fun q hy hz => ?_
    by_cases hqp : q = pos
    · subst hqp; rw [hget, if_pos rfl, hb]; rfl
    · have hq1 : q ≠ pos.add d := by
        rintro rfl; exact hRo (hy ▸ hz ▸ hgp.2.1)
      rw [hget, if_neg hqp]
      unfold moveWorld
      have hq2 : q.add d.opp.opp ∉ pulled c cx.st pos d st := by
        intro h
        have := hSsub _ h
        simp only [Dir.opp_opp] at this
        have e : q = pos.add d := by
          have := congrArg (fun p => p.add d.opp) this
          simpa using this
        exact hq1 e
      have hq3 : q ∉ pulled c cx.st pos d st := by
        intro h
        apply hRo
        rw [← hy, ← hz, hSsub q h]; exact hgp.2.2
      rw [if_neg hq2, if_neg hq3, hW1 q hq1]
  · intro q b hq hk
    rw [hget] at hq
    split at hq
    · rename_i e; subst e
      cases hq
      exact Or.inr (Or.inr hgp)
    · unfold moveWorld at hq
      split at hq
      · rename_i hm
        have e := hSsub _ hm
        have hne : q.add d.opp.opp ≠ pos.add d := by rw [e]; exact Pos.add_ne_self _ d
        cases h0 : cx.st.get (q.add d.opp.opp) with
        | none => rw [hW1 _ hne, h0] at hq; cases hq
        | some b0 =>
          rw [hW1 _ hne, h0] at hq
          simp only [Option.map_some, Option.some.injEq] at hq
          have hs0 := Block.sig_startMoving b0
          rw [hq] at hs0
          simp only [Block.sig, Prod.mk.injEq] at hs0
          obtain ⟨k1, k2, -⟩ := hs0
          rw [hk] at k1
          rcases hg _ b0 h0 k1.symm with h1 | h1 | h1
          · left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
          · right; left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
          · right; right
            simp only [hk, k1.symm, ite_true] at k2
            have hq : q = pos.add d := by
              have := congrArg (fun p => p.add d.opp) e; simpa using this
            rw [k2]
            have hFq : F q b0.dir := by
              have := (hT.move pos d (q.add d.opp.opp) b0.dir hgp.1 h1.1).2
              rwa [Pos.add_opp_add] at this
            exact ⟨hFq, (hT.closed q _ (hq ▸ hgp.2.1) hFq).1, (hT.closed q _ (hq ▸ hgp.2.1) hFq).2⟩
      · split at hq
        · cases hq
        · have hqf : q ≠ pos.add d := by
            rintro rfl
            simp at hq
          rw [hW1 q hqf] at hq
          exact hg q b hq hk

theorem turn_pl (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hRo : ¬ T y z) (hT : FOK T F) (hg : Good3 T F cx.st)
    (h : pistonTurn c cx pos = .ok cx') : RowRel y z cx.st cx'.st ∧ Good3 T F cx'.st := by
  have ofRel : Rel cx.st cx'.st → RowRel y z cx.st cx'.st ∧ Good3 T F cx'.st :=
    fun hr => ⟨hr.toRow, hr.good3 hT hg⟩
  have hid : cx' = cx → RowRel y z cx.st cx'.st ∧ Good3 T F cx'.st :=
    fun e => by subst e; exact ⟨(Rel.refl _).toRow, hg⟩
  cases hgt : cx.st.get pos with
  | none => apply hid; unfold pistonTurn at h; rw [hgt] at h; cases h; rfl
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true => apply hid; unfold pistonTurn at h; rw [hgt] at h; cases h; rfl
      | false =>
        have hdir := hg pos _ hgt rfl
        simp only [Block.dir] at hdir
        have hk4 := k.isLt
        rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
          hk | hk | hk | hk
        · obtain rfl : k = 0 := Fin.ext hk
          by_cases hfire : (cx.powered.contains pos || an) = true
          · cases hS : discover c cx.st (pos.add d) d (some pos) false with
            | none =>
              rw [extFail_spec hgt hfire hS] at h; cases h
              exact ofRel (rel_fail hgt)
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hgt hfire hS
              rw [h1] at h; cases h
              by_cases hd : d = .px ∨ d = .nx
              · exact ofRel (rel_ext' hPL hW hd hgt hS hR)
              · push_neg at hd
                rcases hdir with h1 | h1 | h1
                · exact absurd h1 hd.1
                · exact absurd h1 hd.2
                · exact pl_ext hPL hRo hT h1 hg hgt hS hR
          · apply hid
            unfold pistonTurn at h; rw [hgt] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hgt (Or.inl rfl) rfl
          rw [h1] at h; cases h
          exact ofRel (rel_finish hgt h2)
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · apply hid
            unfold pistonTurn at h; rw [hgt] at h
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true] at h
            cases h; rfl
          · obtain ⟨cx1, h1, h2, -⟩ := retract_spec (c := c) hW hgt (Bool.eq_false_iff.mpr hpw)
            rw [h1] at h; cases h
            by_cases hd : d = .px ∨ d = .nx
            · exact ofRel (rel_retract' hPL hW hd hgt h2)
            · push_neg at hd
              rcases hdir with h1 | h1 | h1
              · exact absurd h1 hd.1
              · exact absurd h1 hd.2
              · exact pl_retract hPL hRo hT h1 hg hgt h2
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hgt (Or.inr rfl) rfl
          rw [h1] at h; cases h
          exact ofRel (rel_finish hgt h2)
    | _ => apply hid; unfold pistonTurn at h; rw [hgt] at h; cases h; rfl

end

section
variable {c : Config} {y z : Int} {T : Int → Int → Prop} {F : Pos → Dir → Prop}

theorem turns_pl (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) : ∀ (ps : List Pos) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → Good3 T F cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ Good3 T F cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    obtain ⟨hr1, hx1⟩ := turn_pl hPL hW hRo hT hx h1
    obtain ⟨hr, hW', hL', hx'⟩ := turns_pl hPL hRo hT ps cx1 cx' hE.wf hE.lok hx1 h
    exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem chunks_pl (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) (o : TickOracle) :
    ∀ (order : List Chunk) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st → Good3 T F cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ Good3 T F cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | ch :: order, cx, cx', hW, hL, hx, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1⟩ := turns_pl hPL hRo hT _ cx cx1 hW hL hx hf
      obtain ⟨hr, hW', hL', hx'⟩ := chunks_pl hPL hRo hT o order cx1 cx' hW1 hL1 hx1 h
      exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem tick_pl (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) {o : TickOracle} {s s' : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : Good3 T F s) (h : tick c o s = .ok s') :
    RowRel y z s s' ∧ Good3 T F s' := by
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hr0 : Rel s s0 := rel_tickStart
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
    obtain ⟨hr, -, -, hx'⟩ := chunks_pl hPL hRo hT o order ⟨s0, pw⟩ cx' hW0 hL0 (hr0.good3 hT hx) hfold
    exact ⟨hr0.toRow.trans hr, hx'⟩

theorem stateAt_pl (hPL : c.pushLimit = 1) (hRo : ¬ T y z) (hT : FOK T F) {o : Oracle} {s : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : Good3 T F s) :
    ∀ t, RowRel y z s (stateAt c o s t) ∧ Good3 T F (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨RowRel.refl _, hx⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx'⟩ := tick_pl hPL hRo hT hWt hLt ih.2 h
    exact ⟨ih.1.trans hr, hx'⟩

end




theorem pl1_outside_closure3 {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) {T : Int → Int → Prop} {F : Pos → Dir → Prop} (hT : FOK T F)
    (hg : Good3 T F s) {q0 : Pos} (hq0 : q0 ∈ s.body) (hO : s.tyAt q0 = .O) (hR : ¬ T q0.y q0.z) :
    AlwaysAtMost c s 0 := by
  obtain ⟨B, hB, hBy, hBz, hst⟩ := exists_stuck hq0 hO
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨q0, hq0⟩
  refine alwaysAtMost_zero_of hW hL hN B.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -⟩ := stateAt_pl (o := o) hPL hR hT hW hL hg t
  have hle : (σ B).x ≤ B.x := by
    by_contra h
    exact hst (hmv B hB hBy hBz (by omega))
  exact (keys_x_ge hxm (hσ.mem hB hBy hBz)).trans hle

/-- **With no `±Z` sideways pistons, some Z plane needs sideways pistons facing both `+Y` and
`-Y`.** At push limit 1, if no sideways piston faces `±Z`, there is a sideways piston, and no Z
plane holds both a `+Y` and a `-Y` piston, the machine has speed 0 under every update order. -/
theorem pl1_planes {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) {q1 : Pos} (h1 : IsSide s q1)
    (hnoz : ∀ q d st an k mv, s.get q = some (.piston d st an k mv) → d ≠ .pz ∧ d ≠ .nz)
    (hplane : ∀ q q' st an k mv st' an' k' mv', s.get q = some (.piston .py st an k mv) →
      s.get q' = some (.piston .ny st' an' k' mv') → q.z ≠ q'.z) :
    AlwaysAtMost c s 0 := by
  classical
  set sg : Int → Int := fun z =>
    if ∃ q st an k mv, s.get q = some (.piston .ny st an k mv) ∧ q.z = z then -1 else 1 with hsg
  set φ : Pos → Int := fun q => q.y * sg q.z with hφ
  set SP := s.body.filter (fun q => IsSide s q) with hSP
  have hne : SP.Nonempty := by
    obtain ⟨d, st, an, k, mv, hb, -⟩ := id h1
    exact ⟨q1, Finset.mem_filter.mpr ⟨body_of_piston hb, h1⟩⟩
  obtain ⟨p0, hp0, hmin⟩ := SP.exists_min_image φ hne
  obtain ⟨hp0b, hp0s⟩ := Finset.mem_filter.mp hp0
  set F : Pos → Dir → Prop := fun q f => (f = .py ∨ f = .ny) ∧ f.dy * sg q.z = 1 with hF
  set T : Int → Int → Prop := fun y z => ∃ p, IsSide s p ∧ p.z = z ∧ p.y * sg z + 1 ≤ y * sg z
    with hTdef
  have hstep : ∀ (q : Pos) (f : Dir), F q f → (q.add f).z = q.z ∧
      (q.add f).y * sg (q.add f).z = q.y * sg q.z + 1 := by
    intro q f hf
    obtain ⟨hf1, hf2⟩ := hf
    rcases hf1 with rfl | rfl
    · refine ⟨by simp [Pos.add, Dir.dz], ?_⟩
      simp only [Pos.add_y, Pos.add_z, Dir.dz, add_zero, Dir.dy] at hf2 ⊢
      linear_combination hf2
    · refine ⟨by simp [Pos.add, Dir.dz], ?_⟩
      simp only [Pos.add_y, Pos.add_z, Dir.dz, add_zero, Dir.dy] at hf2 ⊢
      linear_combination hf2
  have hFz : ∀ q f, F q f → ∀ g, F q g → F (q.add f) g ∧ F (q.add f.opp) g := by
    intro q f hf g hg
    obtain ⟨hf1, -⟩ := hf
    have hz1 : (q.add f).z = q.z := by rcases hf1 with rfl | rfl <;> simp [Pos.add, Dir.dz]
    have hz2 : (q.add f.opp).z = q.z := by rcases hf1 with rfl | rfl <;> simp [Pos.add, Dir.dz, Dir.opp]
    exact ⟨⟨hg.1, by rw [hz1]; exact hg.2⟩, ⟨hg.1, by rw [hz2]; exact hg.2⟩⟩
  have hFOK : FOK T F := by
    refine ⟨?_, ?_, ?_⟩
    · intro q f hq hf
      obtain ⟨p, hp, hpz, hle⟩ := hq
      obtain ⟨e1, e2⟩ := hstep q f hf
      have hf' : F (q.add f) f := ⟨hf.1, by rw [e1]; exact hf.2⟩
      obtain ⟨e3, e4⟩ := hstep (q.add f) f hf'
      refine ⟨⟨p, hp, by rw [e1]; exact hpz, ?_⟩, ⟨p, hp, by rw [e3, e1]; exact hpz, ?_⟩⟩
      · rw [e1] at e2 ⊢; rw [e2]; omega
      · rw [e3, e1] at e4 ⊢; rw [e1] at e2; rw [e4, e2]; omega
    · intro q q' e hy hz hq
      exact ⟨hq.1, by rw [hz]; exact hq.2⟩
    · intro p d q f hpd hqf
      have hz1 : (q.add d).z = q.z := by rcases hpd.1 with rfl | rfl <;> simp [Pos.add, Dir.dz]
      have hz2 : (q.add d.opp).z = q.z := by
        rcases hpd.1 with rfl | rfl <;> simp [Pos.add, Dir.dz, Dir.opp]
      exact ⟨⟨hqf.1, by rw [hz1]; exact hqf.2⟩, ⟨hqf.1, by rw [hz2]; exact hqf.2⟩⟩
  have hsideF : ∀ q d st an k mv, s.get q = some (.piston d st an k mv) → d ≠ .px → d ≠ .nx →
      F q d := by
    intro q d st an k mv hq h1 h2
    obtain ⟨h3, h4⟩ := hnoz q d st an k mv hq
    cases d with
    | px => exact absurd rfl h1
    | nx => exact absurd rfl h2
    | pz => exact absurd rfl h3
    | nz => exact absurd rfl h4
    | py =>
      refine ⟨Or.inl rfl, ?_⟩
      have : ¬ ∃ q' st an k mv, s.get q' = some (.piston .ny st an k mv) ∧ q'.z = q.z := by
        rintro ⟨q', st', an', k', mv', hq', hz⟩
        exact hplane q q' st an k mv st' an' k' mv' hq hq' hz.symm
      rw [hsg]; dsimp only; rw [if_neg this]; simp [Dir.dy]
    | ny =>
      refine ⟨Or.inr rfl, ?_⟩
      have : ∃ q' st an k mv, s.get q' = some (.piston .ny st an k mv) ∧ q'.z = q.z :=
        ⟨q, st, an, k, mv, hq, rfl⟩
      rw [hsg]; dsimp only; rw [if_pos this]; simp [Dir.dy]
  have hg : Good3 T F s := by
    intro q b hq hk
    cases b with
    | piston d st an k mv =>
      simp only [Block.dir]
      by_cases hd : d = .px ∨ d = .nx
      · rcases hd with h | h
        · exact Or.inl h
        · exact Or.inr (Or.inl h)
      · push_neg at hd
        right; right
        have hdF := hsideF q d st an k mv hq hd.1 hd.2
        have hside : IsSide s q := ⟨d, st, an, k, mv, hq, hd.1, hd.2⟩
        obtain ⟨e1, e2⟩ := hstep q d hdF
        have hdF' : F (q.add d) d := ⟨hdF.1, by rw [e1]; exact hdF.2⟩
        obtain ⟨e3, e4⟩ := hstep (q.add d) d hdF'
        refine ⟨hdF, ⟨q, hside, e1.symm, ?_⟩, ⟨q, hside, by rw [e3, e1], ?_⟩⟩
        · rw [e1] at e2 ⊢; rw [e2]
        · rw [e3, e1] at e4 ⊢; rw [e1] at e2; rw [e4, e2]; omega
    | plain kk m => cases kk <;> simp [Block.kind] at hk
    | _ => simp [Block.kind] at hk
  have hO : s.tyAt p0 = .O := by
    obtain ⟨d, st, an, k, mv, hb, hd1, hd2⟩ := id hp0s
    rw [tyAt_piston hb]
    cases d <;> first | exact absurd rfl hd1 | exact absurd rfl hd2 | rfl
  have hR : ¬ T p0.y p0.z := by
    rintro ⟨p, hp, hpz, hle⟩
    have hpm := hmin p (Finset.mem_filter.mpr ⟨by
      obtain ⟨d, st, an, k, mv, hb, -⟩ := id hp; exact body_of_piston hb, hp⟩)
    simp only [hφ] at hpm
    rw [hpz] at hpm
    omega
  exact pl1_outside_closure3 hW hL hPL hFOK hg hp0b hO hR

end FF
