/-
Without power sources nothing flies. If no state of a run holds an end rod, a redstone block or
an observer, no piston is ever powered, so every extension uses up an angry token (a piston
that failed while powered). Tokens are never created without power, so there are at most `K`
extensions in the whole run, hence at most `2K` moves of at most `PL` blocks each.
-/
import Formal.SpeedRest

namespace FF

open Std

/-- No end rod, redstone block or observer. -/
def NoPow (s : St) : Prop :=
  ∀ q b, s.get q = some b → b.kind ≠ .rod ∧ b.kind ≠ .redstone ∧ b.kind ≠ .observer

theorem hardPowered_noPow {s : St} (h : NoPow s) (t : Pos) : hardPowered s t = false := by
  unfold hardPowered
  split
  · rw [Bool.and_eq_false_iff]; right
    rw [List.any_eq_false]
    intro d _
    split
    · rename_i e hg; have := (h _ _ hg).1; simp [Block.kind] at this
    · rename_i e hg; have := (h _ _ hg).2.2; simp [Block.kind] at this
    · simp
  · rfl

theorem pistonPowered_noPow {s : St} (h : NoPow s) (p : Pos) : pistonPowered s p = false := by
  unfold pistonPowered
  split
  · rw [List.any_eq_false]
    intro e _
    rw [hardPowered_noPow h]
    split
    · rename_i nb hg
      obtain ⟨h1, h2, h3⟩ := h _ _ hg
      simp [h1, h2, h3]
    · simp
  · rfl

/-- Power is local: a piston with no end rod, redstone block or observer next to it, and no end
rod or observer two steps away, is not powered. -/
theorem pistonPowered_local {s : St} {p : Pos}
    (h1 : ∀ e b, s.get (p.add e) = some b →
      b.kind ≠ .rod ∧ b.kind ≠ .redstone ∧ b.kind ≠ .observer)
    (h2 : ∀ e f b, s.get ((p.add e).add f) = some b → b.kind ≠ .rod ∧ b.kind ≠ .observer) :
    pistonPowered s p = false := by
  unfold pistonPowered
  split
  · rw [List.any_eq_false]
    intro e _
    have hhp : hardPowered s (p.add e) = false := by
      unfold hardPowered
      split
      · rw [Bool.and_eq_false_iff]; right
        rw [List.any_eq_false]
        intro d _
        split
        · rename_i e' hg; have := (h2 _ _ _ hg).1; simp [Block.kind] at this
        · rename_i e' hg; have := (h2 _ _ _ hg).2; simp [Block.kind] at this
        · simp
      · rfl
    rw [hhp]
    split
    · rename_i nb hg
      obtain ⟨k1, k2, k3⟩ := h1 _ _ hg
      simp [k1, k2, k3]
    · simp
  · rfl

theorem pw_noPow {s : St} (h : NoPow s) (q : Pos) : (powerStage s).2.contains q = false := by
  cases hc : (powerStage s).2.contains q
  · rfl
  · have := powerStage_pw_powered hc
    rw [pistonPowered_noPow h] at this; cases this

/-- The run-level arithmetic: `phi + PL·(2·tokens + n1 + n2)` never rises. -/
theorem counting_np (PL K T : Nat) (a b c g lt : Nat → Nat) (phi : Nat → Int)
    (hrest : ∀ t, a (t + 1) + g (t + 1) ≤ g t)
    (hhi : ∀ t, b (t + 1) + c (t + 1) ≤ a t + b t)
    (hphi : ∀ t, phi (t + 1) ≤ phi t + lt (t + 1))
    (hlt : ∀ t, lt t ≤ PL * (a t + c t))
    (hg0 : g 0 ≤ K) (ha0 : a 0 ≤ K) (hb0 : b 0 ≤ K) :
    phi T ≤ phi 0 + 4 * PL * K := by
  have key : ∀ t, phi t + PL * (2 * g t + a t + b t : Int) ≤ phi 0 + PL * (2 * g 0 + a 0 + b 0 : Int) := by
    intro t
    induction t with
    | zero => exact _root_.le_refl _
    | succ t ih =>
      have h1 := hrest t
      have h2 := hhi t
      have h3 := hphi t
      have h4 := hlt (t + 1)
      have hPL : (0 : Int) ≤ PL := by omega
      have : (a (t + 1) + c (t + 1) : Int) + (2 * g (t + 1) + a (t + 1) + b (t + 1)) ≤
          2 * g t + a t + b t := by omega
      have h5 := mul_le_mul_of_nonneg_left this hPL
      have h4' : (lt (t + 1) : Int) ≤ PL * (a (t + 1) + c (t + 1)) := by exact_mod_cast h4
      nlinarith
  have := key T
  have hPL : (0 : Int) ≤ PL := by omega
  have h0 : (2 * g 0 + a 0 + b 0 : Int) ≤ 4 * K := by omega
  have h6 := mul_le_mul_of_nonneg_left h0 hPL
  have h7 : (0 : Int) ≤ PL * (2 * g T + a T + b T) :=
    mul_nonneg hPL (by positivity)
  nlinarith

/-- A run in which no state holds a power source keeps `N · (min X) ≤ Φ₀ + 4·PL·K`. -/
theorem noPow_bounded {c : Config} {o : Oracle} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hNP : ∀ t, NoPow (stateAt c o s t)) (t : Nat) {x : Int}
    (hx : (stateAt c o s t).minX? = some x) :
    (s.N : Int) * x ≤ s.phi + 4 * c.pushLimit * (s.cls isPK).card := by
  have hspec := stateAt_spec (o := o) hW hL
  have hR2 := stateAt_tick (o := o) hW hL
  have hNc : ∀ i, (stateAt c o s i).N = s.N := by
    intro i
    induction i with
    | zero => rfl
    | succ i ih => rw [(hspec i).2.2.2.count, ih]
  have hKc : ∀ i, ((stateAt c o s i).cls isPK).card = (s.cls isPK).card := by
    intro i
    induction i with
    | zero => rfl
    | succ i ih => rw [(hR2 i).kc, ih]
  have hpart := pistons_partition hW
  have key := counting_np c.pushLimit (s.cls isPK).card t
    (fun i => (stateAt c o s i).nState 1) (fun i => (stateAt c o s i).nState 2)
    (fun i => (stateAt c o s i).nState 3) (fun i => (stateAt c o s i).tokens)
    (fun i => (stateAt c o s i).listTotal) (fun i => (stateAt c o s i).phi)
    (fun i => (hR2 i).restU (pw_noPow (hNP i)))
    (fun i => (hR2 i).hi) (fun i => (hspec i).2.2.2.phi)
    (fun i => listTotal_le (hspec i).2.1 (hspec i).2.2.1)
    (tokens_le hW) (by simp only [stateAt]; omega) (by simp only [stateAt]; omega)
  have := minX_mul_le hx
  rw [hNc t] at this
  simp only [stateAt] at key
  exact this.trans key

end FF
