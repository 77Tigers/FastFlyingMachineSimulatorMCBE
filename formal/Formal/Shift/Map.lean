/-
Relabelling the keys of a tree map or tree set by an order-preserving bijection.
Used to prove that a tick commutes with translating the flyer.
-/
import Formal.Sim
import Mathlib.Logic.Equiv.Defs

namespace FF

open Std

section
variable {α : Type} [Ord α] [TransOrd α] [LawfulEqOrd α] [DecidableEq α]

/-- An order-preserving bijection. -/
structure OIso (α : Type) [Ord α] where
  f : α → α
  g : α → α
  gf : ∀ a, g (f a) = a
  fg : ∀ a, f (g a) = a
  cmp : ∀ a b, compare (f a) (f b) = compare a b

variable (e : OIso α)

theorem OIso.f_inj {a b : α} (h : e.f a = e.f b) : a = b := by
  rw [← e.gf a, ← e.gf b, h]

/-! ### Maps -/

def mapK {β : Type} (m : ExtTreeMap α β) : ExtTreeMap α β :=
  ExtTreeMap.ofList (m.toList.map fun p => (e.f p.1, p.2))

theorem distinct_mapK {β : Type} (m : ExtTreeMap α β) :
    (m.toList.map fun p => (e.f p.1, p.2)).Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) := by
  rw [List.pairwise_map]
  exact (ExtTreeMap.distinct_keys_toList (t := m)).imp fun h => by rw [e.cmp]; exact h

theorem getElem?_mapK {β : Type} (m : ExtTreeMap α β) (k : α) :
    (mapK e m)[k]? = m[e.g k]? := by
  unfold mapK
  cases h : m[e.g k]? with
  | some v =>
    apply ExtTreeMap.getElem?_ofList_of_mem (k := k) (Std.ReflCmp.compare_self) (distinct_mapK e m)
    rw [List.mem_map]
    exact ⟨(e.g k, v), ExtTreeMap.mem_toList_iff_getElem?_eq_some.mpr h, by simp [e.fg]⟩
  | none =>
    apply ExtTreeMap.getElem?_ofList_of_contains_eq_false
    rw [Bool.eq_false_iff]
    intro hc
    rw [List.contains_iff_mem] at hc
    simp only [List.map_map, List.mem_map, Function.comp_apply] at hc
    obtain ⟨p, hp, he⟩ := hc
    have hp' := ExtTreeMap.mem_toList_iff_getElem?_eq_some.mp hp
    rw [← he, e.gf] at h
    rw [h] at hp'; cases hp'

theorem getElem?_mapK_f {β : Type} (m : ExtTreeMap α β) (k : α) :
    (mapK e m)[e.f k]? = m[k]? := by rw [getElem?_mapK, e.gf]

theorem mapK_insert {β : Type} (m : ExtTreeMap α β) (k : α) (v : β) :
    mapK e (m.insert k v) = (mapK e m).insert (e.f k) v := by
  apply ExtTreeMap.ext_getElem?
  intro q
  rw [getElem?_mapK, ExtTreeMap.getElem?_insert, ExtTreeMap.getElem?_insert, getElem?_mapK]
  congr 1
  rw [← e.cmp, e.fg]

theorem mapK_erase {β : Type} (m : ExtTreeMap α β) (k : α) :
    mapK e (m.erase k) = (mapK e m).erase (e.f k) := by
  apply ExtTreeMap.ext_getElem?
  intro q
  rw [getElem?_mapK, ExtTreeMap.getElem?_erase, ExtTreeMap.getElem?_erase, getElem?_mapK]
  congr 1
  rw [← e.cmp, e.fg]

theorem mapK_empty {β : Type} : mapK e (∅ : ExtTreeMap α β) = ∅ := by
  apply ExtTreeMap.ext_getElem?
  intro q; rw [getElem?_mapK]; simp

theorem toList_mapK {β : Type} (m : ExtTreeMap α β) :
    (mapK e m).toList = m.toList.map fun p => (e.f p.1, p.2) := by
  have lt_ne : ∀ a b : α × β, compare a.1 b.1 = .lt → a ≠ b := by
    intro a b h e; subst e
    have h0 : compare a.1 a.1 = .eq := Std.ReflCmp.compare_self
    rw [h0] at h; cases h
  have h1 := ExtTreeMap.ordered_keys_toList (t := mapK e m)
  have h2 : (m.toList.map fun p => (e.f p.1, p.2)).Pairwise
      (fun a b => compare a.1 b.1 = .lt) := by
    rw [List.pairwise_map]
    exact (ExtTreeMap.ordered_keys_toList (t := m)).imp fun h => by rw [e.cmp]; exact h
  refine List.Perm.eq_of_pairwise (le := fun a b => compare a.1 b.1 = .lt) ?_ h1 h2 ?_
  · intro a b _ _ hab hba
    have := Std.OrientedCmp.gt_of_lt hab
    rw [hba] at this; cases this
  refine (List.perm_ext_iff_of_nodup (h1.imp (lt_ne _ _)) (h2.imp (lt_ne _ _))).mpr ?_
  · rintro ⟨k, v⟩
    rw [ExtTreeMap.mem_toList_iff_getElem?_eq_some, getElem?_mapK, List.mem_map]
    constructor
    · intro h
      exact ⟨(e.g k, v), ExtTreeMap.mem_toList_iff_getElem?_eq_some.mpr h, by simp [e.fg]⟩
    · rintro ⟨⟨k', v'⟩, hm, he⟩
      simp only [Prod.mk.injEq] at he
      obtain ⟨rfl, rfl⟩ := he
      rw [e.gf]; exact ExtTreeMap.mem_toList_iff_getElem?_eq_some.mp hm


