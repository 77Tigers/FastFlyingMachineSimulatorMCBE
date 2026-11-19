/-
The forward-move speed bound: with `K` pistons and `N` blocks (not counting arms), every run
from a well-formed state has speed at most

    10 · PL · K / (PL · K + 4 · N)   blocks per second.

Why: as in `SpeedRest`, every piston completes at most `(1 - v)/4` push-pull cycles per tick.
But of the two moves in a cycle only one can carry blocks forward: a `+X` piston pushes
forward and pulls backward, a `-X` piston pushes backward and pulls forward, and a sideways
piston moves nothing along X. So each cycle raises the X sum by at most `PL`, not `2 · PL`.

Since `K ≤ N`, this is at most `10 · PL / (PL + 4)`: 2 bps at push limit 1, 3.33 at 2,
4.29 at 3, 5 at 4, 7.5 at 12. At push limit 12 a flyer with at least 3 blocks per piston
cannot beat 5 blocks per second.
-/
import Formal.SpeedRest
import Formal.Lemmas.Fwd
import Formal.Counting3

namespace FF

open Std

/-- The forward bound: from a well-formed state with `K` pistons and `N > 0` blocks, every run
has speed at most `10·PL·K / (PL·K + 4·N)` blocks per second, up to a constant. -/
theorem speed_bound_fwd {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N) :
    AlwaysAtMost c s (10 * c.pushLimit * (s.cls isPK).card /
      (c.pushLimit * (s.cls isPK).card + 4 * s.N)) := by
  set PL := c.pushLimit
  set K := (s.cls isPK).card
  set N := s.N
  have hD : (0 : ℚ) < PL * K + 4 * N := by
    have : (0 : ℚ) < N := by exact_mod_cast hN
    positivity
  obtain ⟨m0, hm0⟩ := minX_some_of_body hN
  refine ⟨(4 * s.phi + PL * s.xsum isPK + 16 * PL * K : ℚ) / (PL * K + 4 * N) - m0, ?_⟩
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
  have hpart : ∀ i, (stateAt c o s i).restP.card + (stateAt c o s i).nState 1 +
      (stateAt c o s i).nState 2 + (stateAt c o s i).nState 3 + (stateAt c o s i).movP.card = K := by
    intro i; have := pistons_partition (hspec i).2.1; rw [hKc i] at this; omega
  have key := counting3 PL K N t
    (fun i => (stateAt c o s i).nState 1) (fun i => (stateAt c o s i).nState 2)
    (fun i => (stateAt c o s i).nState 3) (fun i => (stateAt c o s i).movP.card)
    (fun i => (stateAt c o s i).restP.card) (fun i => (stateAt c o s i).tokens)
    (fun i => (stateAt c o s i).nSD 1 .px) (fun i => (stateAt c o s i).nSD 1 .nx)
    (fun i => (stateAt c o s i).nSD 2 .nx) (fun i => (stateAt c o s i).nSD 3 .nx)
    (fun i => (stateAt c o s i).fwdTotal)
    (fun i => (stateAt c o s i).xsum isPK) (fun i => (stateAt c o s i).phi)
    (fun i => by have := hpart i; omega)
    (fun i => (hR2 i).rest)
    (fun i => by rw [← hKc i]; exact tokens_le (hspec i).2.1)
    (fun i => (hspec i).2.2.2.n1_le)
    (fun i => (hR2 i).lo) (fun i => (hR2 i).hi) (fun i => (hR2 i).psi)
    (fun i => (hR2 i).phiF)
    (fun i => fwdTotal_le (hspec i).2.1 (hspec i).2.2.1)
    (fun i => nSD_px_nx_le _ 1)
    (fun i => by have := nSD_le_nState (stateAt c o s i) 1 .nx; have := hpart i; omega)
    (fun i => by have := nSD_le_nState (stateAt c o s i) 2 .nx; have := hpart i; omega)
    (fun i => (hR2 i).hiD .nx)
    x' (by have := minX_mul_le hx'; rw [hNc t] at this; exact this)
    (by have := minX_mul_le_cls hx'; rw [hKc t] at this; exact this)
  have hkey : ((4 * N + PL * K : ℚ)) * x' ≤
      PL * K * t + (4 * s.phi + PL * s.xsum isPK + 16 * PL * K) := by
    have := key
    simp only [stateAt] at this
    have h' : ((4 * N + PL * K : Int) : ℚ) * (x' : ℚ) ≤
        ((PL * K * t + 4 * s.phi + PL * s.xsum isPK + 16 * PL * K : Int) : ℚ) := by
      exact_mod_cast this
    push_cast at h'
    linarith
  have hx'le : (x' : ℚ) ≤ (PL * K * t + (4 * s.phi + PL * s.xsum isPK + 16 * PL * K)) /
      (PL * K + 4 * N) := by
    rw [le_div_iff₀ hD]; linarith
  have hd' : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
  have hsplit : (PL * K * t + (4 * s.phi + PL * s.xsum isPK + 16 * PL * K) : ℚ) /
      (PL * K + 4 * N) = 10 * PL * K / (PL * K + 4 * N) / 10 * t +
      (4 * s.phi + PL * s.xsum isPK + 16 * PL * K) / (PL * K + 4 * N) := by
    field_simp
    try ring
  linarith

