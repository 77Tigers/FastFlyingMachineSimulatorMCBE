/-
The run-level counting behind the forward-move speed bound (pure arithmetic): as
`counting2`, but only the forward cells count, at most `PL` per `+X` piston in state 1
(`ap`) and per `-X` piston in state 3 (`cn`), and the `-X` pistons in states 2, 3 after a tick
were in states 1, 2 before (`an`, `bn`, `cn`).

Conclusion: `(4N + PL*K) * x ≤ PL*K*T + const`.
-/
import Formal.Counting2
import Mathlib.Tactic.LinearCombination

namespace FF

set_option maxHeartbeats 1000000 in
theorem counting3 (PL K N T : Nat) (a b c m z g : Nat → Nat) (ap an bn cn : Nat → Nat)
    (lf psi phi : Nat → Int)
    (hpart : ∀ t, z t + a t + b t + c t + m t = K)
    (hrest : ∀ t, a (t + 1) + g (t + 1) ≤ z t + g t)
    (hg : ∀ t, g t ≤ K)
    (h12 : ∀ t, a t ≤ b (t + 1))
    (h23lo : ∀ t, a t + b t ≤ b (t + 1) + c (t + 1))
    (h23hi : ∀ t, b (t + 1) + c (t + 1) ≤ a t + b t)
    (hpsi : ∀ t, psi (t + 1) ≤ psi t + m (t + 1))
    (hphi : ∀ t, phi (t + 1) ≤ phi t + lf (t + 1))
    (hlf : ∀ t, lf t ≤ PL * (ap t + cn t))
    (hapn : ∀ t, ap t + an t ≤ a t)
    (han : ∀ t, an t ≤ K) (hbn : ∀ t, bn t ≤ K)
    (hhiN : ∀ t, bn (t + 1) + cn (t + 1) ≤ an t + bn t)
    (x : Int) (hN : (N : Int) * x ≤ phi T) (hK : (K : Int) * x ≤ psi T) :
    (4 * N + PL * K : Int) * x ≤
      PL * K * T + 4 * phi 0 + PL * psi 0 + 16 * PL * K := by
  have hpartI : ∀ t, (z t : Int) + a t + b t + c t + m t = K := by
    intro t; exact_mod_cast hpart t
  have hrestI : ∀ t, (a (t + 1) : Int) + g (t + 1) ≤ z t + g t := by
    intro t; exact_mod_cast hrest t
  have hgI : ∀ t, (g t : Int) ≤ K := by intro t; exact_mod_cast hg t
  have h12I : ∀ t, (a t : Int) ≤ b (t + 1) := by intro t; exact_mod_cast h12 t
  have h23loI : ∀ t, (a t : Int) + b t ≤ b (t + 1) + c (t + 1) := by
    intro t; exact_mod_cast h23lo t
  have h23hiI : ∀ t, (b (t + 1) : Int) + c (t + 1) ≤ a t + b t := by
    intro t; exact_mod_cast h23hi t
  have hpsiI : ∀ t, psi (t + 1) ≤ psi t + (m (t + 1) : Int) := hpsi
  have hKa : ∀ t, (a t : Int) ≤ K := by
    intro t; have := hpartI t
    have : (0:Int) ≤ z t := by positivity
    have : (0:Int) ≤ b t := by positivity
    have : (0:Int) ≤ c t := by positivity
    have : (0:Int) ≤ m t := by positivity
    linarith [hpartI t]
  have hKb : ∀ t, (b t : Int) ≤ K := by
    intro t
    have : (0:Int) ≤ z t := by positivity
    have : (0:Int) ≤ a t := by positivity
    have : (0:Int) ≤ c t := by positivity
    have : (0:Int) ≤ m t := by positivity
    linarith [hpartI t]
  have hKm : ∀ t, (m t : Int) ≤ K := by
    intro t
    have : (0:Int) ≤ z t := by positivity
    have : (0:Int) ≤ a t := by positivity
    have : (0:Int) ≤ c t := by positivity
    have : (0:Int) ≤ b t := by positivity
    linarith [hpartI t]
  have hKc : ∀ t, (c t : Int) ≤ K := by
    intro t
    have : (0:Int) ≤ z t := by positivity
    have : (0:Int) ≤ a t := by positivity
    have : (0:Int) ≤ m t := by positivity
    have : (0:Int) ≤ b t := by positivity
    linarith [hpartI t]
  have hsA := counting2_aux_shift (fun t => (a t : Int)) T
  have hsB := counting2_aux_shift (fun t => (b t : Int)) T
  have hsC := counting2_aux_shift (fun t => (c t : Int)) T
  have hsM := counting2_aux_shift (fun t => (m t : Int)) T
  have hsG := counting2_aux_shift (fun t => (g t : Int)) T
  have hsP := counting2_aux_shift psi T
  have hsF := counting2_aux_shift phi T
  have hpartS : ∑ t ∈ Finset.range T, ((z t : Int) + a t + b t + c t + m t) = T * K := by
    rw [Finset.sum_congr rfl (fun t _ => hpartI t)]
    simp
  simp only [Finset.sum_add_distrib] at hpartS
  have hrestS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => hrestI t)
  simp only [Finset.sum_add_distrib] at hrestS
  have h12S := Finset.sum_le_sum (s := Finset.range T) (fun t _ => h12I t)
  have h23loS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => h23loI t)
  simp only [Finset.sum_add_distrib] at h23loS
  have h23hiS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => h23hiI t)
  simp only [Finset.sum_add_distrib] at h23hiS
  have hpsiS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => hpsiI t)
  simp only [Finset.sum_add_distrib] at hpsiS
  have hphiS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => hphi t)
  simp only [Finset.sum_add_distrib] at hphiS
  have n0 : ∀ f : Nat → Nat, ∀ t, (0 : Int) ≤ f t := by intro f t; positivity
  have h4E : 4 * ∑ t ∈ Finset.range T, (a (t + 1) : Int) ≤
      T * K - (psi T - psi 0) + 8 * K := by
    have := n0 a 0; have := n0 b 0; have := n0 c 0; have := n0 m 0
    have := n0 a T; have := n0 b T; have := n0 c T; have := n0 m T
    have := n0 g T; have := hgI 0; have := hKa T; have := hKb T; have := hKc T
    have := hKm T; have := hKa 0; have := hKb 0
    linarith
  have hsAn := counting2_aux_shift (fun t => (an t : Int)) T
  have hsBn := counting2_aux_shift (fun t => (bn t : Int)) T
  have hhiS := Finset.sum_le_sum (s := Finset.range T)
    (fun t _ => (show (bn (t + 1) : Int) + cn (t + 1) ≤ an t + bn t by exact_mod_cast hhiN t))
  simp only [Finset.sum_add_distrib] at hhiS
  have hapnS := Finset.sum_le_sum (s := Finset.range T)
    (fun t _ => (show (ap (t + 1) : Int) + an (t + 1) ≤ a (t + 1) by exact_mod_cast hapn (t + 1)))
  simp only [Finset.sum_add_distrib] at hapnS
  have hcn : ∑ t ∈ Finset.range T, (cn (t + 1) : Int) ≤
      ∑ t ∈ Finset.range T, (an (t + 1) : Int) + 2 * K := by
    have := n0 an T; have := n0 bn T
    have : (an 0 : Int) ≤ K := by exact_mod_cast han 0
    have : (bn 0 : Int) ≤ K := by exact_mod_cast hbn 0
    linarith
  have hlfS := Finset.sum_le_sum (s := Finset.range T) (fun t _ => hlf (t + 1))
  rw [← Finset.mul_sum] at hlfS
  simp only [Finset.sum_add_distrib] at hlfS
  push_cast at hlfS
  have hPL : (0 : Int) ≤ PL := by positivity
  have hKK : (0 : Int) ≤ K := by positivity
  have hfw : ∑ t ∈ Finset.range T, (ap (t + 1) : Int) + ∑ t ∈ Finset.range T, (cn (t + 1) : Int) ≤
      ∑ t ∈ Finset.range T, (a (t + 1) : Int) + 2 * K := by linarith
  have hLam := mul_le_mul_of_nonneg_left hfw hPL
  have hphiT' : phi T - phi 0 ≤ ∑ t ∈ Finset.range T, lf (t + 1) := by
    have := hsF
    linarith
  have hE4 := mul_le_mul_of_nonneg_left h4E hPL
  have hKx := mul_le_mul_of_nonneg_left hK hPL
  have hPK : (0 : Int) ≤ PL * K := mul_nonneg hPL hKK
  have hphiT : (N : Int) * x ≤ phi 0 + PL * (∑ t ∈ Finset.range T, (a (t + 1) : Int) + 2 * K) := by
    linarith
  linear_combination 4 * hphiT + hE4 + hKx

end FF
