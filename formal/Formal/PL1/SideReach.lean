/-
Push limit 1: a sideways piston must be able to move another one. A sideways piston at `q`
facing `e` only moves blocks of the rows of `q + e` and `q + 2e`. If no sideways piston has
another sideways piston in those rows (at any X), sideways pistons never change rows, the rows
holding sideways pistons never gain or lose a block, and such a row (it holds a sideways piston,
an `O` block) has a block that never advances (`pl1_needs_side_reach`).
-/
import Formal.PL1.SideRow

namespace FF

open Std

/-- The row of `q` is in `A`, and the rows of `q + e`, `q + 2e` are not. -/
def GoodAt (A : Int → Int → Prop) (q : Pos) (e : Dir) : Prop :=
  A q.y q.z ∧ ¬ A (q.add e).y (q.add e).z ∧ ¬ A ((q.add e).add e).y ((q.add e).add e).z

/-- Every sideways piston lies in a row of `A`, and the rows it reaches do not. -/
def Good (A : Int → Int → Prop) (s : St) : Prop :=
  ∀ q b, s.get q = some b → b.kind = .piston → b.dir = .px ∨ b.dir = .nx ∨ GoodAt A q b.dir

theorem GoodAt.lane {A : Int → Int → Prop} {q q' : Pos} {e : Dir} (h : GoodAt A q e)
    (hy : q'.y = q.y) (hz : q'.z = q.z) : GoodAt A q' e := by
  unfold GoodAt at h ⊢
  simp only [Pos.add_y, Pos.add_z] at h ⊢
  rw [hy, hz]; exact h

theorem Rel.good {A : Int → Int → Prop} {s s' : St} (h : Rel s s') (hs : Good A s) : Good A s' := by
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
    · exact Or.inr (Or.inr (h1.lane l1 l2))

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {y z : Int}
  {A : Int → Int → Prop}

theorem reach_ext {S : List Pos} (hPL : c.pushLimit = 1) (hA : A y z) (hgp : GoodAt A pos d)
    (hg : Good A cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : RowRel y z cx.st cx'.st ∧ Good A cx'.st := by
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
        rintro rfl; exact hgp.2.1 (hy ▸ hz ▸ hA)
      rw [hR.get, if_neg hqp, if_neg hq1]
      unfold moveWorld
      have hq2 : q.add d.opp ∉ S := by
        intro h
        have := hSsub _ h
        have e : q = (pos.add d).add d := by rw [← this]; simp
        apply hgp.2.2
        rw [← e, hy, hz]; exact hA
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
            · exact absurd (e ▸ h1.1) hgp.2.1
        · split at hq
          · cases hq
          · exact hg q b hq hk

theorem reach_retract (hPL : c.pushLimit = 1) (hA : A y z) (hgp : GoodAt A pos d)
    (hg : Good A cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    RowRel y z cx.st cx'.st ∧ Good A cx'.st := by
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
        rintro rfl; exact hgp.2.1 (hy ▸ hz ▸ hA)
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
        apply hgp.2.2
        rw [← hSsub q h, hy, hz]; exact hA
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
          · exact absurd (e ▸ h1.1) hgp.2.2
      · split at hq
        · cases hq
        · have hqf : q ≠ pos.add d := by
            rintro rfl
            simp at hq
          rw [hW1 q hqf] at hq
          exact hg q b hq hk

theorem turn_reach (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hA : A y z) (hg : Good A cx.st)
    (h : pistonTurn c cx pos = .ok cx') : RowRel y z cx.st cx'.st ∧ Good A cx'.st := by
  have ofRel : Rel cx.st cx'.st → RowRel y z cx.st cx'.st ∧ Good A cx'.st :=
    fun hr => ⟨hr.toRow, hr.good hg⟩
  have hid : cx' = cx → RowRel y z cx.st cx'.st ∧ Good A cx'.st :=
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
                · exact reach_ext hPL hA h1 hg hgt hS hR
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
              · exact reach_retract hPL hA h1 hg hgt h2
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hgt (Or.inr rfl) rfl
          rw [h1] at h; cases h
          exact ofRel (rel_finish hgt h2)
    | _ => apply hid; unfold pistonTurn at h; rw [hgt] at h; cases h; rfl

end

section
variable {c : Config} {y z : Int} {A : Int → Int → Prop}

theorem turns_reach (hPL : c.pushLimit = 1) (hA : A y z) : ∀ (ps : List Pos) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → Good A cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ Good A cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    obtain ⟨hr1, hx1⟩ := turn_reach hPL hW hA hx h1
    obtain ⟨hr, hW', hL', hx'⟩ := turns_reach hPL hA ps cx1 cx' hE.wf hE.lok hx1 h
    exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem chunks_reach (hPL : c.pushLimit = 1) (hA : A y z) (o : TickOracle) :
    ∀ (order : List Chunk) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st → Good A cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ Good A cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | ch :: order, cx, cx', hW, hL, hx, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1⟩ := turns_reach hPL hA _ cx cx1 hW hL hx hf
      obtain ⟨hr, hW', hL', hx'⟩ := chunks_reach hPL hA o order cx1 cx' hW1 hL1 hx1 h
      exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem tick_reach (hPL : c.pushLimit = 1) (hA : A y z) {o : TickOracle} {s s' : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : Good A s) (h : tick c o s = .ok s') :
    RowRel y z s s' ∧ Good A s' := by
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
    obtain ⟨hr, -, -, hx'⟩ := chunks_reach hPL hA o order ⟨s0, pw⟩ cx' hW0 hL0 (hr0.good hx) hfold
    exact ⟨hr0.toRow.trans hr, hx'⟩

theorem stateAt_reach (hPL : c.pushLimit = 1) (hA : A y z) {o : Oracle} {s : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : Good A s) :
    ∀ t, RowRel y z s (stateAt c o s t) ∧ Good A (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨RowRel.refl _, hx⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx'⟩ := tick_reach hPL hA hWt hLt ih.2 h
    exact ⟨ih.1.trans hr, hx'⟩

end

/-- A sideways piston at `q`. -/
def IsSide (s : St) (q : Pos) : Prop :=
  ∃ d st an k mv, s.get q = some (.piston d st an k mv) ∧ d ≠ .px ∧ d ≠ .nx

/-- **A push limit 1 flyer needs a sideways piston that can move another sideways piston.** If
there is a sideways piston, and no sideways piston at `p` facing `e` has a sideways piston in the
row of `p + e` or of `p + 2e`, the machine has speed 0 under every update order. -/
theorem pl1_needs_side_reach {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) {q0 : Pos} (hq0 : IsSide s q0)
    (hreach : ∀ p d st an k mv, s.get p = some (.piston d st an k mv) → d ≠ .px → d ≠ .nx →
      ∀ q, IsSide s q → ¬ (q.y = (p.add d).y ∧ q.z = (p.add d).z) ∧
        ¬ (q.y = ((p.add d).add d).y ∧ q.z = ((p.add d).add d).z)) :
    AlwaysAtMost c s 0 := by
  set A : Int → Int → Prop := fun y z => ∃ q, IsSide s q ∧ q.y = y ∧ q.z = z with hAdef
  have hgood : Good A s := by
    intro p b hp hk
    cases b with
    | piston d st an k mv =>
      simp only [Block.dir]
      by_cases hd : d = .px ∨ d = .nx
      · rcases hd with h | h
        · exact Or.inl h
        · exact Or.inr (Or.inl h)
      · push_neg at hd
        right; right
        have hside : IsSide s p := ⟨d, st, an, k, mv, hp, hd.1, hd.2⟩
        refine ⟨⟨p, hside, rfl, rfl⟩, ?_, ?_⟩
        · rintro ⟨q, hq, e1, e2⟩
          exact (hreach p d st an k mv hp hd.1 hd.2 q hq).1 ⟨e1, e2⟩
        · rintro ⟨q, hq, e1, e2⟩
          exact (hreach p d st an k mv hp hd.1 hd.2 q hq).2 ⟨e1, e2⟩
    | plain kk m => cases kk <;> simp [Block.kind] at hk
    | _ => simp [Block.kind] at hk
  obtain ⟨d0, st0, an0, k0, mv0, hb0, hd1, hd2⟩ := hq0
  have hO : s.tyAt q0 = .O := by
    rw [tyAt_piston hb0]; cases d0 <;> simp_all [tyOfSig]
  obtain ⟨B, hB, hBy, hBz, hst⟩ := exists_stuck (body_of_piston hb0) hO
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨q0, body_of_piston hb0⟩
  have hA : A q0.y q0.z := ⟨q0, ⟨d0, st0, an0, k0, mv0, hb0, hd1, hd2⟩, rfl, rfl⟩
  refine alwaysAtMost_zero_of hW hL hN B.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -⟩ := stateAt_reach (o := o) hPL hA hW hL hgood t
  have hle : (σ B).x ≤ B.x := by
    by_contra h
    exact hst (hmv B hB hBy hBz (by omega))
  exact (keys_x_ge hxm (hσ.mem hB hBy hBz)).trans hle


/-- **Unreached rows are stuck.** At push limit 1, if no sideways piston has a sideways piston in
the rows it pushes into or pulls from, then every block that is neither a `+X` piston nor a
sticky `-X` piston (a power source, say) must lie in such a row: otherwise the machine has
speed 0 under every update order. -/
theorem pl1_unreached_row {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1)
    (hstatic : ∀ p d st an k mv, s.get p = some (.piston d st an k mv) → d ≠ .px → d ≠ .nx →
      ∀ q, IsSide s q → ¬ (q.y = (p.add d).y ∧ q.z = (p.add d).z) ∧
        ¬ (q.y = ((p.add d).add d).y ∧ q.z = ((p.add d).add d).z))
    {q0 : Pos} (hq0 : q0 ∈ s.body) (hO : s.tyAt q0 = .O)
    (hun : ∀ p d st an k mv, s.get p = some (.piston d st an k mv) → d ≠ .px → d ≠ .nx →
      ¬ (q0.y = (p.add d).y ∧ q0.z = (p.add d).z) ∧
        ¬ (q0.y = ((p.add d).add d).y ∧ q0.z = ((p.add d).add d).z)) :
    AlwaysAtMost c s 0 := by
  set A : Int → Int → Prop := fun y z => ∀ p d st an k mv,
    s.get p = some (.piston d st an k mv) → d ≠ .px → d ≠ .nx →
      ¬ (y = (p.add d).y ∧ z = (p.add d).z) ∧ ¬ (y = ((p.add d).add d).y ∧ z = ((p.add d).add d).z)
    with hAdef
  have hgood : Good A s := by
    intro p b hp hk
    cases b with
    | piston d st an k mv =>
      simp only [Block.dir]
      by_cases hd : d = .px ∨ d = .nx
      · rcases hd with h | h
        · exact Or.inl h
        · exact Or.inr (Or.inl h)
      · push_neg at hd
        right; right
        have hside : IsSide s p := ⟨d, st, an, k, mv, hp, hd.1, hd.2⟩
        refine ⟨fun p' d' st' an' k' mv' hp' h1 h2 => hstatic p' d' st' an' k' mv' hp' h1 h2 p hside,
          ?_, ?_⟩
        · intro hA'
          exact (hA' p d st an k mv hp hd.1 hd.2).1 ⟨rfl, rfl⟩
        · intro hA'
          exact (hA' p d st an k mv hp hd.1 hd.2).2 ⟨rfl, rfl⟩
    | plain kk m => cases kk <;> simp [Block.kind] at hk
    | _ => simp [Block.kind] at hk
  obtain ⟨B, hB, hBy, hBz, hst⟩ := exists_stuck hq0 hO
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨q0, hq0⟩
  have hA : A q0.y q0.z := fun p d st an k mv hp h1 h2 => hun p d st an k mv hp h1 h2
  refine alwaysAtMost_zero_of hW hL hN B.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -⟩ := stateAt_reach (o := o) hPL hA hW hL hgood t
  have hle : (σ B).x ≤ B.x := by
    by_contra h
    exact hst (hmv B hB hBy hBz (by omega))
  exact (keys_x_ge hxm (hσ.mem hB hBy hBz)).trans hle

end FF
