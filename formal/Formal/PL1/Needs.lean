/-
What a push limit 1 flyer needs. At push limit 1, with pistons facing any way, a move carries one
block one step, and it moves forward only if pushed by the `+X` piston just behind it or pulled
by a sticky `-X` piston two cells ahead of it. Hence:
* without a sticky `-X` piston the rearmost block layer never advances (`pl1_needs_Q`);
* without a `+X` piston the frontmost layer never advances, so neither does the rear
  (`pl1_needs_P`);
* without a power source there are finitely many moves (`pl1_needs_power`);
* with only X-facing pistons nothing flies (`pl1_xonly_speed0`).
So a push limit 1 flyer needs a `+X` piston, a sticky `-X` piston, a sideways piston and a power
source (`pl1_flyer_needs`).
-/
import Formal.PL1.NoFlyer

namespace FF

open Std

/-- `r` could be moved forward in `s`: a `+X` piston just behind it or a sticky `-X` piston two
cells ahead of it (anywhere in those layers). -/
def HasFwd (s : St) (r : Pos) : Prop :=
  (∃ p ∈ s.body, p.x + 1 = r.x ∧ s.tyAt p = .P) ∨ (∃ p ∈ s.body, p.x = r.x + 2 ∧ s.tyAt p = .Q)

/-- A one-to-one map of the blocks keeping their kinds, facings and stickiness, in which a block
gains at most one in X, and only if it could be moved forward. -/
def Rel0 (s s' : St) : Prop :=
  ∃ σ : Pos → Pos, (∀ q, q ∈ s'.body ↔ ∃ r ∈ s.body, σ r = q) ∧
    (∀ r ∈ s.body, (s'.get (σ r)).map Block.sig = (s.get r).map Block.sig) ∧
    (∀ r ∈ s.body, (σ r).x ≤ r.x ∨ ((σ r).x = r.x + 1 ∧ HasFwd s r))

theorem rel0_id {s s' : St} (hb : ∀ q, q ∈ s'.body ↔ q ∈ s.body)
    (hs : ∀ q ∈ s.body, (s'.get q).map Block.sig = (s.get q).map Block.sig) : Rel0 s s' :=
  ⟨id, fun q => by rw [hb]; exact ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩, hs,
    fun r _ => Or.inl (_root_.le_refl _)⟩

theorem rel0_sig {s s' : St} (hs : ∀ q, (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    Rel0 s s' :=
  rel0_id (fun q => body_iff_of_sig (hs q)) (fun q _ => hs q)

theorem rel0_off {s s' : St} (a : Pos) (ha : a ∉ s.body) (ha' : a ∉ s'.body)
    (hs : ∀ q, q ≠ a → (s'.get q).map Block.sig = (s.get q).map Block.sig) : Rel0 s s' := by
  refine rel0_id (fun q => ?_) (fun q hq => hs q (by rintro rfl; exact ha hq))
  by_cases h : q = a
  · subst h; exact ⟨fun h => absurd h ha', fun h => absurd h ha⟩
  · exact body_iff_of_sig (hs q h)

theorem rel0_move {s s' : St} {r r' : Pos} (hr : r ∈ s.body) (hr' : r' ∉ s.body)
    (hx : r'.x ≤ r.x ∨ (r'.x = r.x + 1 ∧ HasFwd s r))
    (hget' : (s'.get r').map Block.sig = (s.get r).map Block.sig)
    (hrn : r ∉ s'.body)
    (hothers : ∀ q, q ≠ r → q ≠ r' → (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    Rel0 s s' := by
  classical
  have hne : r ≠ r' := by rintro rfl; exact hr' hr
  have hr's : r' ∈ s'.body := by
    rw [St.mem_body] at hr ⊢
    obtain ⟨b, hb, hk⟩ := hr
    rw [hb] at hget'
    cases h : s'.get r' with
    | none => rw [h] at hget'; cases hget'
    | some b' =>
      rw [h] at hget'
      simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hget'
      exact ⟨b', rfl, by simp [isNonArm] at hk ⊢; rw [hget'.1]; exact hk⟩
  set σ : Pos → Pos := fun q => if q = r then r' else q with hσ
  refine ⟨σ, ?_, ?_, ?_⟩
  · intro q
    by_cases h1 : q = r'
    · subst h1; exact ⟨fun _ => ⟨r, hr, by simp [hσ]⟩, fun _ => hr's⟩
    · by_cases h2 : q = r
      · subst h2
        refine ⟨fun h => absurd h hrn, ?_⟩
        rintro ⟨p, hp, e⟩
        simp only [hσ] at e
        split at e
        · exact absurd e.symm hne
        · rename_i hpr; exact absurd e hpr
      · rw [body_iff_of_sig (hothers q h2 h1)]
        constructor
        · intro h; exact ⟨q, h, by simp [hσ, h2]⟩
        · rintro ⟨p, hp, e⟩
          simp only [hσ] at e
          split at e
          · exact absurd e.symm h1
          · exact e ▸ hp
  · intro p hp
    simp only [hσ]
    split
    · rename_i h; subst h; exact hget'
    · rename_i h
      exact hothers p h (by rintro rfl; exact hr' hp)
  · intro p hp
    simp only [hσ]
    split
    · rename_i h; subst h; exact hx
    · exact Or.inl (_root_.le_refl _)

theorem Pos.add_add_ne (p : Pos) (d : Dir) : (p.add d).add d ≠ p := by
  intro h
  cases p; cases d <;> simp only [Pos.add, Dir.dx, Dir.dy, Dir.dz, Pos.mk.injEq] at h <;> omega

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem rel0_ext {S : List Pos} (hPL : c.pushLimit = 1)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : Rel0 cx.st cx'.st := by
  have hlen := discover_length_le hS
  rw [hPL] at hlen
  have hpd : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hpos' : cx'.st.get pos = some (.piston d st false 1 false) := by rw [hR.get]; simp
  have hsigpos : (cx'.st.get pos).map Block.sig = (cx.st.get pos).map Block.sig := by
    rw [hpos', hb]; rfl
  have harm' : cx'.st.get (pos.add d) = some (.plain .arm false) := by
    rw [hR.get, if_neg hpd]; simp
  match S, hS, hR, hlen with
  | [], hS, hR, _ =>
    have hf : cx.st.get (pos.add d) = none := by
      cases h : cx.st.get (pos.add d) with
      | none => rfl
      | some _ => have := discover_first_mem hS (by rw [h]; rfl); simp at this
    refine rel0_off (pos.add d) (not_body_of_none hf) (not_body_of_arm harm') ?_
    intro q hq
    by_cases hqp : q = pos
    · subst hqp; exact hsigpos
    · rw [hR.get, if_neg hqp, if_neg hq]; simp [moveWorld]
  | [r], hS, hR, _ =>
    have hM := discover_moveOK hS
    have hr : r = pos.add d := by
      cases h : cx.st.get (pos.add d) with
      | none => have := discover_empty hS h; simp at this
      | some _ =>
        have := discover_first_mem hS (by rw [h]; rfl)
        simp at this; exact this.symm
    have hdest : cx.st.get (r.add d) = none := by
      cases h : cx.st.get (r.add d) with
      | none => rfl
      | some _ =>
        have := hM.2 r (by simp) (by rw [h]; rfl)
        simp at this; exact absurd this (Pos.add_ne_self r d)
    obtain ⟨br, hbr, hir⟩ := discover_mem hS (show r ∈ [r] by simp)
    have hrB : r ∈ cx.st.body :=
      St.mem_body.mpr ⟨br, hbr, by simpa [isNonArm] using immovable_arm hir⟩
    have hr'p : r.add d ≠ pos := by rw [hr]; exact Pos.add_add_ne pos d
    have hr'r : r.add d ≠ pos.add d := by rw [← hr]; exact Pos.add_ne_self r d
    have hxc : (r.add d).x ≤ r.x ∨ ((r.add d).x = r.x + 1 ∧ HasFwd cx.st r) := by
      cases d with
      | px =>
        right
        refine ⟨by simp [Pos.add, Dir.dx], Or.inl ⟨pos, body_of_piston hb, ?_, ?_⟩⟩
        · rw [hr]; simp [Pos.add, Dir.dx]
        · rw [tyAt_piston hb]; rfl
      | _ => left; simp [Pos.add, Dir.dx]
    refine rel0_move hrB (not_body_of_none hdest) hxc ?_ ?_ ?_
    · rw [hR.get, if_neg hr'p, if_neg hr'r, mw_dest (by simp), hbr]
      simp [Block.sig_startMoving]
    · rw [hr]; exact not_body_of_arm harm'
    · intro q hq1 hq2
      by_cases hqp : q = pos
      · subst hqp; exact hsigpos
      · rw [hR.get, if_neg hqp, if_neg (by rw [← hr]; exact hq1)]
        unfold moveWorld
        rw [if_neg, if_neg (by simpa using hq1)]
        intro h
        simp at h
        apply hq2; rw [← h]; simp
  | _ :: _ :: _, _, _, hlen => simp at hlen

theorem rel0_retract (hPL : c.pushLimit = 1) (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    Rel0 cx.st cx'.st := by
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hpd : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hlen := (pulled_length (c := c) (cx := cx) (pos := pos) (d := d) (st := st)).1
  rw [hPL] at hlen
  have hsigpos : (cx'.st.get pos).map Block.sig = (cx.st.get pos).map Block.sig := by
    rw [hget, if_pos rfl, hb]; rfl
  have hW1 : ∀ q, q ≠ pos.add d → (cx.st.remove (pos.add d)).get q = cx.st.get q :=
    fun q hq => St.get_remove_ne (Ne.symm hq)
  rcases hP : pulled c cx.st pos d st with _ | ⟨r, _ | ⟨r2, rest⟩⟩
  · have harm' : cx'.st.get (pos.add d) = none := by
      rw [hget, if_neg hpd, hP]; simp [moveWorld]
    refine rel0_off (pos.add d) (not_body_of_arm harm) (not_body_of_none harm') ?_
    intro q hq
    by_cases hqp : q = pos
    · subst hqp; exact hsigpos
    · rw [hget, if_neg hqp, hP]; simp [moveWorld, hW1 q hq]
  · have hst : st = true := by
      cases st
      · simp [pulled] at hP
      · rfl
    have hdisc : discover c (cx.st.remove (pos.add d)) ((pos.add d).add d) d.opp (some pos) true =
        some [r] := by
      rcases pulled_cases (c := c) (cx := cx) (pos := pos) (d := d) (st := st) with h | h
      · rw [hP] at h; cases h
      · rw [hP] at h; exact h
    have hr : r = (pos.add d).add d := by
      cases h : (cx.st.remove (pos.add d)).get ((pos.add d).add d) with
      | none => have := discover_empty hdisc h; simp at this
      | some _ =>
        have := discover_first_mem hdisc (by rw [h]; rfl)
        simp at this; exact this.symm
    have hrf : r ≠ pos.add d := by rw [hr]; exact Pos.add_ne_self _ d
    have hrp : r ≠ pos := by rw [hr]; exact Pos.add_add_ne pos d
    obtain ⟨br, hbr, hir⟩ := discover_mem hdisc (show r ∈ [r] by simp)
    rw [hW1 r hrf] at hbr
    have hrB : r ∈ cx.st.body :=
      St.mem_body.mpr ⟨br, hbr, by simpa [isNonArm] using immovable_arm hir⟩
    have hr' : r.add d.opp = pos.add d := by rw [hr]; simp
    have hxc : (r.add d.opp).x ≤ r.x ∨ ((r.add d.opp).x = r.x + 1 ∧ HasFwd cx.st r) := by
      subst hst
      cases d with
      | nx =>
        right
        refine ⟨by simp [Pos.add, Dir.dx, Dir.opp], Or.inr ⟨pos, body_of_piston hb, ?_, ?_⟩⟩
        · rw [hr]; simp [Pos.add, Dir.dx]; omega
        · rw [tyAt_piston hb]; rfl
      | _ => left; simp [Pos.add, Dir.dx, Dir.opp]
    refine rel0_move (r' := r.add d.opp) hrB (by rw [hr']; exact not_body_of_arm harm) hxc ?_ ?_ ?_
    · rw [hget, if_neg (by rw [hr']; exact hpd), hP, mw_dest (by simp), hW1 r hrf, hbr]
      simp [Block.sig_startMoving]
    · rw [St.mem_body]
      rintro ⟨b, hb', -⟩
      rw [hget, if_neg hrp, hP] at hb'
      unfold moveWorld at hb'
      rw [if_neg (by simp; exact Pos.add_ne_self r d), if_pos (by simp)] at hb'
      cases hb'
    · intro q hq1 hq2
      by_cases hqp : q = pos
      · subst hqp; exact hsigpos
      · have hqf : q ≠ pos.add d := by rw [← hr']; exact hq2
        rw [hget, if_neg hqp, hP]
        unfold moveWorld
        rw [if_neg, if_neg (by simpa using hq1), hW1 q hqf]
        intro h
        simp at h
        apply hqf
        have := congrArg (fun p => p.add d.opp) h
        simp at this
        rw [this, hr]; simp
  · rw [hP] at hlen; simp at hlen

theorem rel0_finish {k next : Fin 4} (hb : cx.st.get pos = some (.piston d st an k false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q) :
    Rel0 cx.st cx'.st := by
  refine rel0_sig fun q => ?_
  rw [hget]
  split
  · rename_i h; subst h; rw [hb]; rfl
  · split
    · rw [Option.map_map]
      congr 1
      funext b
      simp [Block.sig_finished]
    · rfl

theorem rel0_fail (hb : cx.st.get pos = some (.piston d st an 0 false)) :
    Rel0 cx.st (cx.st.set pos (.piston d st true 0 false)) := by
  refine rel0_sig fun q => ?_
  rw [St.get_set]
  split
  · rename_i h; subst h; rw [hb]; rfl
  · rfl

theorem turn_rel0 (hPL : c.pushLimit = 1) (hW : Wf cx.st)
    (h : pistonTurn c cx pos = .ok cx') : Rel0 cx.st cx'.st := by
  have hid : cx' = cx → Rel0 cx.st cx'.st := fun e => e ▸ rel0_sig (fun _ => rfl)
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
              exact rel0_fail hg
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              exact rel0_ext hPL hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          exact rel0_finish hg h2
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true] at h
            cases h; rfl
          · obtain ⟨cx1, h1, h2, -⟩ := retract_spec (c := c) hW hg (Bool.eq_false_iff.mpr hpw)
            rw [h1] at h; cases h
            exact rel0_retract hPL hW hg h2
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          exact rel0_finish hg h2
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

/-! ### Invariants -/

def NoTy (t : Ty) (s : St) : Prop := ∀ q ∈ s.body, s.tyAt q ≠ t

theorem Rel0.noTy {s s' : St} {t : Ty} (h : Rel0 s s') (hn : NoTy t s) : NoTy t s' := by
  obtain ⟨σ, hb, hs, -⟩ := h
  intro q hq
  obtain ⟨r, hr, rfl⟩ := (hb q).mp hq
  have : s'.tyAt (σ r) = s.tyAt r := by unfold St.tyAt; rw [hs r hr]
  rw [this]; exact hn r hr

/-- With no sticky `-X` piston, some block stays at or behind `m`. -/
def IQ (m : Int) (s : St) : Prop := NoTy .Q s ∧ ∃ q ∈ s.body, q.x ≤ m

/-- With no `+X` piston, every block stays at or behind `M`. -/
def IP (M : Int) (s : St) : Prop := NoTy .P s ∧ ∀ q ∈ s.body, q.x ≤ M

theorem Rel0.iQ {s s' : St} {m : Int} (h : Rel0 s s') (hI : IQ m s) : IQ m s' := by
  refine ⟨h.noTy hI.1, ?_⟩
  obtain ⟨σ, hb, -, hx⟩ := h
  obtain ⟨q, hq, hqm⟩ := hI.2
  -- the rearmost such block: if it moved forward, it was pushed from behind
  have mem : ∀ r ∈ s.body, σ r ∈ s'.body := fun r hr => (hb _).mpr ⟨r, hr, rfl⟩
  rcases hx q hq with h1 | ⟨h1, hf⟩
  · exact ⟨σ q, mem q hq, by omega⟩
  · rcases hf with ⟨p, hp, hpx, -⟩ | ⟨p, hp, -, hpQ⟩
    · refine ⟨σ p, mem p hp, ?_⟩
      rcases hx p hp with h2 | ⟨h2, -⟩ <;> omega
    · exact absurd hpQ (hI.1 p hp)

theorem Rel0.iP {s s' : St} {M : Int} (h : Rel0 s s') (hI : IP M s) : IP M s' := by
  refine ⟨h.noTy hI.1, ?_⟩
  obtain ⟨σ, hb, -, hx⟩ := h
  intro q hq
  obtain ⟨r, hr, rfl⟩ := (hb q).mp hq
  rcases hx r hr with h1 | ⟨h1, hf⟩
  · have := hI.2 r hr; omega
  · rcases hf with ⟨p, hp, -, hpP⟩ | ⟨p, hp, hpx, -⟩
    · exact absurd hpP (hI.1 p hp)
    · have := hI.2 p hp; omega

theorem Rel0.noPow {s s' : St} (h : Rel0 s s') (hn : NoPow s) : NoPow s' := by
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

theorem rel0_tickStart {s : St} : Rel0 s (tickStart s) := by
  refine rel0_sig fun q => ?_
  rw [tickStart_get, Option.map_map]
  congr 1
  funext b
  exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b

/-! ### Ticks and runs -/

section
variable {c : Config} (hPL : c.pushLimit = 1) (I : St → Prop) (hI : ∀ s s', Rel0 s s' → I s → I s')
include hPL hI

theorem turns_pres : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st → ListsOK c cx.st → I cx.st →
    ps.foldlM (pistonTurn c) cx = .ok cx' → Wf cx'.st ∧ ListsOK c cx'.st ∧ I cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    exact turns_pres ps cx1 cx' hE.wf hE.lok (hI _ _ (turn_rel0 hPL hW h1) hx) h

theorem chunks_pres (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
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
      obtain ⟨hW1, hL1, hx1⟩ := turns_pres hPL I hI _ cx cx1 hW hL hx hf
      exact chunks_pres o order cx1 cx' hW1 hL1 hx1 h

theorem tick_pres {o : TickOracle} {s s' : St} (hW : Wf s) (hL : ListsOK c s) (hx : I s)
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
    exact (chunks_pres hPL I hI o order ⟨s0, pw⟩ cx' hW0 hL0 (hI _ _ rel0_tickStart hx) hfold).2.2

theorem stateAt_pres {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) (hx : I s) :
    ∀ t, I (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact hx
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    exact tick_pres hPL I hI hWt hLt ih h

end

/-! ### The theorems -/

/-- From a bound `minX(t) ≤ X` on every run, speed 0. -/
theorem alwaysAtMost_zero_of {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (X : Int) (hX : ∀ o t x, (stateAt c o s t).minX? = some x → x ≤ X) : AlwaysAtMost c s 0 := by
  obtain ⟨m0, hm0⟩ := minX_some_of_body hN
  refine ⟨(X : ℚ) - m0, ?_⟩
  rintro o t d ⟨s', x, x', hrun, hxs, hx', hd⟩
  rw [hm0] at hxs; cases hxs
  have hs' : s' = stateAt c o s t := by
    have := (stateAt_spec (o := o) hW hL t).1
    rw [hrun] at this; cases this; rfl
  subst hs'
  have h1 : (x' : ℚ) ≤ X := by exact_mod_cast hX o t x' hx'
  have hd' : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
  simp only [zero_div, zero_mul, zero_add]
  linarith

/-- Push limit 1 without a sticky `-X` piston: speed 0. -/
theorem pl1_needs_Q {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hPL : c.pushLimit = 1)
    (hN : 0 < s.N) (hQ : NoTy .Q s) : AlwaysAtMost c s 0 := by
  obtain ⟨q0, hq0⟩ := Finset.card_pos.mp hN
  refine alwaysAtMost_zero_of hW hL hN q0.x fun o t x hx => ?_
  have := stateAt_pres (o := o) hPL (IQ q0.x) (fun _ _ h hI => h.iQ hI) hW hL ⟨hQ, q0, hq0, _root_.le_refl _⟩ t
  obtain ⟨q, hq, hqx⟩ := this.2
  exact (keys_x_ge hx hq).trans hqx

/-- Push limit 1 without a `+X` piston: speed 0. -/
theorem pl1_needs_P {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hPL : c.pushLimit = 1)
    (hN : 0 < s.N) (hP : NoTy .P s) : AlwaysAtMost c s 0 := by
  classical
  obtain ⟨M, hM'⟩ : ∃ M : Int, ∀ q ∈ s.body, q.x ≤ M :=
    ⟨∑ q ∈ s.body, |q.x|, fun q hq => (le_abs_self _).trans
      (Finset.single_le_sum (f := fun q => |q.x|) (fun _ _ => abs_nonneg _) hq)⟩
  refine alwaysAtMost_zero_of hW hL hN M fun o t x hx => ?_
  have hI := stateAt_pres (o := o) hPL (IP M) (fun _ _ h hI => h.iP hI) hW hL ⟨hP, hM'⟩ t
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

/-- Push limit 1 without a power source (end rod, redstone block, observer): speed 0. -/
theorem pl1_needs_power {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) (hN : 0 < s.N) (hNP : NoPow s) : AlwaysAtMost c s 0 := by
  have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
  refine alwaysAtMost_zero_of hW hL hN ((s.phi + 4 * c.pushLimit * (s.cls isPK).card) / s.N)
    fun o t x hx => ?_
  have hNPt := stateAt_pres (o := o) hPL NoPow (fun _ _ h hn => h.noPow hn) hW hL hNP
  have hb := noPow_bounded hW hL hNPt t hx
  have hNi : (0 : Int) < s.N := by exact_mod_cast hN
  rw [Int.le_ediv_iff_mul_le hNi]
  linarith

/-- **What a push limit 1 flyer needs.** A machine at push limit 1 has speed 0 under every
update order unless it has a `+X` piston, a sticky `-X` piston, a piston facing sideways and a
power source (end rod, redstone block or observer). -/
theorem pl1_flyer_needs {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) (hN : 0 < s.N)
    (hmiss : NoTy .P s ∨ NoTy .Q s ∨ XOnly s ∨ NoPow s) : AlwaysAtMost c s 0 := by
  rcases hmiss with h | h | h | h
  · exact pl1_needs_P hW hL hPL hN h
  · exact pl1_needs_Q hW hL hPL hN h
  · exact pl1_xonly_speed0 hW hL hPL h hN
  · exact pl1_needs_power hW hL hPL hN h

end FF
