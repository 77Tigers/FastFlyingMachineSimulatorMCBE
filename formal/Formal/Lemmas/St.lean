/-
Cell-level rewriting rules for the state operations of `Formal/Sim.lean`.
-/
import Formal.Sim

namespace FF

open Std

@[simp] theorem compare_pos_eq_iff {a b : Pos} : compare a b = .eq ↔ a = b :=
  compare_eq_iff_eq

@[simp] theorem compare_pos_ne_eq {a b : Pos} : (compare a b != .eq) = (a != b) := by
  by_cases h : a = b
  · subst h
    have : compare a a = .eq := Std.ReflCmp.compare_self
    rw [this]; simp
  · have : compare a b ≠ .eq := fun e => h (compare_eq_iff_eq.mp e)
    have h1 : (compare a b != Ordering.eq) = true := bne_iff_ne.mpr this
    have h2 : (a != b) = true := bne_iff_ne.mpr h
    rw [h1, h2]

namespace St

variable {s : St} {p q : Pos} {b : Block}

theorem get_set : (s.set p b).get q = if p = q then some b else s.get q := by
  simp [set, get, ExtTreeMap.getElem?_insert]

@[simp] theorem get_set_self : (s.set p b).get p = some b := by simp [get_set]

theorem get_set_ne (h : p ≠ q) : (s.set p b).get q = s.get q := by simp [get_set, h]

theorem get_remove : (s.remove p).get q = if p = q then none else s.get q := by
  simp [remove, get, ExtTreeMap.getElem?_erase]

@[simp] theorem get_remove_self : (s.remove p).get p = none := by simp [get_remove]

theorem get_remove_ne (h : p ≠ q) : (s.remove p).get q = s.get q := by simp [get_remove, h]

/-- `setList` never changes the blocks. -/
theorem setList_world {c : Config} {l : List Pos} {s' : St}
    (h : s.setList c p l = .ok s') : s'.world = s.world := by
  unfold setList at h
  split at h
  · split at h
    · cases h
    · split at h
      · cases h
      · dsimp only at h
        split at h
        · cases h
        · split at h <;> (cases h; rfl)
  · cases h

theorem setList_get {c : Config} {l : List Pos} {s' : St}
    (h : s.setList c p l = .ok s') : s'.get q = s.get q := by
  simp [get, setList_world h]

/-- `setList` succeeds only on a piston. -/
theorem setList_owner {c : Config} {l : List Pos} {s' : St}
    (h : s.setList c p l = .ok s') : ∃ b, s.get p = some b ∧ b.isPiston = true := by
  unfold setList at h
  split at h
  · rename_i b hb
    split at h
    · cases h
    · rename_i hp
      exact ⟨b, hb, by simpa using hp⟩
  · cases h

end St

namespace Ctx

variable {cx : Ctx} {p q : Pos} {b : Block}

@[simp] theorem removeIndexed_st : (cx.removeIndexed p).st = cx.st.remove p := rfl
@[simp] theorem placeIndexed_st : (cx.placeIndexed p b).st = cx.st.set p b := rfl

theorem removeIndexed_powered :
    (cx.removeIndexed p).powered.contains q = (cx.powered.contains q && p != q) := by
  simp [removeIndexed, ExtTreeSet.contains_erase]
  cases cx.powered.contains q <;> simp

theorem placeIndexed_powered :
    (cx.placeIndexed p b).powered.contains q = (cx.powered.contains q && p != q) := by
  simp [placeIndexed, ExtTreeSet.contains_erase]
  cases cx.powered.contains q <;> simp

end Ctx

/-- Power is only ever lost during a tick: the cache shrinks. -/
theorem Ctx.removeIndexed_powered_le {cx : Ctx} {p q : Pos} :
    (cx.removeIndexed p).powered.contains q = true → cx.powered.contains q = true := by
  simp [Ctx.removeIndexed_powered]; intro h _; exact h

theorem Ctx.placeIndexed_powered_le {cx : Ctx} {p q : Pos} {b : Block} :
    (cx.placeIndexed p b).powered.contains q = true → cx.powered.contains q = true := by
  simp [Ctx.placeIndexed_powered]; intro h _; exact h

end FF
