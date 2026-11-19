/-
No flyer at push limit 1 whose pistons all face `+X` or `-X`.

At push limit 1 every move carries a single block one step into an empty cell, so with only
X-facing pistons each row along X keeps its blocks in order forever (`Rel`, `Formal/PL1/Turn`).
A block can then only be moved forward by the `+X` piston just behind it in its row or the
sticky `-X` piston just ahead of it. If the row holds any other block (for instance an observer,
a redstone block or a rod: a power source), some block of the row has no possible forward mover
(`chain_stuck`), so it never moves forward, and the rearmost X stays behind it forever, under
every update order.
-/
import Formal.PL1.Turn
import Formal.NoPower

namespace FF

open Std

theorem rel_tickStart {s : St} : Rel s (tickStart s) := by
  refine relabel_sig fun q => ?_
  rw [tickStart_get, Option.map_map]
  congr 1
  funext b
  exact BitsOnly.sig (comp_bits (calmAt_bits _ q) unpulse_bits) b

section
variable {c : Config}

theorem turns_rel (hPL : c.pushLimit = 1) : ∀ (ps : List Pos) (cx cx' : Ctx), Wf cx.st →
    ListsOK c cx.st → XOnly cx.st → ps.foldlM (pistonTurn c) cx = .ok cx' →
    Rel cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨Rel.refl _, hW, hL, hx⟩
  | p :: ps, cx, cx', hW, hL, hx, h => by
    obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := p) hW hL
    rw [List.foldlM_cons, h1] at h
    have hr1 := turn_rel hPL hW hx h1
    obtain ⟨hr, hW', hL', hx'⟩ := turns_rel hPL ps cx1 cx' hE.wf hE.lok (hr1.xOnly hx) h
    exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem chunks_rel (hPL : c.pushLimit = 1) (o : TickOracle) : ∀ (order : List Chunk) (cx cx' : Ctx),
    Wf cx.st → ListsOK c cx.st → XOnly cx.st →
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' →
    Rel cx.st cx'.st ∧ Wf cx'.st ∧ ListsOK c cx'.st ∧ XOnly cx'.st
  | [], cx, cx', hW, hL, hx, h => by cases h; exact ⟨Rel.refl _, hW, hL, hx⟩
  | ch :: order, cx, cx', hW, hL, hx, h => by
    rw [List.foldlM_cons] at h
    cases hf : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | error e => rw [hf] at h; cases h
    | ok cx1 =>
      rw [hf] at h
      obtain ⟨hr1, hW1, hL1, hx1⟩ := turns_rel hPL _ cx cx1 hW hL hx hf
      obtain ⟨hr, hW', hL', hx'⟩ := chunks_rel hPL o order cx1 cx' hW1 hL1 hx1 h
      exact ⟨hr1.trans hr, hW', hL', hx'⟩

theorem tick_rel (hPL : c.pushLimit = 1) {o : TickOracle} {s s' : St} (hW : Wf s)
    (hL : ListsOK c s) (hx : XOnly s) (h : tick c o s = .ok s') : Rel s s' ∧ XOnly s' := by
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
    obtain ⟨hr, -, -, hx'⟩ := chunks_rel hPL o order ⟨s0, pw⟩ cx' hW0 hL0 (hr0.xOnly hx) hfold
    exact ⟨hr0.trans hr, hx'⟩

theorem stateAt_rel (hPL : c.pushLimit = 1) {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hx : XOnly s) : ∀ t, Rel s (stateAt c o s t) ∧ XOnly (stateAt c o s t) := by
  intro t
  induction t with
  | zero => exact ⟨Rel.refl _, hx⟩
  | succ t ih =>
    obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
    obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
    have he : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
    rw [he]
    obtain ⟨hr, hx'⟩ := tick_rel hPL hWt hLt ih.2 h
    exact ⟨ih.1.trans hr, hx'⟩

end

/-- The X values of the blocks in the row `y`, `z`. -/
def St.rowX (s : St) (y z : Int) : Finset Int :=
  (s.body.filter (fun q => q.y = y ∧ q.z = z)).image (·.x)

theorem rk_eq_rkF {s : St} {p : Pos} {y z : Int} (hy : p.y = y) (hz : p.z = z) :
    s.rk p = rkF (s.rowX y z) p.x := by
  classical
  subst hy; subst hz
  unfold St.rk rkF St.rowX
  rw [Finset.filter_image, Finset.card_image_of_injOn, Finset.filter_filter]
  · congr 1
    apply Finset.filter_congr
    intro q _
    simp [and_assoc]
  · intro a ha b hb e
    simp only [Finset.coe_filter, Set.mem_setOf_eq] at ha hb
    exact Pos.eq_of_xyz e (by simp_all) (by simp_all)

theorem mem_rowX {s : St} {y z x : Int} : x ∈ s.rowX y z ↔ (⟨x, y, z⟩ : Pos) ∈ s.body := by
  unfold St.rowX
  rw [Finset.mem_image]
  constructor
  · rintro ⟨q, hq, rfl⟩
    rw [Finset.mem_filter] at hq
    have : q = ⟨q.x, y, z⟩ := Pos.eq_of_xyz rfl hq.2.1 hq.2.2
    rw [← this]; exact hq.1
  · intro h; exact ⟨_, Finset.mem_filter.mpr ⟨h, rfl, rfl⟩, rfl⟩

/-- A block with no possible forward mover exists as soon as some block is not an X-facing
piston (`+X`, or sticky `-X`). -/
theorem exists_stuck {s : St} {q0 : Pos} (hq0 : q0 ∈ s.body) (hO : s.tyAt q0 = .O) :
    ∃ B ∈ s.body, B.y = q0.y ∧ B.z = q0.z ∧ ¬ HasMover s B := by
  set y := q0.y
  set z := q0.z
  have hq0' : q0 = ⟨q0.x, y, z⟩ := Pos.eq_of_xyz rfl rfl rfl
  obtain ⟨b, hb, hstuck⟩ := chain_stuck (s.rowX y z) (fun x => s.tyAt ⟨x, y, z⟩) q0.x
    (mem_rowX.mpr (hq0' ▸ hq0)) (by show s.tyAt ⟨q0.x, y, z⟩ = .O; rw [← hq0']; exact hO)
  refine ⟨⟨b, y, z⟩, mem_rowX.mp hb, rfl, rfl, ?_⟩
  rintro ⟨p, hp, hpy, hpz, hk⟩
  apply hstuck
  have hpe : p = ⟨p.x, y, z⟩ := Pos.eq_of_xyz rfl hpy hpz
  refine ⟨p.x, mem_rowX.mpr (hpe ▸ hp), ?_⟩
  have h1 := rk_eq_rkF (s := s) hpy hpz
  have h2 : s.rk ⟨b, y, z⟩ = rkF (s.rowX y z) b := rk_eq_rkF (s := s) (p := ⟨b, y, z⟩) rfl rfl
  have h3 : s.tyAt ⟨p.x, y, z⟩ = s.tyAt p := by rw [← hpe]
  rw [← h1, ← h2, h3]
  exact hk

/-- **No flyer at push limit 1 with only X-facing pistons.** If every piston faces `+X` or `-X`
and some block is not a `+X` piston or a sticky `-X` piston (for instance any power source), then
under every update order the rearmost X never gets more than a constant ahead of where it
started: speed 0. -/
theorem pl1_xonly_no_flyer {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) (hx : XOnly s) (hO : ∃ q ∈ s.body, s.tyAt q = .O) :
    AlwaysAtMost c s 0 := by
  obtain ⟨q0, hq0, hO0⟩ := hO
  obtain ⟨B, hB, -, -, hst⟩ := exists_stuck hq0 hO0
  have hN : 0 < s.N := Finset.card_pos.mpr ⟨q0, hq0⟩
  obtain ⟨m0, hm0⟩ := minX_some_of_body hN
  refine ⟨(B.x : ℚ) - m0, ?_⟩
  rintro o t d ⟨s', x, x', hrun, hxs, hx', hd⟩
  rw [hm0] at hxs; cases hxs
  have hs' : s' = stateAt c o s t := by
    have := (stateAt_spec (o := o) hW hL t).1
    rw [hrun] at this; cases this; rfl
  subst hs'
  obtain ⟨⟨σ, hσ, hmv⟩, -⟩ := stateAt_rel (o := o) hPL hW hL hx t
  have hle : (σ B).x ≤ B.x := by
    by_contra h
    exact hst (hmv B hB (by omega))
  have hmin := keys_x_ge hx' (hσ.mem hB)
  have : (x' : ℚ) ≤ B.x := by exact_mod_cast hmin.trans hle
  have hd' : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
  simp only [zero_div, zero_mul, zero_add]
  linarith

theorem tyOfSig_piston {g : Kind × Dir × Bool} (h : tyOfSig g ≠ .O) : g.1 = .piston := by
  obtain ⟨k, d, st⟩ := g
  cases k <;> cases d <;> cases st <;> simp_all [tyOfSig]

/-- **No flyer at push limit 1 with only X-facing pistons**, in full: under every update order
the rearmost X stays within a constant of its start (speed 0). Either some block is not an
X-facing piston and has no forward mover (`pl1_xonly_no_flyer`), or every block is a piston, so
there is no power source and only finitely many moves (`noPow_bounded`). -/
theorem pl1_xonly_speed0 {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit = 1) (hx : XOnly s) (hN : 0 < s.N) : AlwaysAtMost c s 0 := by
  by_cases hO : ∃ q ∈ s.body, s.tyAt q = .O
  · exact pl1_xonly_no_flyer hW hL hPL hx hO
  · push_neg at hO
    have hNP : ∀ o t, NoPow (stateAt c o s t) := by
      intro o t q b hq
      by_cases harm : b.kind = .arm
      · simp [harm]
      · have hqB : q ∈ (stateAt c o s t).body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, harm]⟩
        obtain ⟨⟨σ, hσ, -⟩, -⟩ := stateAt_rel (o := o) hPL hW hL hx t
        obtain ⟨r, hr, rfl⟩ := (hσ.body _).mp hqB
        have hs := hσ.sig r hr
        have hty := hO r hr
        rw [hq] at hs
        cases hb : s.get r with
        | none => rw [hb] at hs; cases hs
        | some b0 =>
          rw [hb] at hs
          have hk0 : b0.kind = .piston := by
            have : s.tyAt r = tyOfSig b0.sig := by simp [St.tyAt, hb]
            rw [this] at hty
            exact tyOfSig_piston hty
          simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hs
          rw [hs.1, hk0]
          simp
    obtain ⟨m0, hm0⟩ := minX_some_of_body hN
    have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
    refine ⟨((s.phi + 4 * c.pushLimit * (s.cls isPK).card : Int) : ℚ) / s.N - m0, ?_⟩
    rintro o t d ⟨s', x, x', hrun, hxs, hx', hd⟩
    rw [hm0] at hxs; cases hxs
    have hs' : s' = stateAt c o s t := by
      have := (stateAt_spec (o := o) hW hL t).1
      rw [hrun] at this; cases this; rfl
    subst hs'
    have hb := noPow_bounded hW hL (hNP o) t hx'
    have hb' : (s.N : ℚ) * x' ≤ ((s.phi + 4 * c.pushLimit * (s.cls isPK).card : Int) : ℚ) := by
      exact_mod_cast hb
    have hx'le : (x' : ℚ) ≤ ((s.phi + 4 * c.pushLimit * (s.cls isPK).card : Int) : ℚ) / s.N := by
      rw [le_div_iff₀ hN']; linarith
    have hd' : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
    simp only [zero_div, zero_mul, zero_add]
    linarith

end FF
