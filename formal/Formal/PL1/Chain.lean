/-
The chain lemma behind "no push limit 1 flyer with only X-facing pistons" (pure combinatorics).

In one row of blocks along X, sorted by X, a block can only be moved forward by the block just
behind it if that one is a `+X` piston (type `P`), or by the block just ahead of it if that one
is a sticky `-X` piston (type `Q`). If some block of the row is neither (type `O`), then some
block of the row has no possible forward mover.
-/
import Mathlib.Data.Finset.Card
import Mathlib.Data.Int.Interval
import Mathlib.Order.Interval.Finset.Nat

namespace FF

inductive Ty
  | P | Q | O
  deriving DecidableEq, Repr

/-- The rank of `a` in `S`: the number of elements of `S` below it. -/
def rkF (S : Finset Int) (a : Int) : Nat := (S.filter (· < a)).card

theorem rkF_lt_card {S : Finset Int} {x : Int} (hx : x ∈ S) : rkF S x < S.card := by
  unfold rkF
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset (Finset.filter_subset _ _)]
  exact ⟨x, hx, by simp⟩

theorem rkF_strictMono {S : Finset Int} {a b : Int} (ha : a ∈ S) (hab : a < b) :
    rkF S a < rkF S b := by
  unfold rkF
  apply Finset.card_lt_card
  rw [Finset.ssubset_iff_of_subset]
  · exact ⟨a, by simp [ha, hab], by simp⟩
  · intro x hx
    simp only [Finset.mem_filter] at hx ⊢
    exact ⟨hx.1, lt_trans hx.2 hab⟩

theorem rkF_injOn (S : Finset Int) : Set.InjOn (rkF S) (S : Set Int) := by
  intro a ha b hb hab
  rcases lt_trichotomy a b with h | h | h
  · exact absurd hab (ne_of_lt (rkF_strictMono ha h))
  · exact h
  · exact absurd hab (ne_of_gt (rkF_strictMono hb h))

theorem rkF_surj (S : Finset Int) : ∀ k < S.card, ∃ x ∈ S, rkF S x = k := by
  have hsub : S.image (rkF S) ⊆ Finset.range S.card := by
    intro k hk
    obtain ⟨x, hx, rfl⟩ := Finset.mem_image.mp hk
    exact Finset.mem_range.mpr (rkF_lt_card hx)
  have heq : S.image (rkF S) = Finset.range S.card :=
    Finset.eq_of_subset_of_card_le hsub (by rw [Finset.card_image_of_injOn (rkF_injOn S)]; simp)
  intro k hk
  have : k ∈ S.image (rkF S) := by rw [heq]; exact Finset.mem_range.mpr hk
  obtain ⟨x, hx, hxk⟩ := Finset.mem_image.mp this
  exact ⟨x, hx, hxk⟩

