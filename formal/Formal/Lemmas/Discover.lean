/-
What a successful discovery guarantees: the moved set is a duplicate-free list of at
most `pushLimit` occupied, movable cells, and the first cell is in it (or empty).
-/
import Formal.Sim

namespace FF

variable {c : Config} {s : St} {first : Pos} {dir : Dir} {owner : Option Pos} {pulling : Bool}
  {l : List Pos}

theorem discover_length_le (h : discover c s first dir owner pulling = some l) :
    l.length ≤ c.pushLimit := by
  unfold discover at h
  split at h
  · cases h; simp
  · split at h
    · cases h
    · split at h
      · cases h
      · dsimp only at h
        split at h
        · cases h
        · rename_i hbad
          cases h
          simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at hbad
          omega

theorem discover_mem (h : discover c s first dir owner pulling = some l) (hp : p ∈ l) :
    ∃ b, s.get p = some b ∧ immovable owner p b = false := by
  unfold discover at h
  split at h
  · cases h; simp at hp
  · split at h
    · cases h
    · split at h
      · cases h
      · rename_i S _
        dsimp only at h
        split at h
        · cases h
        · rename_i hbad
          cases h
          simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at hbad
          have := hbad.1
          simp only [List.any_eq_true, not_exists, not_and] at this
          have hp' := this p hp
          revert hp'
          cases hg : s.get p with
          | none => simp
          | some b => intro hb; exact ⟨b, rfl, by simpa using hb⟩

theorem discover_nodup (h : discover c s first dir owner pulling = some l) : l.Nodup := by
  unfold discover at h
  split at h
  · cases h; simp
  · split at h
    · cases h
    · split at h
      · cases h
      · dsimp only at h
        split at h
        · cases h
        · cases h
          refine (Std.ExtTreeSet.distinct_toList).imp ?_
          intro a b hab heq
          exact hab (by simp [heq])

end FF
