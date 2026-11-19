/-
The moved set is closed: it contains the first block, the occupied destination of every
member, and every movable neighbour a slime/honey member sticks to.
-/
import Formal.Lemmas.Discover
import Formal.Lemmas.St

namespace FF

open Std

theorem Dir.mem_all (e : Dir) : e ∈ Dir.all := by cases e <;> simp [Dir.all]

theorem ExtTreeSet.mem_insert_pos {t : ExtTreeSet Pos} {k a : Pos} :
    a ∈ t.insert k ↔ k = a ∨ a ∈ t := by
  simp [ExtTreeSet.mem_insert]

/-! ### Folds that only insert -/

section Fold
variable {α : Type} {f : ExtTreeSet Pos → α → ExtTreeSet Pos}

theorem foldl_mono (hf : ∀ acc a q, q ∈ acc → q ∈ f acc a) :
    ∀ (l : List α) (acc : ExtTreeSet Pos) (q : Pos), q ∈ acc → q ∈ l.foldl f acc := by
  intro l
  induction l with
  | nil => intro acc q h; exact h
  | cons x xs ih => intro acc q h; exact ih _ _ (hf _ _ _ h)

theorem foldl_mem_of_step (hf : ∀ acc a q, q ∈ acc → q ∈ f acc a) {a : α} {q : Pos}
    (hq : ∀ acc, q ∈ f acc a) :
    ∀ (l : List α) (acc : ExtTreeSet Pos), a ∈ l → q ∈ l.foldl f acc := by
  intro l
  induction l with
  | nil => intro acc h; simp at h
  | cons x xs ih =>
    intro acc h
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp h with h | h
    · subst h; exact foldl_mono hf xs _ _ (hq acc)
    · exact ih _ h

end Fold

/-! ### `expandStep` and `expand` -/

section Expand
variable {s : St} {dir : Dir} {owner : Option Pos}

theorem adhStep_mono {p : Pos} {b : Block} {acc : ExtTreeSet Pos} {e : Dir} {q : Pos}
    (h : q ∈ acc) : q ∈ adhStep s owner p b acc e := by
  unfold adhStep
  split
  · split
    · exact ExtTreeSet.mem_insert_pos.mpr (Or.inr h)
    · exact h
  · exact h

theorem adhesion_mono {acc : ExtTreeSet Pos} {p q : Pos} (h : q ∈ acc) :
    q ∈ adhesion s owner acc p := by
  unfold adhesion
  split
  · split
    · exact foldl_mono (fun _ _ _ hq => adhStep_mono hq) _ _ _ h
    · exact h
  · exact h

theorem expandStep_mono {acc : ExtTreeSet Pos} {p q : Pos} (h : q ∈ acc) :
    q ∈ expandStep s dir owner acc p := by
  unfold expandStep
  dsimp only
  split
  · exact ExtTreeSet.mem_insert_pos.mpr (Or.inr (adhesion_mono h))
  · exact adhesion_mono h

theorem expandStep_dest {acc : ExtTreeSet Pos} {p : Pos} (h : (s.get (p.add dir)).isSome) :
    p.add dir ∈ expandStep s dir owner acc p := by
  unfold expandStep
  simp only [h, ite_true]
  exact ExtTreeSet.mem_insert_pos.mpr (Or.inl rfl)

theorem expandStep_adh {acc : ExtTreeSet Pos} {p : Pos} {b nb : Block} {e : Dir}
    (hb : s.get p = some b) (hk : isGlue b = true)
    (hnb : s.get (p.add e) = some nb) (hm : immovable owner (p.add e) nb = false)
    (ha : adheres b.kind nb.kind = true) :
    p.add e ∈ expandStep s dir owner acc p := by
  have h1 : p.add e ∈ adhesion s owner acc p := by
    unfold adhesion
    rw [hb]
    simp only [hk, ite_true]
    refine foldl_mem_of_step (fun _ _ _ hq => adhStep_mono hq) ?_ _ _ (Dir.mem_all e)
    intro acc
    unfold adhStep
    rw [hnb]
    simp only [hm, ha, Bool.not_false, Bool.and_self, ite_true]
    exact ExtTreeSet.mem_insert_pos.mpr (Or.inl rfl)
  unfold expandStep
  dsimp only
  split
  · exact ExtTreeSet.mem_insert_pos.mpr (Or.inr h1)
  · exact h1

theorem expand_eq (S : ExtTreeSet Pos) :
    expand s dir owner S = S.toList.foldl (expandStep s dir owner) S := by
  simp [expand, ExtTreeSet.foldl_eq_foldl_toList]

theorem mem_expand_self {S : ExtTreeSet Pos} {q : Pos} (h : q ∈ S) : q ∈ expand s dir owner S := by
  rw [expand_eq]
  exact foldl_mono (f := expandStep s dir owner) (fun _ _ _ hq => expandStep_mono hq) _ _ _ h