theorem chain_nat (n : Nat) (t : Nat → Ty) (i : Nat) (hi : i < n) (hO : t i = .O)
    (h : ∀ k < n, (1 ≤ k ∧ t (k - 1) = .P) ∨ (k + 1 < n ∧ t (k + 1) = .Q)) : False := by
  by_cases hA : 1 ≤ i ∧ t (i - 1) = .P
  · have claim : ∀ d j, j < i → i ≤ j + d + 1 → t j = .P := by
      intro d
      induction d with
      | zero =>
        intro j hj1 hj2
        have : i - 1 = j := by omega
        rw [← this]; exact hA.2
      | succ d ih =>
        intro j hj1 hj2
        by_cases hc : i ≤ j + d + 1
        · exact ih j hj1 hc
        · have h2 := h (j + 1) (by omega)
          rcases h2 with ⟨_, h3⟩ | ⟨_, h3⟩
          · simpa using h3
          · exfalso
            by_cases h4 : j + 2 = i
            · rw [show j + 1 + 1 = i by omega, hO] at h3; exact absurd h3 (by decide)
            · have h5 := ih (j + 2) (by omega) (by omega)
              rw [show j + 1 + 1 = j + 2 from rfl, h5] at h3; exact absurd h3 (by decide)
    have h0 := h 0 (by omega)
    rcases h0 with ⟨h1, _⟩ | ⟨_, h3⟩
    · omega
    · by_cases h4 : 1 = i
      · rw [show 0 + 1 = i by omega, hO] at h3; exact absurd h3 (by decide)
      · have h5 := claim i 1 (by omega) (by omega)
        rw [show 0 + 1 = 1 from rfl, h5] at h3; exact absurd h3 (by decide)
  · have hi1 := h i hi
    rcases hi1 with h1 | ⟨hn, h2⟩
    · exact hA h1
    · have claim : ∀ d j, i < j → j < n → j ≤ i + d + 1 → t j = .Q := by
        intro d
        induction d with
        | zero =>
          intro j hj1 hj2 hj3
          rw [show j = i + 1 by omega]; exact h2
        | succ d ih =>
          intro j hj1 hj2 hj3
          by_cases hc : j ≤ i + d + 1
          · exact ih j hj1 hj2 hc
          · have h5 := h (j - 1) (by omega)
            rcases h5 with ⟨_, h3⟩ | ⟨_, h3⟩
            · exfalso
              by_cases h4 : j - 2 = i
              · rw [show j - 1 - 1 = i by omega, hO] at h3; exact absurd h3 (by decide)
              · have h6 := ih (j - 2) (by omega) (by omega) (by omega)
                rw [show j - 1 - 1 = j - 2 from rfl, h6] at h3; exact absurd h3 (by decide)
            · rw [show j - 1 + 1 = j by omega] at h3; exact h3
      have hq := claim n (n - 1) (by omega) (by omega) (by omega)
      have h0 := h (n - 1) (by omega)
      rcases h0 with ⟨_, h3⟩ | ⟨h3, _⟩
      · by_cases h4 : n - 1 - 1 = i
        · rw [h4, hO] at h3; exact absurd h3 (by decide)
        · have h6 := claim n (n - 1 - 1) (by omega) (by omega) (by omega)
          rw [h6] at h3; exact absurd h3 (by decide)
      · omega

theorem chain_stuck (S : Finset Int) (τ : Int → Ty) (a : Int) (ha : a ∈ S) (hO : τ a = .O) :
    ∃ b ∈ S, ¬ ∃ p ∈ S, (rkF S p + 1 = rkF S b ∧ τ p = .P) ∨
      (rkF S p = rkF S b + 1 ∧ τ p = .Q) := by
  classical
  by_contra hcon
  push Not at hcon
  have surj := rkF_surj S
  let t : Nat → Ty := fun k =>
    if hk : k < S.card then τ (Classical.choose (surj k hk)) else .O
  have key : ∀ x ∈ S, t (rkF S x) = τ x := by
    intro x hx
    have hk := rkF_lt_card hx
    simp only [t, hk, dite_true]
    have hs := Classical.choose_spec (surj (rkF S x) hk)
    have : Classical.choose (surj (rkF S x) hk) = x :=
      rkF_injOn S hs.1 hx hs.2
    rw [this]
  refine chain_nat S.card t (rkF S a) (rkF_lt_card ha) (by rw [key a ha, hO]) ?_
  intro k hk
  obtain ⟨b, hb, hbk⟩ := surj k hk
  obtain ⟨p, hp, hpp⟩ := hcon b hb
  have kp := key p hp
  have lp := rkF_lt_card hp
  rcases hpp with ⟨e, hτ⟩ | ⟨e, hτ⟩
  · left
    refine ⟨by omega, ?_⟩
    rw [show k - 1 = rkF S p by omega, kp, hτ]
  · right
    refine ⟨by omega, ?_⟩
    rw [show k + 1 = rkF S p by omega, kp, hτ]

end FF
