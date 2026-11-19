/-
Main results.

`speed_bound`: from any well-formed state (in particular any buildable one), every run,
under every oracle, has speed at most `20·PL / (2·PL + 3)` blocks per second up to a
constant, where `PL` is the push limit. Consequences: no flyer goes 10 bps at any push
limit, and none goes faster than 9 bps at a push limit of 13 or less (so not at 5).

Proof outline (see the lemma files):
* every tick keeps `Wf`, never fails, and keeps the number `N` of non-arm blocks;
* the X sum `Φ` of the non-arm blocks rises per tick by at most the number of cells in
  piston lists afterwards (blocks moved this tick); each of those is a moving block;
* per piston in state 1 or 3 at most `PL` listed cells; listed cells and pistons in
  states 1, 2, 3 are distinct non-arm blocks, so together at most `N`;
* a piston in state 1 is in state 2 one tick later, and one in state 3 was in state 2
  one tick earlier: every push or pull keeps its piston frozen for about 1.5 ticks;
* summing over the run and using min X ≤ Φ / N gives the bound.
-/
import Formal.Lemmas.Static
import Formal.Speed
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Algebra.Group.Action.Defs

namespace FF

open Std

/-! ### The states of a run -/

/-- The state after `t` ticks (the previous state if a tick failed, which never happens on
well-formed states). -/
def stateAt (c : Config) (o : Oracle) (s : St) : Nat → St
  | 0 => s
  | t + 1 =>
    match tick c (o t) (stateAt c o s t) with
    | .ok s' => s'
    | .error _ => stateAt c o s t

theorem stateAt_spec {c : Config} {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s) :
    ∀ t, run c o s t = .ok (stateAt c o s t) ∧ Wf (stateAt c o s t) ∧
      ListsOK c (stateAt c o s t) ∧ TickResult c (stateAt c o s t) (stateAt c o s (t + 1)) := by
  intro t
  induction t with
  | zero =>
    obtain ⟨s', h, hR⟩ := tick_spec hW hL (o 0)
    refine ⟨rfl, hW, hL, ?_⟩
    have : stateAt c o s 1 = s' := by simp [stateAt, h]
    rw [this]; exact hR
  | succ t ih =>
    obtain ⟨hrun, hWt, hLt, hR⟩ := ih
    have hW' := hR.wf
    have hL' := hR.lok
    have htick : tick c (o t) (stateAt c o s t) = .ok (stateAt c o s (t + 1)) := by
      obtain ⟨s', h, -⟩ := tick_spec hWt hLt (o t)
      have : stateAt c o s (t + 1) = s' := by simp [stateAt, h]
      rw [this, h]
    refine ⟨?_, hW', hL', ?_⟩
    · show (do tick c (o t) (← run c o s t)) = _
      rw [hrun]
      exact htick
    · obtain ⟨s', h, hR'⟩ := tick_spec hW' hL' (o (t + 1))
      have : stateAt c o s (t + 2) = s' := by
        show (match tick c (o (t + 1)) (stateAt c o s (t + 1)) with
          | .ok s' => s' | .error _ => stateAt c o s (t + 1)) = s'
        rw [h]
      rw [this]; exact hR'

/-! ### The counting argument -/

theorem sum_shift (f : Nat → Nat) (T : Nat) :
    (∑ i ∈ Finset.range T, f (i + 1)) + f 0 = (∑ i ∈ Finset.range T, f i) + f T := by
  induction T with
  | zero => simp
  | succ T ih => rw [Finset.sum_range_succ, Finset.sum_range_succ]; omega

