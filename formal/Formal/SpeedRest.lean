/-
A speed bound that uses the pistons' rest: with `K` pistons and `N` blocks (not counting
arms), every run from a well-formed state has speed at most

    10 · PL · K / (PL · K + 2 · N)   blocks per second.

Why: a piston cannot be moved while it is in states 1, 2, 3 (at least three tick ends per
push or pull cycle), nor in the tick before it extends (a piston moved in that tick is not
powered, and an angry one must have failed while resting earlier). So with speed `v` per
tick every piston, which must itself move `v` per tick, completes at most `(1 - v)/4`
cycles per tick, and each cycle moves at most `2 · PL` blocks, while all `N` blocks must
move `v` per tick.

Since `K ≤ N`, this is at most `10 · PL / (PL + 2)` (8.57 at push limit 12), and at push
limit 12 a flyer with at least 6 blocks per piston cannot beat 5 blocks per second.
-/
import Formal.SpeedBound
import Formal.Lemmas.RestTick
import Formal.Counting2

namespace FF

open Std

/-! ### One state -/

section
variable {s : St} (hW : Wf s)
include hW

/-- The pistons are resting, in state 1, 2 or 3, or moving. -/
theorem pistons_partition :
    (s.cls isPK).card = s.restP.card + s.nState 1 + s.nState 2 + s.nState 3 + s.movP.card := by
  classical
  have hU : s.cls isPK = s.restP ∪ s.stateCells 1 ∪ s.stateCells 2 ∪ s.stateCells 3 ∪ s.movP := by
    ext q
    simp only [Finset.mem_union, St.mem_cls, St.restP, St.movP, St.mem_cellsWith,
      St.mem_stateCells, HasState]
    constructor
    · rintro ⟨b, hb, hk⟩
      cases b with
      | piston d st an k mv =>
        cases mv
        · have hk4 := k.isLt
          rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
            h | h | h | h
          · left; left; left; left; exact ⟨_, hb, by simp [h]⟩
          · left; left; left; right; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
          · left; left; right; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
          · left; right; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
        · right; exact ⟨_, hb, by simp [Block.isPiston, Block.kind, Block.moving]⟩
      | plain kk m => cases kk <;> simp [isPK, Block.kind] at hk
      | _ => simp [isPK, Block.kind] at hk
    · rintro ((((⟨b, hb, hk⟩ | ⟨d, st, an, hb⟩) | ⟨d, st, an, hb⟩) | ⟨d, st, an, hb⟩) | ⟨b, hb, hk⟩)
      · refine ⟨b, hb, ?_⟩
        cases b with
        | piston => simp [isPK, Block.kind]
        | _ => simp at hk
      · exact ⟨_, hb, by simp [isPK, Block.kind]⟩
      · exact ⟨_, hb, by simp [isPK, Block.kind]⟩
      · exact ⟨_, hb, by simp [isPK, Block.kind]⟩
      · refine ⟨b, hb, ?_⟩
        simp only [Block.isPiston, Bool.and_eq_true, beq_iff_eq] at hk
        simp [isPK, hk.1]
  -- the parts are disjoint
  have key : ∀ q, (q ∈ s.restP → q ∉ s.stateCells 1 ∧ q ∉ s.stateCells 2 ∧ q ∉ s.stateCells 3 ∧
      q ∉ s.movP) ∧ (q ∈ s.stateCells 1 → q ∉ s.stateCells 2 ∧ q ∉ s.stateCells 3 ∧ q ∉ s.movP) ∧
      (q ∈ s.stateCells 2 → q ∉ s.stateCells 3 ∧ q ∉ s.movP) ∧
      (q ∈ s.stateCells 3 → q ∉ s.movP) := by
    intro q
    simp only [St.restP, St.movP, St.mem_cellsWith, St.mem_stateCells, HasState]
    refine ⟨?_, ?_, ?_, ?_⟩
    · rintro ⟨b, hb, hk⟩
      cases b with
      | piston d st an k mv =>
        cases mv
        · simp at hk
          refine ⟨?_, ?_, ?_, ?_⟩ <;> (try rintro ⟨_, _, _, h⟩) <;> (try rintro ⟨_, h, _⟩) <;>
            simp_all [Block.isPiston, Block.kind, Block.moving]
          all_goals (have := congrArg Fin.val h; simp_all)
        · simp at hk
      | _ => simp at hk
    · rintro ⟨d, st, an, hb⟩
      refine ⟨?_, ?_, ?_⟩ <;> (try rintro ⟨_, _, _, h⟩) <;> (try rintro ⟨_, h, _⟩) <;>
        simp_all [Block.isPiston, Block.kind, Block.moving]
    · rintro ⟨d, st, an, hb⟩
      refine ⟨?_, ?_⟩ <;> (try rintro ⟨_, _, _, h⟩) <;> (try rintro ⟨_, h, _⟩) <;>
        simp_all [Block.isPiston, Block.kind, Block.moving]
    · rintro ⟨d, st, an, hb⟩ ⟨_, h, h'⟩
      simp_all [Block.isPiston, Block.kind, Block.moving]
  have dj : ∀ A B : Finset Pos, (∀ q, q ∈ A → q ∉ B) → Disjoint A B :=
    fun A B h => Finset.disjoint_left.mpr h
  rw [hU, Finset.card_union_of_disjoint (dj _ _ ?_), Finset.card_union_of_disjoint (dj _ _ ?_),
    Finset.card_union_of_disjoint (dj _ _ ?_), Finset.card_union_of_disjoint (dj _ _ ?_)]
  · rfl
  all_goals
    intro q hq
    try simp only [Finset.mem_union] at hq
    have := key q
    tauto