/-! ### Sets -/

def mapS (t : ExtTreeSet α) : ExtTreeSet α := ⟨mapK e t.inner⟩

theorem contains_mapS (t : ExtTreeSet α) (k : α) : (mapS e t).contains k = t.contains (e.g k) := by
  show (mapK e t.inner).contains k = t.inner.contains (e.g k)
  rw [ExtTreeMap.contains_eq_isSome_getElem?, ExtTreeMap.contains_eq_isSome_getElem?,
    getElem?_mapK]

theorem contains_mapS_f (t : ExtTreeSet α) (k : α) : (mapS e t).contains (e.f k) = t.contains k := by
  rw [contains_mapS, e.gf]

theorem mapS_insert (t : ExtTreeSet α) (a : α) : mapS e (t.insert a) = (mapS e t).insert (e.f a) := by
  apply ExtTreeSet.ext_contains
  intro q
  rw [contains_mapS, ExtTreeSet.contains_insert, ExtTreeSet.contains_insert, contains_mapS]
  congr 1
  rw [← e.cmp, e.fg]

theorem mapS_erase (t : ExtTreeSet α) (a : α) : mapS e (t.erase a) = (mapS e t).erase (e.f a) := by
  apply ExtTreeSet.ext_contains
  intro q
  rw [contains_mapS, ExtTreeSet.contains_erase, ExtTreeSet.contains_erase, contains_mapS]
  congr 1
  rw [← e.cmp, e.fg]

theorem mapS_empty : mapS e (∅ : ExtTreeSet α) = ∅ := by
  apply ExtTreeSet.ext_contains
  intro q; rw [contains_mapS]; rfl

theorem toList_mapS (t : ExtTreeSet α) : (mapS e t).toList = t.toList.map e.f := by
  show (mapK e t.inner).keys = t.inner.keys.map e.f
  rw [← ExtTreeMap.map_fst_toList_eq_keys, ← ExtTreeMap.map_fst_toList_eq_keys, toList_mapK,
    List.map_map, List.map_map]
  rfl

theorem size_mapS (t : ExtTreeSet α) : (mapS e t).size = t.size := by
  rw [← ExtTreeSet.length_toList, ← ExtTreeSet.length_toList, toList_mapS, List.length_map]

theorem foldl_mapS {δ : Type} (t : ExtTreeSet α) (f : δ → α → δ) (init : δ) :
    (mapS e t).foldl f init = t.foldl (fun d a => f d (e.f a)) init := by
  rw [ExtTreeSet.foldl_eq_foldl_toList, ExtTreeSet.foldl_eq_foldl_toList, toList_mapS,
    List.foldl_map]

theorem foldl_mapK {β δ : Type} (m : ExtTreeMap α β) (f : δ → α → β → δ) (init : δ) :
    (mapK e m).foldl f init = m.foldl (fun d a b => f d (e.f a) b) init := by
  rw [ExtTreeMap.foldl_eq_foldl_toList, ExtTreeMap.foldl_eq_foldl_toList, toList_mapK,
    List.foldl_map]

theorem size_mapK {β : Type} (m : ExtTreeMap α β) : (mapK e m).size = m.size := by
  rw [← ExtTreeMap.length_toList, ← ExtTreeMap.length_toList, toList_mapK, List.length_map]

theorem mapK_map {β γ : Type} (m : ExtTreeMap α β) (f : α → β → γ) :
    mapK e (m.map f) = (mapK e m).map fun k v => f (e.g k) v := by
  apply ExtTreeMap.ext_getElem?
  intro q
  rw [getElem?_mapK, ExtTreeMap.getElem?_map, ExtTreeMap.getElem?_map, getElem?_mapK]

theorem mapK_filter {β : Type} (m : ExtTreeMap α β) (f : α → β → Bool) :
    mapK e (m.filter f) = (mapK e m).filter fun k v => f (e.g k) v := by
  apply ExtTreeMap.ext_getElem?
  intro q
  rw [getElem?_mapK, ExtTreeMap.getElem?_filter', ExtTreeMap.getElem?_filter', getElem?_mapK]

end

end FF