/-- Summing the per-tick inequalities over `T` ticks. -/
theorem counting (PL N T : Nat) (l a b cc : Nat → Nat)
    (S1 : ∀ t, l t ≤ PL * (a t + cc t)) (S2 : ∀ t, l t + a t + b t + cc t ≤ N)
    (A1 : ∀ t, a t ≤ b (t + 1)) (A2 : ∀ t, cc (t + 1) ≤ b t) :
    (2 * PL + 3) * (∑ i ∈ Finset.range T, l (i + 1)) ≤ 2 * PL * N * (T + 1) := by
  set L := ∑ i ∈ Finset.range T, l (i + 1)
  set A := ∑ i ∈ Finset.range T, a (i + 1)
  set B := ∑ i ∈ Finset.range T, b (i + 1)
  set C := ∑ i ∈ Finset.range T, cc (i + 1)
  have hi : L + A + B + C ≤ N * T := by
    have : ∑ i ∈ Finset.range T, (l (i + 1) + a (i + 1) + b (i + 1) + cc (i + 1)) ≤
        ∑ _i ∈ Finset.range T, N := Finset.sum_le_sum fun i _ => S2 (i + 1)
    simp only [Finset.sum_add_distrib, Finset.sum_const, Finset.card_range, smul_eq_mul] at this
    rw [Nat.mul_comm T N] at this
    exact this
  have hii : L ≤ PL * (A + C) := by
    have : ∑ i ∈ Finset.range T, l (i + 1) ≤ ∑ i ∈ Finset.range T, PL * (a (i + 1) + cc (i + 1)) :=
      Finset.sum_le_sum fun i _ => S1 (i + 1)
    rw [← Finset.mul_sum, Finset.sum_add_distrib] at this
    exact this
  have h3 : A ≤ B + N := by
    have e := sum_shift a T
    have : ∑ i ∈ Finset.range T, a i ≤ B := Finset.sum_le_sum fun i _ => A1 i
    have := S2 T
    omega
  have h4 : C ≤ B + N := by
    have e := sum_shift b T
    have : C ≤ ∑ i ∈ Finset.range T, b i := Finset.sum_le_sum fun i _ => A2 i
    have := S2 0
    omega
  have h5 : 2 * L + 3 * (A + C) ≤ 2 * (N * T) + 2 * N := by omega
  have h6 := Nat.mul_le_mul_left PL h5
  nlinarith [h6, hii]

/-! ### Minimum X and the average -/

theorem keys_x_ge {s : St} {m : Int} (hm : s.minX? = some m) {q : Pos} (hq : q ∈ s.body) :
    m ≤ q.x := by
  unfold St.minX? at hm
  have := (List.min?_eq_some_iff.mp hm).2
  apply this
  obtain ⟨b, hb, -⟩ := St.mem_body.mp hq
  apply List.mem_map.mpr
  refine ⟨q, ?_, rfl⟩
  rw [ExtTreeMap.mem_keys]
  exact ExtTreeMap.mem_iff_isSome_getElem?.mpr (by simp [St.get] at hb; simp [hb])

theorem minX_mul_le {s : St} {m : Int} (hm : s.minX? = some m) : (s.N : Int) * m ≤ s.phi := by
  unfold St.N St.phi
  have : ∑ _q ∈ s.body, m ≤ ∑ q ∈ s.body, q.x := Finset.sum_le_sum fun q hq => keys_x_ge hm hq
  simpa [Finset.sum_const, nsmul_eq_mul] using this

theorem minX_some_of_body {s : St} (hN : 0 < s.N) : ∃ m, s.minX? = some m := by
  unfold St.N at hN
  obtain ⟨q, hq⟩ := Finset.card_pos.mp hN
  obtain ⟨b, hb, -⟩ := St.mem_body.mp hq
  unfold St.minX?
  cases h : (s.world.keys.map (·.x)).min? with
  | some m => exact ⟨m, rfl⟩
  | none =>
    rw [List.min?_eq_none_iff] at h
    have : q ∈ s.world.keys := by
      rw [ExtTreeMap.mem_keys]
      exact ExtTreeMap.mem_iff_isSome_getElem?.mpr (by simp [St.get] at hb; simp [hb])
    have := List.mem_map_of_mem (f := (·.x)) this
    rw [h] at this; simp at this

end FF