theorem mem_expand_of_step {S : ExtTreeSet Pos} {p q : Pos} (hp : p ∈ S)
    (hq : ∀ acc, q ∈ expandStep s dir owner acc p) : q ∈ expand s dir owner S := by
  rw [expand_eq]
  exact foldl_mem_of_step (f := expandStep s dir owner) (fun _ _ _ hq => expandStep_mono hq) hq _ _
    (ExtTreeSet.mem_toList.mpr hp)

end Expand

/-! ### `closure` -/

/-- `closure` returns a superset of its start that `expand` cannot enlarge. -/
theorem closure_spec {c : Config} {s : St} {dir : Dir} {owner : Option Pos} :
    ∀ (n : Nat) (S T : ExtTreeSet Pos), closure c s dir owner n S = some T →
      (∀ q, q ∈ expand s dir owner T → q ∈ T) ∧ (∀ q, q ∈ S → q ∈ T) := by
  intro n
  induction n with
  | zero => intro S T h; simp [closure] at h
  | succ n ih =>
    intro S T h
    unfold closure at h
    split at h
    · cases h
    · dsimp only at h
      split at h
      · rename_i hall
        cases h
        refine ⟨?_, fun q hq => hq⟩
        intro q hq
        have := List.all_eq_true.mp hall q (ExtTreeSet.mem_toList.mpr hq)
        exact ExtTreeSet.contains_iff_mem.mp this
      · obtain ⟨h1, h2⟩ := ih _ _ h
        exact ⟨h1, fun q hq => h2 q (mem_expand_self hq)⟩

/-! ### Consequences for `discover` -/

section Discover
variable {c : Config} {s : St} {first : Pos} {dir : Dir} {owner : Option Pos} {pulling : Bool}
  {l : List Pos}

/-- A successful discovery from an occupied cell is a closed set containing that cell. -/
theorem discover_spec (h : discover c s first dir owner pulling = some l)
    (hf : (s.get first).isSome) :
    ∃ T : ExtTreeSet Pos, l = T.toList ∧ first ∈ T ∧
      ∀ q, q ∈ expand s dir owner T → q ∈ T := by
  unfold discover at h
  split at h
  · rename_i hn; rw [hn] at hf; cases hf
  · split at h
    · cases h
    · split at h
      · cases h
      · rename_i T hT
        dsimp only at h
        split at h
        · cases h
        · cases h
          obtain ⟨h1, h2⟩ := closure_spec _ _ _ hT
          exact ⟨T, rfl, h2 _ (by simp), h1⟩

theorem discover_empty (h : discover c s first dir owner pulling = some l)
    (hf : s.get first = none) : l = [] := by
  unfold discover at h
  rw [hf] at h
  cases h; rfl

theorem discover_first_mem (h : discover c s first dir owner pulling = some l)
    (hf : (s.get first).isSome) : first ∈ l := by
  obtain ⟨T, rfl, hT, -⟩ := discover_spec h hf
  exact ExtTreeSet.mem_toList.mpr hT

/-- The occupied destination of a moved block is moved too. -/
theorem discover_dest_mem (h : discover c s first dir owner pulling = some l) {p : Pos}
    (hp : p ∈ l) (hd : (s.get (p.add dir)).isSome) : p.add dir ∈ l := by
  have hf : (s.get first).isSome := by
    cases hg : s.get first with
    | some _ => rfl
    | none => rw [discover_empty h hg] at hp; simp at hp
  obtain ⟨T, rfl, -, hcl⟩ := discover_spec h hf
  have hpT := ExtTreeSet.mem_toList.mp hp
  exact ExtTreeSet.mem_toList.mpr (hcl _ (mem_expand_of_step hpT fun _ => expandStep_dest hd))

/-- A movable neighbour that a moved slime/honey block sticks to is moved too. -/
theorem discover_adh_mem (h : discover c s first dir owner pulling = some l) {p : Pos}
    (hp : p ∈ l) {b nb : Block} {e : Dir} (hb : s.get p = some b) (hk : isGlue b = true)
    (hnb : s.get (p.add e) = some nb) (hm : immovable owner (p.add e) nb = false)
    (ha : adheres b.kind nb.kind = true) : p.add e ∈ l := by
  have hf : (s.get first).isSome := by
    cases hg : s.get first with
    | some _ => rfl
    | none => rw [discover_empty h hg] at hp; simp at hp
  obtain ⟨T, rfl, -, hcl⟩ := discover_spec h hf
  have hpT := ExtTreeSet.mem_toList.mp hp
  exact ExtTreeSet.mem_toList.mpr
    (hcl _ (mem_expand_of_step hpT fun _ => expandStep_adh hb hk hnb hm ha))

end Discover

end FF
