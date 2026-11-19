/-
At push limit 1, with every piston facing `+X` or `-X`, one piston turn is a relabelling in
which a block that moves forward was pushed by the `+X` piston just behind it or pulled by the
sticky `-X` piston just ahead of it (`Rel`).
-/
import Formal.PL1.Lane

namespace FF

open Std

theorem xdir {d : Dir} (hd : d = .px ∨ d = .nx) : d.dy = 0 ∧ d.dz = 0 ∧ (d.dx = 1 ∨ d.dx = -1) := by
  rcases hd with rfl | rfl <;> decide

theorem Pos.add_y (p : Pos) (d : Dir) : (p.add d).y = p.y + d.dy := rfl
theorem Pos.add_z (p : Pos) (d : Dir) : (p.add d).z = p.z + d.dz := rfl

theorem Pos.ne_of_x {a b : Pos} (h : a.x ≠ b.x) : a ≠ b := by rintro rfl; exact h rfl

theorem tyAt_piston {s : St} {q : Pos} {d : Dir} {st an : Bool} {k : Fin 4} {mv : Bool}
    (h : s.get q = some (.piston d st an k mv)) : s.tyAt q = tyOfSig (.piston, d, st) := by
  simp [St.tyAt, h, Block.sig, Block.kind, Block.dir, Block.sticky]

theorem body_of_piston {s : St} {q : Pos} {d : Dir} {st an : Bool} {k : Fin 4} {mv : Bool}
    (h : s.get q = some (.piston d st an k mv)) : q ∈ s.body :=
  St.mem_body.mpr ⟨_, h, by simp [isNonArm, Block.kind]⟩

theorem not_body_of_none {s : St} {q : Pos} (h : s.get q = none) : q ∉ s.body := by
  intro hq; obtain ⟨b, hb, -⟩ := St.mem_body.mp hq; rw [h] at hb; cases hb

theorem not_body_of_arm {s : St} {q : Pos} {m : Bool} (h : s.get q = some (.plain .arm m)) :
    q ∉ s.body := by
  intro hq; obtain ⟨b, hb, hk⟩ := St.mem_body.mp hq; rw [h] at hb; cases hb
  simp [isNonArm, Block.kind] at hk

