/-
The speed bound and its consequences (statements in `Formal/Speed.lean`, proof outline in
`Formal/Theorems.lean`).
-/
import Formal.Theorems
import Mathlib.Algebra.Order.Floor.Semiring
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Data.Rat.Floor

namespace FF

open Std

/-! ### No non-arm blocks: nothing ever moves -/

theorem candidates_nil {c : Config} {s : St} {ch : Chunk} (hN : s.N = 0) :
    candidates c s ch = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro q hq
  obtain ⟨⟨b, hb, hp, -⟩, -⟩ := mem_candidates.mp hq
  have : q ∈ s.body := St.mem_body.mpr ⟨b, hb, by
    intro hk; simp [Block.isPiston, hk] at hp⟩
  unfold St.N at hN
  rw [Finset.card_eq_zero] at hN
  rw [hN] at this; simp at this

theorem tick_no_body {c : Config} {o : TickOracle} {s : St} (hW : Wf s) (hN : s.N = 0) :
    tick c o s = .ok (tickStart s) := by
  have hN0 : (tickStart s).N = 0 := by rw [(tickStart_count hW).1, hN]
  have key : ∀ (order : List Chunk) (pw : ExtTreeSet Pos),
      order.foldlM (fun cx ch =>
        (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx)
        (⟨tickStart s, pw⟩ : Ctx) = .ok ⟨tickStart s, pw⟩ := by
    intro order pw
    induction order with
    | nil => rfl
    | cons ch order ih =>
      simp only [List.foldlM_cons]
      have hnil : (o.pistons (tickStart s) ch (candidates c (tickStart s) ch)).val = [] := by
        have hp := (o.pistons (tickStart s) ch (candidates c (tickStart s) ch)).property
        exact List.Perm.eq_nil (hp.trans (List.perm_nil.mpr (candidates_nil hN0)))
      simp only [hnil, List.foldlM_nil]
      exact ih
  unfold tick
  simp only [bind, Except.bind, pure, Except.pure]
  rw [show clearAngry (powerStage s).1 (powerStage s).2 = tickStart s from rfl, key]

theorem minX_tickStart (s : St) : (tickStart s).minX? = s.minX? := by
  simp [St.minX?, tickStart, clearAngry, powerStage, ExtTreeMap.keys_map]

/-! ### The speed bound -/

/-- From a well-formed state, every run under every oracle has speed at most
`20·PL/(2·PL+3)` blocks per second, up to a constant. -/
theorem speed_bound {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) :
    AlwaysAtMost c s (20 * c.pushLimit / (2 * c.pushLimit + 3)) := by
  set PL := c.pushLimit
  have hK : (0 : ℚ) < 2 * PL + 3 := by positivity
  by_cases hN : s.N = 0
  · refine ⟨0, ?_⟩
    rintro o t d ⟨s', x, x', hrun, hx, hx', hd⟩
    -- nothing moves: the minimum X stays
    have hst : ∀ t, (stateAt c o s t).minX? = s.minX? ∧ (stateAt c o s t).N = 0 := by
      intro t
      induction t with
      | zero => exact ⟨rfl, hN⟩
      | succ t ih =>
        obtain ⟨-, hWt, -, hR⟩ := stateAt_spec (o := o) hW hL t
        have h1 : stateAt c o s (t + 1) = tickStart (stateAt c o s t) := by
          simp [stateAt, tick_no_body hWt ih.2]
        exact ⟨by rw [h1, minX_tickStart, ih.1], by rw [hR.count, ih.2]⟩
    have hs' : s' = stateAt c o s t := by
      have := (stateAt_spec (o := o) hW hL t).1
      rw [hrun] at this; cases this; rfl
    rw [hs', (hst t).1, hx] at hx'
    cases hx'
    have : (0 : ℚ) ≤ 20 * PL / (2 * PL + 3) / 10 * t := by positivity
    have : d ≤ 0 := by simpa using hd
    linarith
  · have hNpos : 0 < s.N := Nat.pos_of_ne_zero hN
    obtain ⟨m0, hm0⟩ := minX_some_of_body hNpos
    refine ⟨(s.phi : ℚ) / s.N - m0 + 1, ?_⟩
    rintro o t d ⟨s', x, x', hrun, hx, hx', hd⟩
    rw [hm0] at hx; cases hx
    have hs' : s' = stateAt c o s t := by
      have := (stateAt_spec (o := o) hW hL t).1
      rw [hrun] at this; cases this; rfl
    subst hs'
    have hspec := stateAt_spec (o := o) hW hL
    -- N is constant
    have hNc : ∀ i, (stateAt c o s i).N = s.N := by
      intro i
      induction i with
      | zero => rfl
      | succ i ih => rw [(hspec i).2.2.2.count, ih]
    -- the X sum
    have hphi : ∀ i, (stateAt c o s i).phi ≤
        s.phi + ∑ j ∈ Finset.range i, ((stateAt c o s (j + 1)).listTotal : Int) := by
      intro i
      induction i with
      | zero => simp [stateAt]
      | succ i ih =>
        rw [Finset.sum_range_succ]
        have := (hspec i).2.2.2.phi
        linarith
    have hcount := counting PL s.N t (fun i => (stateAt c o s i).listTotal)
      (fun i => (stateAt c o s i).nState 1) (fun i => (stateAt c o s i).nState 2)
      (fun i => (stateAt c o s i).nState 3)
      (fun i => listTotal_le (hspec i).2.1 (hspec i).2.2.1)
      (fun i => by
        have := listTotal_add_le (hspec i).2.1 (hspec i).2.2.1
        rw [hNc i] at this; exact this)
      (fun i => (hspec i).2.2.2.n1_le) (fun i => (hspec i).2.2.2.n3_le)
    have hmin := minX_mul_le hx'
    rw [hNc t] at hmin
    -- to the rationals
    set Λ : Nat := ∑ j ∈ Finset.range t, (stateAt c o s (j + 1)).listTotal with hΛdef
    have h1 : (s.N : ℚ) * x' ≤ s.phi + Λ := by
      have h3 := hphi t
      have h4 : (s.N : Int) * x' ≤ s.phi + (Λ : Int) := by
        have : ((Λ : Nat) : Int) =
            ∑ j ∈ Finset.range t, ((stateAt c o s (j + 1)).listTotal : Int) := by
          rw [hΛdef]; push_cast; rfl
        rw [this]; linarith
      exact_mod_cast h4
    have h2 : ((2 * PL + 3 : ℕ) : ℚ) * Λ ≤ ((2 * PL * s.N * (t + 1) : ℕ) : ℚ) := by
      exact_mod_cast hcount
    push_cast at h2
    have hNq : (0 : ℚ) < s.N := by exact_mod_cast hNpos
    have hx'1 : (x' : ℚ) ≤ s.phi / s.N + Λ / s.N := by
      rw [← add_div, le_div_iff₀ hNq]; linarith
    have hΛN : (Λ : ℚ) / s.N ≤ 2 * PL * (t + 1) / (2 * PL + 3) := by
      rw [div_le_div_iff₀ hNq hK]; nlinarith
    have hfrac : (2 * PL : ℚ) / (2 * PL + 3) ≤ 1 := by
      rw [div_le_one hK]; linarith
    have hv : (20 * PL : ℚ) / (2 * PL + 3) / 10 * t + 2 * PL / (2 * PL + 3) =
        2 * PL * (t + 1) / (2 * PL + 3) := by
      field_simp; ring
    have : d ≤ (x' : ℚ) - m0 := by exact_mod_cast hd
    linarith

/-! ### Consequences -/

theorem not_faster_of_alwaysAtMost {c : Config} {s : St} {v v' : ℚ} (h : AlwaysAtMost c s v)
    (hv : v ≤ v') : ¬ CanBeFasterThan c s v' := by
  obtain ⟨C, hC⟩ := h
  rintro ⟨o, ε, hε, hT⟩
  obtain ⟨t, ht, hadv⟩ := hT (⌈C / ε⌉₊ + 1)
  have hle := hC o t _ hadv
  have ht' : (C / ε : ℚ) < t := by
    have h1 := Nat.le_ceil (C / ε)
    have h2 : ((⌈C / ε⌉₊ + 1 : ℕ) : ℚ) ≤ t := by exact_mod_cast ht
    push_cast at h2
    linarith
  have htnn : (0 : ℚ) ≤ t := by positivity
  have h3 : ε * t ≤ C := by nlinarith
  have h4 : C < ε * t := by rwa [div_lt_iff₀ hε, mul_comm] at ht'
  linarith

/-- Nothing goes 10 blocks per second, at any push limit. -/
theorem no_flyer_10bps {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) :
    ¬ CanBeFasterThan c s 10 := by
  apply not_faster_of_alwaysAtMost (speed_bound hW hL)
  rw [div_le_iff₀ (by positivity)]
  linarith

/-- Nothing goes faster than 9 blocks per second at a push limit of 13 or less (the
warm-up: in particular at push limit 5). -/
theorem no_flyer_9bps {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s)
    (hPL : c.pushLimit ≤ 13) : ¬ CanBeFasterThan c s 9 := by
  apply not_faster_of_alwaysAtMost (speed_bound hW hL)
  rw [div_le_iff₀ (by positivity)]
  have : (c.pushLimit : ℚ) ≤ 13 := by exact_mod_cast hPL
  linarith

theorem Buildable.listsOK {c : Config} {s : St} (h : Buildable s) : ListsOK c s := by
  intro p L hL; rw [h.no_lists p] at hL; cases hL

/-- The bound for every buildable start state. -/
theorem buildable_speed_bound {c : Config} {s : St} (h : Buildable s) :
    AlwaysAtMost c s (20 * c.pushLimit / (2 * c.pushLimit + 3)) :=
  speed_bound h.wf h.listsOK

/-- The warm-up: from a buildable state at push limit 5, no run beats 9 bps. -/
theorem buildable_no_9bps_pl5 {c : Config} {s : St} (h : Buildable s) (hPL : c.pushLimit = 5) :
    ¬ CanBeFasterThan c s 9 :=
  no_flyer_9bps h.wf h.listsOK (by omega)

end FF