/-! ### Consequences -/

/-- Every run is at most `10·PL/(PL+4)` blocks per second. -/
theorem speed_bound_fwd_uniform {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hN : 0 < s.N) : AlwaysAtMost c s (10 * c.pushLimit / (c.pushLimit + 4)) := by
  apply (speed_bound_fwd hW hL hN).mono
  have hKN : ((s.cls isPK).card : ℚ) ≤ s.N := by exact_mod_cast pistons_le_N s
  have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
  have hPL : (0 : ℚ) ≤ c.pushLimit := by positivity
  have hK0 : (0 : ℚ) ≤ (s.cls isPK).card := by positivity
  rw [div_le_div_iff₀ (by positivity) (by positivity)]
  nlinarith [mul_nonneg hPL hK0, mul_nonneg hPL (sub_nonneg.mpr hKN),
    mul_nonneg (mul_nonneg hPL hPL) (sub_nonneg.mpr hKN)]

/-- The uniform bound at a given push limit. -/
theorem speed_bound_pl {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (n : Nat) (hPL : c.pushLimit = n) : AlwaysAtMost c s (10 * n / (n + 4)) := by
  have := speed_bound_fwd_uniform hW hL hN
  rw [hPL] at this
  exact this

/-- Push limit 1: nothing beats 2 blocks per second. -/
theorem pl1_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 1) : AlwaysAtMost c s 2 := by
  have := speed_bound_pl hW hL hN 1 hPL; norm_num at this; exact this

/-- Push limit 2: nothing beats 10/3 blocks per second. -/
theorem pl2_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 2) : AlwaysAtMost c s (10 / 3) := by
  have := speed_bound_pl hW hL hN 2 hPL; norm_num at this; exact this

/-- Push limit 3: nothing beats 30/7 blocks per second. -/
theorem pl3_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 3) : AlwaysAtMost c s (30 / 7) := by
  have := speed_bound_pl hW hL hN 3 hPL; norm_num at this; exact this

/-- Push limit 4: nothing beats 5 blocks per second. -/
theorem pl4_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 4) : AlwaysAtMost c s 5 := by
  have := speed_bound_pl hW hL hN 4 hPL; norm_num at this; exact this

/-- Push limit 5: nothing beats 50/9 blocks per second. -/
theorem pl5_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 5) : AlwaysAtMost c s (50 / 9) := by
  have := speed_bound_pl hW hL hN 5 hPL; norm_num at this; exact this

/-- Push limit 12: nothing beats 7.5 blocks per second. -/
theorem pl12_bound_fwd {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (hN : 0 < s.N)
    (hPL : c.pushLimit = 12) : AlwaysAtMost c s (15 / 2) := by
  have := speed_bound_pl hW hL hN 12 hPL; norm_num at this; exact this

/-- At push limit 12, a flyer with at least 3 blocks per piston never beats 5 blocks per
second. -/
theorem pl12_five_bps_of_ratio3 {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hN : 0 < s.N) (hPL : c.pushLimit = 12) (hratio : 3 * (s.cls isPK).card ≤ s.N) :
    AlwaysAtMost c s 5 := by
  apply (speed_bound_fwd hW hL hN).mono
  rw [hPL]
  have hr : (3 : ℚ) * (s.cls isPK).card ≤ s.N := by exact_mod_cast hratio
  have hN' : (0 : ℚ) < s.N := by exact_mod_cast hN
  have hK0 : (0 : ℚ) ≤ (s.cls isPK).card := by positivity
  rw [div_le_iff₀ (by positivity)]
  push_cast
  nlinarith

end FF
