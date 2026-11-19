import Formal.Sim
open FF Std
example (a b : Pos) : (compare a b != .eq) = (a != b) := by
  by_cases h : a = b
  · subst h
    have : compare a a = .eq := Std.ReflCmp.compare_self
    rw [this]; simp
  · have : compare a b ≠ .eq := fun e => h (compare_eq_iff_eq.mp e)
    have h1 : (compare a b != Ordering.eq) = true := bne_iff_ne.mpr this
    have h2 : (a != b) = true := bne_iff_ne.mpr h
    rw [h1, h2]
