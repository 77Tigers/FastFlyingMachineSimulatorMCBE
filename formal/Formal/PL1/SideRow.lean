/-
Push limit 1: sideways pistons in a single row do not help. A sideways piston facing `e` only
ever moves blocks between the rows `+e` and `+2e` from its own, never into or out of its own
row. So if every sideways piston sits in the row `(y, z)`, that row keeps its blocks and their
order forever, and a block of it that is neither a `+X` piston nor a sticky `-X` piston (for
instance a sideways piston) forces a block of the row that never advances (`chain_stuck`).
Hence a push limit 1 flyer needs sideways pistons in at least two rows.
-/
import Formal.PL1.Needs

namespace FF

open Std

/-- Every sideways piston lies in the row `(y, z)`. -/
def SideRow (y z : Int) (s : St) : Prop :=
  ∀ q b, s.get q = some b → b.kind = .piston → b.dir = .px ∨ b.dir = .nx ∨ (q.y = y ∧ q.z = z)

/-- A relabelling of the blocks of row `(y, z)` only. -/
structure RowLab (y z : Int) (s s' : St) (σ : Pos → Pos) : Prop where
  body : ∀ q, (q ∈ s'.body ∧ q.y = y ∧ q.z = z) ↔ ∃ r ∈ s.body, r.y = y ∧ r.z = z ∧ σ r = q
  inj : ∀ a ∈ s.body, ∀ b ∈ s.body, a.y = y → a.z = z → b.y = y → b.z = z → σ a = σ b → a = b
  sig : ∀ r ∈ s.body, r.y = y → r.z = z → (s'.get (σ r)).map Block.sig = (s.get r).map Block.sig
  lane : ∀ r ∈ s.body, r.y = y → r.z = z → (σ r).y = y ∧ (σ r).z = z
  order : ∀ a ∈ s.body, ∀ b ∈ s.body, a.y = y → a.z = z → b.y = y → b.z = z →
    (a.x < b.x ↔ (σ a).x < (σ b).x)

def RowRel (y z : Int) (s s' : St) : Prop :=
  ∃ σ, RowLab y z s s' σ ∧ ∀ r ∈ s.body, r.y = y → r.z = z → r.x < (σ r).x → HasMover s r

section
variable {y z : Int}

theorem RowLab.mem {s s' : St} {σ : Pos → Pos} (h : RowLab y z s s' σ) {r : Pos} (hr : r ∈ s.body)
    (hy : r.y = y) (hz : r.z = z) : σ r ∈ s'.body := ((h.body _).mpr ⟨r, hr, hy, hz, rfl⟩).1

theorem RowLab.tyAt {s s' : St} {σ : Pos → Pos} (h : RowLab y z s s' σ) {r : Pos}
    (hr : r ∈ s.body) (hy : r.y = y) (hz : r.z = z) : s'.tyAt (σ r) = s.tyAt r := by
  unfold St.tyAt; rw [h.sig r hr hy hz]

theorem RowLab.rk {s s' : St} {σ : Pos → Pos} (h : RowLab y z s s' σ) {r : Pos}
    (hr : r ∈ s.body) (hy : r.y = y) (hz : r.z = z) : s'.rk (σ r) = s.rk r := by
  classical
  obtain ⟨ly, lz⟩ := h.lane r hr hy hz
  have himg : s'.body.filter (fun p => p.y = y ∧ p.z = z) =
      (s.body.filter (fun p => p.y = y ∧ p.z = z)).image σ := by
    ext q
    rw [Finset.mem_filter, Finset.mem_image, h.body]
    constructor
    · rintro ⟨p, hp, h1, h2, rfl⟩; exact ⟨p, Finset.mem_filter.mpr ⟨hp, h1, h2⟩, rfl⟩
    · rintro ⟨p, hp, rfl⟩
      obtain ⟨hp, h1, h2⟩ := Finset.mem_filter.mp hp
      exact ⟨p, hp, h1, h2, rfl⟩
  unfold St.rk
  rw [ly, lz, hy, hz]
  have e1 : s'.body.filter (fun p => p.y = y ∧ p.z = z ∧ p.x < (σ r).x) =
      (s'.body.filter (fun p => p.y = y ∧ p.z = z)).filter (fun p => p.x < (σ r).x) := by
    rw [Finset.filter_filter]; congr 1; funext p; simp [and_assoc]
  have e2 : s.body.filter (fun p => p.y = y ∧ p.z = z ∧ p.x < r.x) =
      (s.body.filter (fun p => p.y = y ∧ p.z = z)).filter (fun p => p.x < r.x) := by
    rw [Finset.filter_filter]; congr 1; funext p; simp [and_assoc]
  rw [e1, e2, himg, Finset.filter_image, Finset.card_image_of_injOn]
  · congr 1
    apply Finset.filter_congr
    intro p hp
    obtain ⟨hp, h1, h2⟩ := Finset.mem_filter.mp hp
    exact (h.order p hp r hr h1 h2 hy hz).symm
  · intro a ha b hb e
    obtain ⟨ha, a1, a2⟩ := Finset.mem_filter.mp (Finset.mem_filter.mp ha).1
    obtain ⟨hb, b1, b2⟩ := Finset.mem_filter.mp (Finset.mem_filter.mp hb).1
    exact h.inj a ha b hb a1 a2 b1 b2 e

theorem RowRel.trans {s1 s2 s3 : St} (h1 : RowRel y z s1 s2) (h2 : RowRel y z s2 s3) :
    RowRel y z s1 s3 := by
  obtain ⟨σ, hσ, hm1⟩ := h1
  obtain ⟨τ, hτ, hm2⟩ := h2
  refine ⟨τ ∘ σ, ⟨?_, ?_, ?_, ?_, ?_⟩, ?_⟩
  · intro q
    rw [hτ.body]
    constructor
    · rintro ⟨r', hr', h1, h2, rfl⟩
      obtain ⟨r, hr, e1, e2, rfl⟩ := (hσ.body r').mp ⟨hr', h1, h2⟩
      exact ⟨r, hr, e1, e2, rfl⟩
    · rintro ⟨r, hr, e1, e2, rfl⟩
      obtain ⟨l1, l2⟩ := hσ.lane r hr e1 e2
      exact ⟨σ r, hσ.mem hr e1 e2, l1, l2, rfl⟩
  · intro a ha b hb a1 a2 b1 b2 e
    obtain ⟨la1, la2⟩ := hσ.lane a ha a1 a2
    obtain ⟨lb1, lb2⟩ := hσ.lane b hb b1 b2
    exact hσ.inj a ha b hb a1 a2 b1 b2
      (hτ.inj _ (hσ.mem ha a1 a2) _ (hσ.mem hb b1 b2) la1 la2 lb1 lb2 e)
  · intro r hr e1 e2
    obtain ⟨l1, l2⟩ := hσ.lane r hr e1 e2
    exact (hτ.sig _ (hσ.mem hr e1 e2) l1 l2).trans (hσ.sig r hr e1 e2)
  · intro r hr e1 e2
    obtain ⟨l1, l2⟩ := hσ.lane r hr e1 e2
    exact hτ.lane _ (hσ.mem hr e1 e2) l1 l2
  · intro a ha b hb a1 a2 b1 b2
    obtain ⟨la1, la2⟩ := hσ.lane a ha a1 a2
    obtain ⟨lb1, lb2⟩ := hσ.lane b hb b1 b2
    exact (hσ.order a ha b hb a1 a2 b1 b2).trans
      (hτ.order _ (hσ.mem ha a1 a2) _ (hσ.mem hb b1 b2) la1 la2 lb1 lb2)
  · intro r hr e1 e2 hlt
    by_cases h : r.x < (σ r).x
    · exact hm1 r hr e1 e2 h
    · obtain ⟨l1, l2⟩ := hσ.lane r hr e1 e2
      obtain ⟨p', hp', hy, hz, hk⟩ :=
        hm2 _ (hσ.mem hr e1 e2) l1 l2 (by simp only [Function.comp_apply] at hlt; omega)
      have hpy : p'.y = y := hy.trans l1
      have hpz : p'.z = z := hz.trans l2
      obtain ⟨p, hp, p1, p2, rfl⟩ := (hσ.body p').mp ⟨hp', hpy, hpz⟩
      refine ⟨p, hp, p1.trans e1.symm, p2.trans e2.symm, ?_⟩
      rw [hσ.rk hp p1 p2, hσ.rk hr e1 e2, hσ.tyAt hp p1 p2] at hk
      exact hk

theorem Rel.toRow {s s' : St} (h : Rel s s') : RowRel y z s s' := by
  obtain ⟨σ, hσ, hm⟩ := h
  refine ⟨σ, ⟨?_, fun a ha b hb _ _ _ _ e => hσ.inj a ha b hb e, fun r hr _ _ => hσ.sig r hr,
    fun r hr e1 e2 => by obtain ⟨l1, l2⟩ := hσ.lane r hr; exact ⟨l1.trans e1, l2.trans e2⟩,
    fun a ha b hb a1 a2 b1 b2 => hσ.order a ha b hb (a1.trans b1.symm) (a2.trans b2.symm)⟩,
    fun r hr _ _ hlt => hm r hr hlt⟩
  intro q
  rw [hσ.body]
  constructor
  · rintro ⟨⟨r, hr, rfl⟩, h1, h2⟩
    obtain ⟨l1, l2⟩ := hσ.lane r hr
    exact ⟨r, hr, l1 ▸ h1, l2 ▸ h2, rfl⟩
  · rintro ⟨r, hr, e1, e2, rfl⟩
    obtain ⟨l1, l2⟩ := hσ.lane r hr
    exact ⟨⟨r, hr, rfl⟩, l1.trans e1, l2.trans e2⟩

/-- Nothing in the row changes but state bits. -/
theorem rowRel_still {s s' : St}
    (hs : ∀ q, q.y = y → q.z = z → (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    RowRel y z s s' := by
  refine ⟨id, ⟨?_, fun _ _ _ _ _ _ _ _ e => e, fun r _ e1 e2 => hs r e1 e2,
    fun _ _ e1 e2 => ⟨e1, e2⟩, fun _ _ _ _ _ _ _ _ => Iff.rfl⟩,
    fun r _ _ _ h => absurd h (lt_irrefl _)⟩
  intro q
  constructor
  · rintro ⟨hq, h1, h2⟩
    exact ⟨q, (body_iff_of_sig (hs q h1 h2)).mp hq, h1, h2, rfl⟩
  · rintro ⟨r, hr, e1, e2, rfl⟩
    exact ⟨(body_iff_of_sig (hs r e1 e2)).mpr hr, e1, e2⟩

theorem Rel.sideRow {s s' : St} (h : Rel s s') (hs : SideRow y z s) : SideRow y z s' := by
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
    rw [e2, l1, l2]; exact this

end

theorem off_row1 {p : Pos} {d : Dir} (hd : d ≠ .px ∧ d ≠ .nx) :
    ¬ ((p.add d).y = p.y ∧ (p.add d).z = p.z) := by
  cases d <;> simp_all [Pos.add, Dir.dy, Dir.dz]

theorem off_row2 {p : Pos} {d : Dir} (hd : d ≠ .px ∧ d ≠ .nx) :
    ¬ (((p.add d).add d).y = p.y ∧ ((p.add d).add d).z = p.z) := by
  cases d <;> simp_all [Pos.add, Dir.dy, Dir.dz] <;> omega

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {y z : Int}

theorem side_ext {S : List Pos} (hPL : c.pushLimit = 1) (hd : d ≠ .px ∧ d ≠ .nx)
    (hrow : pos.y = y ∧ pos.z = z) (hsr : SideRow y z cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : RowRel y z cx.st cx'.st ∧ SideRow y z cx'.st := by
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
  have hpd : pos.add d ≠ pos := Pos.add_ne_self pos d
  constructor
  · refine rowRel_still fun q hy hz => ?_
    by_cases hqp : q = pos
    · subst hqp; rw [hR.get, hb]; simp; rfl
    · have hq1 : q ≠ pos.add d := by
        rintro rfl; exact off_row1 hd ⟨hy.trans hrow.1.symm, hz.trans hrow.2.symm⟩
      rw [hR.get, if_neg hqp, if_neg hq1]
      unfold moveWorld
      have hq2 : q.add d.opp ∉ S := by
        intro h
        have := hSsub _ h
        have e : q = (pos.add d).add d := by rw [← this]; simp
        apply off_row2 (p := pos) (d := d) hd
        rw [← e]; exact ⟨hy.trans hrow.1.symm, hz.trans hrow.2.symm⟩
      have hq3 : q ∉ S := fun h => hq1 (hSsub q h)
      rw [if_neg hq2, if_neg hq3]
  · intro q b hq hk
    by_cases hin : q.y = y ∧ q.z = z
    · exact Or.inr (Or.inr hin)
    · rw [hR.get] at hq
      split at hq
      · rename_i e; subst e; exact absurd hrow hin
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
              have hoff : ¬ ((q.add d.opp).y = y ∧ (q.add d.opp).z = z) := by
                rw [e]; intro hh; exact off_row1 hd ⟨hh.1.trans hrow.1.symm, hh.2.trans hrow.2.symm⟩
              rcases hsr _ b0 h0 k1.symm with h1 | h1 | h1
              · left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
              · right; left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
              · exact absurd h1 hoff
          · split at hq
            · cases hq
            · exact hsr q b hq hk

theorem side_retract (hPL : c.pushLimit = 1) (hd : d ≠ .px ∧ d ≠ .nx)
    (hrow : pos.y = y ∧ pos.z = z) (hsr : SideRow y z cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    RowRel y z cx.st cx'.st ∧ SideRow y z cx'.st := by
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
        rintro rfl; exact off_row1 hd ⟨hy.trans hrow.1.symm, hz.trans hrow.2.symm⟩
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
        apply off_row2 (p := pos) (d := d) hd
        rw [← hSsub q h]; exact ⟨hy.trans hrow.1.symm, hz.trans hrow.2.symm⟩
      rw [if_neg hq2, if_neg hq3, hW1 q hq1]
  · intro q b hq hk
    by_cases hin : q.y = y ∧ q.z = z
    · exact Or.inr (Or.inr hin)
    · rw [hget] at hq
      split at hq
      · rename_i e; subst e; exact absurd hrow hin
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
            have hoff : ¬ ((q.add d.opp.opp).y = y ∧ (q.add d.opp.opp).z = z) := by
              rw [e]; intro hh; exact off_row2 hd ⟨hh.1.trans hrow.1.symm, hh.2.trans hrow.2.symm⟩
            rcases hsr _ b0 h0 k1.symm with h1 | h1 | h1
            · left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
            · right; left; simp only [hk, k1.symm, ite_true] at k2; rw [k2]; exact h1
            · exact absurd h1 hoff
        · split at hq
          · cases hq
          · have hqf : q ≠ pos.add d := by
              rintro rfl
              simp at hq
            rw [hW1 q hqf] at hq
            exact hsr q b hq hk

end


section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {y z : Int}

theorem turn_row (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hsr : SideRow y z cx.st)
    (h : pistonTurn c cx pos = .ok cx') : RowRel y z cx.st cx'.st ∧ SideRow y z cx'.st := by
  have ofRel : Rel cx.st cx'.st → RowRel y z cx.st cx'.st ∧ SideRow y z cx'.st :=
    fun hr => ⟨hr.toRow, hr.sideRow hsr⟩
  have hid : cx' = cx → RowRel y z cx.st cx'.st ∧ SideRow y z cx'.st :=
    fun e => by subst e; exact ⟨(Rel.refl _).toRow, hsr⟩
  cases hg : cx.st.get pos with
  | none => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl
      | false =>
        have hdir := hsr pos _ hg rfl
        have hk4 := k.isLt
        rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
          hk | hk | hk | hk
        · obtain rfl : k = 0 := Fin.ext hk
          by_cases hfire : (cx.powered.contains pos || an) = true
          · cases hS : discover c cx.st (pos.add d) d (some pos) false with
            | none =>
              rw [extFail_spec hg hfire hS] at h; cases h
              exact ofRel (rel_fail hg)
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              by_cases hd : d = .px ∨ d = .nx
              · exact ofRel (rel_ext' hPL hW hd hg hS hR)
              · push_neg at hd
                rcases hdir with h1 | h1 | h1
                · exact absurd h1 hd.1
                · exact absurd h1 hd.2
                · exact side_ext hPL hd h1 hsr hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          exact ofRel (rel_finish hg h2)
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true] at h
            cases h; rfl
          · obtain ⟨cx1, h1, h2, -⟩ := retract_spec (c := c) hW hg (Bool.eq_false_iff.mpr hpw)
            rw [h1] at h; cases h
            by_cases hd : d = .px ∨ d = .nx
            · exact ofRel (rel_retract' hPL hW hd hg h2)
            · push_neg at hd
              rcases hdir with h1 | h1 | h1
              · exact absurd h1 hd.1
              · exact absurd h1 hd.2
              · exact side_retract hPL hd h1 hsr hg h2
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          exact ofRel (rel_finish hg h2)
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

section
variable {c : Config} {y z : Int}

theorem RowRel.refl (s : St) : RowRel y z s s := (Rel.refl s).toRow

theorem turns_row (hPL : c.pushLimit = 1) : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st →
    ListsOK c cx.st → SideRow y z cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ SideRow y z cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    obtain ⟨hr1, hx1⟩ := turn_row hPL hW hx h1
    obtain ⟨hr, hW', hL', hx'⟩ := turns_row hPL ps cx1 cx' hE.wf hE.lok hx1 h
    exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem chunks_row (hPL : c.pushLimit = 1) (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → SideRow y z cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    RowRel y z cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ SideRow y z cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨RowRel.refl _, hW, hL, hx⟩
  | ch :: order, cx, cx', hW, hL, hx, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1⟩ := turns_row hPL _ cx cx1 hW hL hx hf
      obtain ⟨hr, hW', hL', hx'⟩ := chunks_row hPL o order cx1 cx' hW1 hL1 hx1 h
      exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem tick_row (hPL : c.pushLimit = 1) {o : TickOracle} {s s' : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : SideRow y z s) (h : tick c o s = .ok s') :
    RowRel y z s s' ∧ SideRow y z s' := by
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
    obtain ⟨hr, -, -, hx'⟩ := chunks_row hPL o order ⟨s0, pw⟩ cx' hW0 hL0 (hr0.sideRow hx) hfold
    exact ⟨hr0.toRow.trans hr, hx'⟩

theorem stateAt_row (hPL : c.pushLimit = 1) {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hx : SideRow y z s) : ∀ t, RowRel y z s (stateAt c o s t) ∧ SideRow y z (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨RowRel.refl _, hx⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx'⟩ := tick_row hPL hWt hLt ih.2 h
    exact ⟨ih.1.trans hr, hx'⟩

end

/-- At push limit 1, if every sideways piston lies in the row `(y, z)` and that row holds a block
that is neither a `+X` piston nor a sticky `-X` piston, the machine has speed 0. -/
theorem pl1_siderow_speed0 {c : Config} {s : St} {y z : Int} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) (hsr : SideRow y z s) {q0 : Pos} (hq0 : q0 ∈ s.body)
    (hy : q0.y = y) (hz : q0.z = z) (hO : s.tyAt q0 = .O) : AlwaysAtMost c s 0 := by
  obtain ⟨B, hB, hBy, hBz, hst⟩ := exists_stuck hq0 hO
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨q0, hq0⟩
  refine alwaysAtMost_zero_of hW hL hN B.x fun o t x hxm => ?_
  obtain ⟨⟨σ, hσ, hmv⟩, -⟩ := stateAt_row (o := o) hPL hW hL hsr t
  have hle : (σ B).x ≤ B.x := by
    by_contra h
    exact hst (hmv B hB (hBy.trans hy) (hBz.trans hz) (by omega))
  exact (keys_x_ge hxm (hσ.mem hB (hBy.trans hy) (hBz.trans hz))).trans hle

/-- **A push limit 1 flyer needs sideways pistons in two different rows.** If all sideways
pistons lie in one row (and there is at least one), the machine has speed 0 under every update
order. -/
theorem pl1_needs_two_side_rows {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) {q0 : Pos} {d0 : Dir} {st0 an0 : Bool} {k0 : Fin 4} {mv0 : Bool}
    (hq0 : s.get q0 = some (.piston d0 st0 an0 k0 mv0)) (hside : d0 ≠ .px ∧ d0 ≠ .nx)
    (hsr : SideRow q0.y q0.z s) : AlwaysAtMost c s 0 := by
  refine pl1_siderow_speed0 hW hL hPL hsr (body_of_piston hq0) rfl rfl ?_
  rw [tyAt_piston hq0]
  cases d0 <;> simp_all [tyOfSig]

end FF