/-- A relabelling where only the cells `a` changes, from no block to no block. -/
theorem rel_of_sig_off {s s' : St} (a : Pos) (ha : a ∉ s.body) (ha' : a ∉ s'.body)
    (hs : ∀ q, q ≠ a → (s'.get q).map Block.sig = (s.get q).map Block.sig) : Rel s s' := by
  refine relabel_id (fun q => ?_) (fun q hq => hs q (by rintro rfl; exact ha hq))
  by_cases h : q = a
  · subst h; exact ⟨fun h => absurd h ha', fun h => absurd h ha⟩
  · exact body_iff_of_sig (hs q h)

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool}

theorem rel_ext' {S : List Pos} (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hd : d = .px ∨ d = .nx)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : Rel cx.st cx'.st := by
  obtain ⟨hdy, hdz, hdx⟩ := xdir hd
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
    refine rel_of_sig_off (pos.add d) (not_body_of_none hf) (not_body_of_arm harm') ?_
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
    have hrB : r ∈ cx.st.body := St.mem_body.mpr ⟨br, hbr, by simpa [isNonArm] using immovable_arm hir⟩
    have hr'p : r.add d ≠ pos := by
      apply Pos.ne_of_x; rw [hr, Pos.add_x, Pos.add_x]; omega
    have hr'r : r.add d ≠ pos.add d := by rw [← hr]; exact Pos.add_ne_self r d
    refine relabel_move hrB (not_body_of_none hdest) (by rw [Pos.add_y, hdy]; simp)
      (by rw [Pos.add_z, hdz]; simp) (by rw [Pos.add_x]; omega) ?_ ?_ ?_ ?_
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
    · intro hlt
      rw [Pos.add_x] at hlt
      have hdx1 : d.dx = 1 := by omega
      refine ⟨pos, body_of_piston hb, ?_, ?_, Or.inl ⟨?_, ?_⟩⟩
      · rw [hr, Pos.add_y, hdy]; simp
      · rw [hr, Pos.add_z, hdz]; simp
      · exact (rk_succ (body_of_piston hb) (by rw [hr, Pos.add_y, hdy]; simp)
          (by rw [hr, Pos.add_z, hdz]; simp) (by rw [hr, Pos.add_x, hdx1])).symm
      · rw [tyAt_piston hb]
        rcases hd with rfl | rfl
        · rfl
        · simp [Dir.dx] at hdx1
  | _ :: _ :: _, _, _, hlen => simp at hlen

theorem rel_retract' (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hd : d = .px ∨ d = .nx)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    Rel cx.st cx'.st := by
  obtain ⟨hdy, hdz, hdx⟩ := xdir hd
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hpd : pos.add d ≠ pos := Pos.add_ne_self pos d
  have hlen := (pulled_length (c := c) (cx := cx) (pos := pos) (d := d) (st := st)).1
  rw [hPL] at hlen
  have hsigpos : (cx'.st.get pos).map Block.sig = (cx.st.get pos).map Block.sig := by
    rw [hget, if_pos rfl, hb]; rfl
  have hW1 : ∀ q, q ≠ pos.add d → (cx.st.remove (pos.add d)).get q = cx.st.get q :=
    fun q hq => St.get_remove_ne (Ne.symm hq)
  rcases hP : pulled c cx.st pos d st with _ | ⟨r, _ | ⟨r2, rest⟩⟩
  · -- nothing pulled
    have harm' : cx'.st.get (pos.add d) = none := by
      rw [hget, if_neg hpd, hP]; simp [moveWorld]
    refine rel_of_sig_off (pos.add d) (not_body_of_arm harm) (not_body_of_none harm') ?_
    intro q hq
    by_cases hqp : q = pos
    · subst hqp; exact hsigpos
    · rw [hget, if_neg hqp, hP]; simp [moveWorld, hW1 q hq]
  · -- one block pulled
    have hst : st = true := by
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
    have hrp : r ≠ pos := by apply Pos.ne_of_x; rw [hr, Pos.add_x, Pos.add_x]; omega
    obtain ⟨br, hbr, hir⟩ := discover_mem hdisc (show r ∈ [r] by simp)
    rw [hW1 r hrf] at hbr
    have hrB : r ∈ cx.st.body := St.mem_body.mpr ⟨br, hbr, by simpa [isNonArm] using immovable_arm hir⟩
    have hr' : r.add d.opp = pos.add d := by rw [hr]; simp
    refine relabel_move (r' := r.add d.opp) hrB (by rw [hr']; exact not_body_of_arm harm)
      (by rw [hr', hr, Pos.add_y, Pos.add_y, Pos.add_y, hdy]; simp)
      (by rw [hr', hr, Pos.add_z, Pos.add_z, Pos.add_z, hdz]; simp)
      (by rw [hr', hr, Pos.add_x, Pos.add_x, Pos.add_x]; omega) ?_ ?_ ?_ ?_
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
    · intro hlt
      rw [hr', hr, Pos.add_x, Pos.add_x] at hlt
      have hdx1 : d.dx = -1 := by omega
      have hdn : d = .nx := by
        rcases hd with rfl | rfl
        · simp [Dir.dx] at hdx1
        · rfl
      subst hdn; subst hst
      have ey : pos.y = r.y := by rw [hr]; simp [Pos.add, Dir.dy]
      have ez : pos.z = r.z := by rw [hr]; simp [Pos.add, Dir.dz]
      have ex : r.x = pos.x - 2 := by rw [hr]; simp [Pos.add, Dir.dx]; omega
      refine ⟨pos, body_of_piston hb, ey, ez, Or.inr ⟨?_, ?_⟩⟩
      · refine rk_succ2 hrB ey ez (by omega) ?_
        have : (⟨r.x + 1, r.y, r.z⟩ : Pos) = pos.add .nx :=
          Pos.eq_of_xyz (by simp [Pos.add, Dir.dx]; omega) (by simp [Pos.add, Dir.dy, ey])
            (by simp [Pos.add, Dir.dz, ez])
        rw [this]; exact not_body_of_arm harm
      · rw [tyAt_piston hb]; rfl
  · rw [hP] at hlen; simp at hlen

theorem rel_ext {S : List Pos} (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hx : XOnly cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) : Rel cx.st cx'.st :=
  rel_ext' hPL hW (hx pos _ hb rfl) hb hS hR

theorem rel_retract (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hx : XOnly cx.st)
    (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q) :
    Rel cx.st cx'.st :=
  rel_retract' hPL hW (hx pos _ hb rfl) hb hget

theorem rel_finish {k next : Fin 4} (hb : cx.st.get pos = some (.piston d st an k false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q) :
    Rel cx.st cx'.st := by
  refine relabel_sig fun q => ?_
  rw [hget]
  split
  · rename_i h; subst h; rw [hb]; rfl
  · split
    · rw [Option.map_map]
      congr 1
      funext b
      simp [Block.sig_finished]
    · rfl

theorem rel_fail (hb : cx.st.get pos = some (.piston d st an 0 false)) :
    Rel cx.st (cx.st.set pos (.piston d st true 0 false)) := by
  refine relabel_sig fun q => ?_
  rw [St.get_set]
  split
  · rename_i h; subst h; rw [hb]; rfl
  · rfl

theorem turn_rel (hPL : c.pushLimit = 1) (hW : Wf cx.st) (hx : XOnly cx.st)
    (h : pistonTurn c cx pos = .ok cx') : Rel cx.st cx'.st := by
  have hid : cx' = cx → Rel cx.st cx'.st := fun e => e ▸ Rel.refl _
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
              exact rel_fail hg
            | some S =>
              obtain ⟨cx1, h1, hR, -⟩ := ext_result hW hg hfire hS
              rw [h1] at h; cases h
              exact rel_ext hPL hW hx hg hS hR
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [Fin.val_zero] at h
            rw [if_neg hfire] at h; cases h; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 2) hW hg (Or.inl rfl) rfl
          rw [h1] at h; cases h
          exact rel_finish hg h2
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · apply hid
            unfold pistonTurn at h; rw [hg] at h
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true] at h
            cases h; rfl
          · obtain ⟨cx1, h1, h2, -⟩ := retract_spec (c := c) hW hg (Bool.eq_false_iff.mpr hpw)
            rw [h1] at h; cases h
            exact rel_retract hPL hW hx hg h2
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx1, h1, h2, -⟩ := finish_spec (c := c) (next := 0) hW hg (Or.inr rfl) rfl
          rw [h1] at h; cases h
          exact rel_finish hg h2
    | _ => apply hid; unfold pistonTurn at h; rw [hg] at h; cases h; rfl

end

end FF