theorem tokens_le : s.tokens ≤ (s.cls isPK).card := by
  classical
  rw [pistons_partition hW]
  unfold St.tokens
  have h1 : s.angryMov ⊆ s.movP := by
    intro q hq
    obtain ⟨b, hb, hk⟩ := St.mem_cellsWith.mp hq
    refine St.mem_cellsWith.mpr ⟨b, hb, ?_⟩
    cases b with
    | piston d st an k mv => cases an <;> cases mv <;> simp_all [Block.isPiston, Block.kind, Block.moving]
    | _ => simp at hk
  have h2 : s.fAngry ⊆ s.stateCells 1 ∪ s.stateCells 2 ∪ s.stateCells 3 := by
    intro q hq
    obtain ⟨b, hb, hk⟩ := St.mem_fAngry.mp hq
    simp only [Finset.mem_union, St.mem_stateCells, HasState]
    cases b with
    | piston d st an k mv =>
      cases mv
      · simp [faB] at hk
        have hk4 := k.isLt
        rcases (show k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with h | h | h
        · left; left; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
        · left; right; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
        · right; exact ⟨d, st, an, by rw [hb]; congr; exact Fin.ext h⟩
      · simp [faB] at hk
    | _ => simp [faB] at hk
  have c1 := Finset.card_le_card h1
  have c2 := (Finset.card_le_card h2).trans ((Finset.card_union_le _ _).trans
    (Nat.add_le_add_right (Finset.card_union_le _ _) _))
  unfold St.nState; omega

end

theorem minX_mul_le_cls {s : St} {m : Int} (hm : s.minX? = some m) :
    ((s.cls isPK).card : Int) * m ≤ s.xsum isPK := by
  have hsub : ∀ q ∈ s.cls isPK, q ∈ s.body := by
    intro q hq
    obtain ⟨b, hb, hk⟩ := St.mem_cls.mp hq
    exact St.mem_body.mpr ⟨b, hb, by intro h; rw [h] at hk; simp [isPK] at hk⟩
  unfold St.xsum
  have : ∑ _q ∈ s.cls isPK, m ≤ ∑ q ∈ s.cls isPK, q.x :=
    Finset.sum_le_sum fun q hq => keys_x_ge hm (hsub q hq)
  simpa [Finset.sum_const, nsmul_eq_mul] using this

/-! ### The run -/

theorem stateAt_tick {c : Config} {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) (t : Nat) :
    TickResult2 (stateAt c o s t) (stateAt c o s (t + 1)) := by
  obtain ⟨-, hWt, hLt, -⟩ := stateAt_spec (o := o) hW hL t
  obtain ⟨s', h, hR⟩ := tick_spec2 hWt hLt (o t)
  have : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
  rw [this]; exact hR

/-- The rest bound: from a well-formed state with `K` pistons and `N > 0` blocks, every run has
speed at most `10·PL·K / (PL·K + 2·N)` blocks per second, up to a constant. -/
theorem speed_bound_rest {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N) :
    AlwaysAtMost c s (10 * c.pushLimit * (s.cls isPK).card /
      (c.pushLimit * (s.cls isPK).card + 2 * s.N)) := by
  set PL := c.pushLimit
  set K := (s.cls isPK).card
  set N := s.N
  have hD : (0 : ℚ) < PL * K + 2 * N := by
    have : (0 : ℚ) < N := by exact_mod_cast hN
    positivity
  obtain ⟨m0, hm0⟩ := minX_some_of_body hN
  refine ⟨(2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K : ℚ) / (PL * K + 2 * N) - m0, ?_⟩
  rintro o t d ⟨s', x, x', hrun, hx, hx', hd⟩
  rw [hm0] at hx; cases hx
  have hs' : s' = stateAt c o s t := by
    have := (stateAt_spec (o := o) hW hL t).1
    rw [hrun] at this; cases this; rfl
  subst hs'
  have hspec := stateAt_spec (o := o) hW hL
  have hR2 := stateAt_tick (o := o) hW hL
  have hKc : ∀ i, ((stateAt c o s i).cls isPK).card = K := by
    intro i
    induction i with
    | zero => rfl
    | succ i ih => rw [(hR2 i).kc, ih]
  have hNc : ∀ i, (stateAt c o s i).N = N := by
    intro i
    induction i with
    | zero => rfl
    | succ i ih => rw [(hspec i).2.2.2.count, ih]
  have key := counting2 PL K N t
    (fun i => (stateAt c o s i).nState 1) (fun i => (stateAt c o s i).nState 2)
    (fun i => (stateAt c o s i).nState 3) (fun i => (stateAt c o s i).movP.card)
    (fun i => (stateAt c o s i).restP.card) (fun i => (stateAt c o s i).tokens)
    (fun i => (stateAt c o s i).listTotal)
    (fun i => (stateAt c o s i).xsum isPK) (fun i => (stateAt c o s i).phi)
    (fun i => by have := pistons_partition (hspec i).2.1; rw [hKc i] at this; omega)
    (fun i => (hR2 i).rest)
    (fun i => by rw [← hKc i]; exact tokens_le (hspec i).2.1)
    (fun i => (hspec i).2.2.2.n1_le)
    (fun i => (hR2 i).lo) (fun i => (hR2 i).hi) (fun i => (hR2 i).psi)
    (fun i => (hspec i).2.2.2.phi)
    (fun i => listTotal_le (hspec i).2.1 (hspec i).2.2.1)
    x' (by have := minX_mul_le hx'; rw [hNc t] at this; exact this)
    (by have := minX_mul_le_cls hx'; rw [hKc t] at this; exact this)
  -- to the rationals
  have hkey : ((2 * N + PL * K : ℚ)) * x' ≤
      PL * K * t + (2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K) := by
    have := key
    simp only [stateAt] at this
    have h' : ((2 * N + PL * K : Int) : ℚ) * (x' : ℚ) ≤
        ((PL * K * t + 2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K : Int) : ℚ) := by
      exact_mod_cast this
    push_cast at h'
    linarith
  have hx'le : (x' : ℚ) ≤ (PL * K * t + (2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K)) /
      (PL * K + 2 * N) := by
    rw [le_div_iff₀ hD]; linarith
  have hd' : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
  have hsplit : (PL * K * t + (2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K) : ℚ) /
      (PL * K + 2 * N) = 10 * PL * K / (PL * K + 2 * N) / 10 * t +
      (2 * s.phi + PL * s.xsum isPK + 20 * PL * K + 20 * K) / (PL * K + 2 * N) := by
    field_simp
    try ring
  linarith


/-! ### Consequences -/

theorem AlwaysAtMost.mono {c : Config} {s : St} {v v' : ℚ} (h : AlwaysAtMost c s v)
    (hv : v ≤ v') : AlwaysAtMost c s v' := by
  obtain ⟨C, hC⟩ := h
  refine ⟨C, fun o t d hd => (hC o t d hd).trans ?_⟩
  have : (0 : ℚ) ≤ t := by positivity
  nlinarith

theorem pistons_le_N (s : St) : (s.cls isPK).card ≤ s.N := by
  apply Finset.card_le_card
  intro q hq
  obtain ⟨b, hb, hk⟩ := St.mem_cls.mp hq
  exact St.mem_body.mpr ⟨b, hb, by intro h; rw [h] at hk; simp [isPK] at hk⟩

/-- Every run is at most `10·PL/(PL+2)` blocks per second (8.57 at push limit 12). -/
theorem speed_bound_rest_uniform {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hN : 0 < s.N) : AlwaysAtMost c s (10 * c.pushLimit / (c.pushLimit + 2)) := by
  apply (speed_bound_rest hW hL hN).mono
  have hKN : ((s.cls isPK).card : ℚ) ≤ s.N := by exact_mod_cast pistons_le_N s
  have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
  have hPL : (0 : ℚ) ≤ c.pushLimit := by positivity
  have hK0 : (0 : ℚ) ≤ (s.cls isPK).card := by positivity
  rw [div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hPL hK0, mul_nonneg hPL (sub_nonneg.mpr hKN),
    mul_nonneg (mul_nonneg hPL hPL) (sub_nonneg.mpr hKN)]

/-- At push limit 12, a flyer with at least 6 blocks per piston never beats 5 blocks per
second. -/
theorem pl12_five_bps_of_ratio {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hN : 0 < s.N) (hPL : c.pushLimit = 12) (hratio : 6 * (s.cls isPK).card ≤ s.N) :
    AlwaysAtMost c s 5 := by
  apply (speed_bound_rest hW hL hN).mono
  rw [hPL]
  have hr : (6 : ℚ) * (s.cls isPK).card ≤ s.N := by exact_mod_cast hratio
  have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
  have hK0 : (0 : ℚ) ≤ (s.cls isPK).card := by positivity
  rw [div_le_iff₀ (by positivity)]
  push_cast
  nlinarith

/-- At push limit 12 nothing goes 9 blocks per second... in fact nothing beats 60/7 ≈ 8.57. -/
theorem pl12_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 12) : AlwaysAtMost c s (60 / 7) := by
  have := speed_bound_rest_uniform hW hL hN
  rw [hPL] at this
  norm_num at this
  exact this

end FF
