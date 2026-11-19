/-
A tick commutes with translating the whole flyer by 16·n blocks along X (a whole number of
chunks): translate the state, and conjugate the oracle.
-/
import Formal.Shift.Map
import Formal.Lemmas.St
import Mathlib.Data.List.Nodup
import Mathlib.Order.Compare

namespace FF

open Std

/-! ### The translations -/

theorem compare_int_add (a b c : Int) : compare (a + c) (b + c) = compare a b := by
  simp only [compare, compareOfLessAndEq]
  split_ifs <;> first | rfl | omega

section
attribute [local instance] lexOrd

theorem compare_triple_shift (a b : Int × Int × Int) (c : Int) :
    compare (a.1 + c, a.2) (b.1 + c, b.2) = compare a b := by
  obtain ⟨a1, a2⟩ := a
  obtain ⟨b1, b2⟩ := b
  show compareLex (compareOn Prod.fst) (compareOn Prod.snd) _ _ =
    compareLex (compareOn Prod.fst) (compareOn Prod.snd) _ _
  simp only [compareLex, compareOn]
  rw [compare_int_add]

theorem compare_pair_shift (a b : Int × Int) (c : Int) :
    compare (a.1 + c, a.2) (b.1 + c, b.2) = compare a b := by
  obtain ⟨a1, a2⟩ := a
  obtain ⟨b1, b2⟩ := b
  show compareLex (compareOn Prod.fst) (compareOn Prod.snd) _ _ =
    compareLex (compareOn Prod.fst) (compareOn Prod.snd) _ _
  simp only [compareLex, compareOn]
  rw [compare_int_add]

end

/-- Translation by `16 n` along X. -/
def posT (n : Int) : OIso Pos where
  f p := ⟨p.x + 16 * n, p.y, p.z⟩
  g p := ⟨p.x - 16 * n, p.y, p.z⟩
  gf p := by simp
  fg p := by simp
  cmp a b := compare_triple_shift a.toTriple b.toTriple (16 * n)

/-- The matching translation of chunks. -/
def chunkT (n : Int) : OIso Chunk where
  f c := ⟨c.cx + n, c.cz⟩
  g c := ⟨c.cx - n, c.cz⟩
  gf c := by simp
  fg c := by simp
  cmp a b := compare_pair_shift a.toPair b.toPair n

theorem posT_add (n : Int) (p : Pos) (d : Dir) : (posT n).f (p.add d) = ((posT n).f p).add d := by
  simp only [posT, Pos.add]; congr 1; omega

theorem chunkOf_posT (c : Config) (n : Int) (p : Pos) :
    c.chunkOf ((posT n).f p) = (chunkT n).f (c.chunkOf p) := by
  simp only [Config.chunkOf, posT, chunkT]
  congr 1
  rw [show p.x + 16 * n + c.phaseX = (p.x + c.phaseX) + n * 16 by omega]
  exact Int.add_mul_ediv_right _ _ (by decide)


/-! ### Translated states -/

section
variable (n : Int)


def St.tr (s : St) : St where
  world := mapK (posT n) s.world
  lists := mapK (posT n) (s.lists.map fun _ L => L.map (posT n).f)

def Ctx.tr (cx : Ctx) : Ctx := ⟨cx.st.tr n, mapS (posT n) cx.powered⟩

variable {n}

theorem St.eq_of {s t : St} (h1 : ∀ q : Pos, s.world[q]? = t.world[q]?)
    (h2 : ∀ q : Pos, s.lists[q]? = t.lists[q]?) : s = t := by
  cases s; cases t
  simp only [St.mk.injEq]
  exact ⟨ExtTreeMap.ext_getElem? h1, ExtTreeMap.ext_getElem? h2⟩

theorem St.tr_world (s : St) (q : Pos) : (s.tr n).world[q]? = s.world[(posT n).g q]? :=
  getElem?_mapK _ _ _

theorem St.tr_get (s : St) (q : Pos) : (s.tr n).get q = s.get ((posT n).g q) :=
  getElem?_mapK _ _ _

theorem St.tr_get_f (s : St) (q : Pos) : (s.tr n).get ((posT n).f q) = s.get q := by
  rw [St.tr_get, (posT n).gf]

theorem St.tr_lists (s : St) (q : Pos) :
    (s.tr n).lists[q]? = (s.lists[(posT n).g q]?).map (List.map (posT n).f) := by
  simp only [St.tr]
  rw [getElem?_mapK, ExtTreeMap.getElem?_map]

theorem St.tr_lists_f (s : St) (q : Pos) :
    (s.tr n).lists[(posT n).f q]? = (s.lists[q]?).map (List.map (posT n).f) := by
  rw [St.tr_lists, (posT n).gf]

theorem St.tr_list (s : St) (q : Pos) : (s.tr n).list ((posT n).f q) = (s.list q).map (posT n).f := by
  unfold St.list
  rw [ExtTreeMap.getD_eq_getD_getElem?, ExtTreeMap.getD_eq_getD_getElem?, St.tr_lists_f]
  cases s.lists[q]? <;> rfl

theorem posT_g_f_iff {a b : Pos} : (posT n).g a = b ↔ a = (posT n).f b := by
  constructor
  · rintro rfl; rw [(posT n).fg]
  · rintro rfl; rw [(posT n).gf]

theorem St.tr_set (s : St) (p : Pos) (b : Block) : (s.set p b).tr n = (s.tr n).set ((posT n).f p) b := by
  apply St.eq_of
  · intro q
    show St.get ((s.set p b).tr n) q = St.get ((s.tr n).set ((posT n).f p) b) q
    rw [St.tr_get, St.get_set, St.get_set, St.tr_get]
    congr 1
    exact propext ⟨fun h => by rw [h, (posT n).fg], fun h => by rw [← h, (posT n).gf]⟩
  · intro q
    rw [St.tr_lists]
    simp only [St.set]
    split
    · rw [St.tr_lists]
    · rw [ExtTreeMap.getElem?_erase, ExtTreeMap.getElem?_erase, St.tr_lists]
      by_cases h : (posT n).f p = q
      · subst h; simp [(posT n).gf]
      · have h' : p ≠ (posT n).g q := by rintro rfl; exact h ((posT n).fg q)
        simp only [compare_pos_eq_iff, beq_iff_eq] at *
        simp [h', h]

theorem St.tr_remove (s : St) (p : Pos) : (s.remove p).tr n = (s.tr n).remove ((posT n).f p) := by
  apply St.eq_of
  · intro q
    show St.get ((s.remove p).tr n) q = St.get ((s.tr n).remove ((posT n).f p)) q
    rw [St.tr_get, St.get_remove, St.get_remove, St.tr_get]
    congr 1
    exact propext ⟨fun h => by rw [h, (posT n).fg], fun h => by rw [← h, (posT n).gf]⟩
  · intro q
    rw [St.tr_lists]
    simp only [St.remove]
    rw [ExtTreeMap.getElem?_erase, ExtTreeMap.getElem?_erase, St.tr_lists]
    by_cases h : (posT n).f p = q
    · subst h; simp [(posT n).gf]
    · have h' : p ≠ (posT n).g q := by rintro rfl; exact h ((posT n).fg q)
      simp only [compare_pos_eq_iff, beq_iff_eq] at *
      simp [h', h]


theorem posT_f_inj {a b : Pos} (h : (posT n).f a = (posT n).f b) : a = b := (posT n).f_inj h

theorem St.tr_lists_erase (s : St) (p : Pos) :
    ({ s with lists := s.lists.erase p } : St).tr n =
      { s.tr n with lists := (s.tr n).lists.erase ((posT n).f p) } := by
  apply St.eq_of
  · intro q; rfl
  · intro q
    show (St.tr n { s with lists := s.lists.erase p }).lists[q]? = ((s.tr n).lists.erase _)[q]?
    rw [St.tr_lists, ExtTreeMap.getElem?_erase, ExtTreeMap.getElem?_erase, St.tr_lists]
    simp only [compare_pos_eq_iff]
    by_cases h : (posT n).f p = q
    · subst h; simp [(posT n).gf]
    · have h' : p ≠ (posT n).g q := by rintro rfl; exact h ((posT n).fg q)
      simp [h', h]

theorem St.tr_lists_insert (s : St) (p : Pos) (L : List Pos) :
    ({ s with lists := s.lists.insert p L } : St).tr n =
      { s.tr n with lists := (s.tr n).lists.insert ((posT n).f p) (L.map (posT n).f) } := by
  apply St.eq_of
  · intro q; rfl
  · intro q
    show (St.tr n { s with lists := s.lists.insert p L }).lists[q]? = ((s.tr n).lists.insert _ _)[q]?
    rw [St.tr_lists, ExtTreeMap.getElem?_insert, ExtTreeMap.getElem?_insert, St.tr_lists]
    simp only [compare_pos_eq_iff]
    by_cases h : (posT n).f p = q
    · subst h; simp [(posT n).gf]
    · have h' : p ≠ (posT n).g q := by rintro rfl; exact h ((posT n).fg q)
      simp [h', h]

def Err.tr (n : Int) : Err → Err
  | .listOwnerNotPiston p => .listOwnerNotPiston ((posT n).f p)
  | .listTooLong p => .listTooLong ((posT n).f p)
  | .listDuplicate p => .listDuplicate ((posT n).f p)

/-- Translate both outcomes of a computation. -/
def trE {α β : Type} (n : Int) (f : α → β) : Except Err α → Except Err β
  | .ok a => .ok (f a)
  | .error e => .error (e.tr n)

theorem St.tr_setList (c : Config) (s : St) (p : Pos) (l : List Pos) :
    trE n (St.tr n) (s.setList c p l) = (s.tr n).setList c ((posT n).f p) (l.map (posT n).f) := by
  have hsort : (l.map (posT n).f).mergeSort (fun a b => compare a b != .gt) =
      (l.mergeSort (fun a b => compare a b != .gt)).map (posT n).f := by
    rw [List.map_mergeSort]
    intro a _ b _
    rw [(posT n).cmp]
  have hnd : ∀ L : List Pos, (L.map (posT n).f).Nodup ↔ L.Nodup :=
    fun L => List.nodup_map_iff (fun a b h => posT_f_inj h)
  unfold St.setList
  rw [St.tr_get_f]
  cases s.get p with
  | none => rfl
  | some b =>
    simp only [List.length_map, hsort]
    split
    · rfl
    · split
      · rfl
      · simp only [hnd, List.isEmpty_map]
        split
        · rfl
        · split
          · simp only [trE]; rw [St.tr_lists_erase]
          · simp only [trE]; rw [St.tr_lists_insert]


theorem Ctx.tr_removeIndexed (cx : Ctx) (p : Pos) :
    (cx.removeIndexed p).tr n = (cx.tr n).removeIndexed ((posT n).f p) := by
  simp only [Ctx.tr, Ctx.removeIndexed, St.tr_remove, mapS_erase]

theorem Ctx.tr_placeIndexed (cx : Ctx) (p : Pos) (b : Block) :
    (cx.placeIndexed p b).tr n = (cx.tr n).placeIndexed ((posT n).f p) b := by
  simp only [Ctx.tr, Ctx.placeIndexed, St.tr_set, mapS_erase]

theorem beq_posT (a b : Pos) : ((posT n).f a == (posT n).f b) = (a == b) := by
  by_cases h : a = b
  · subst h; simp
  · have : (posT n).f a ≠ (posT n).f b := fun e => h (posT_f_inj e)
    simp [h, this]

/-! ### Power -/

theorem hardPowered_tr (s : St) (t : Pos) : hardPowered (s.tr n) ((posT n).f t) = hardPowered s t := by
  unfold hardPowered
  simp only [St.tr_get_f, ← posT_add]

theorem pistonPowered_tr (s : St) (p : Pos) :
    pistonPowered (s.tr n) ((posT n).f p) = pistonPowered s p := by
  unfold pistonPowered
  simp only [St.tr_get_f, ← posT_add, hardPowered_tr, beq_posT]

theorem foldl_insert_tr (F : Pos → Bool) (L : List (Pos × Block)) (init : ExtTreeSet Pos) :
    L.foldl (fun acc e => if F ((posT n).f e.1) then acc.insert ((posT n).f e.1) else acc)
      (mapS (posT n) init) =
    mapS (posT n) (L.foldl (fun acc e => if F ((posT n).f e.1) then acc.insert e.1 else acc) init) := by
  induction L generalizing init with
  | nil => rfl
  | cons e L ih =>
    simp only [List.foldl_cons]
    split
    · rw [← mapS_insert, ih]
    · rw [ih]

theorem powerStage_tr (s : St) :
    powerStage (s.tr n) = ((powerStage s).1.tr n, mapS (posT n) (powerStage s).2) := by
  have hpw : (powerStage (s.tr n)).2 = mapS (posT n) (powerStage s).2 := by
    show (s.tr n).world.foldl (fun acc p _ => if pistonPowered (s.tr n) p then acc.insert p else acc) ∅
      = mapS (posT n) (s.world.foldl (fun acc p _ => if pistonPowered s p then acc.insert p else acc) ∅)
    have hw : (s.tr n).world = mapK (posT n) s.world := rfl
    rw [hw, foldl_mapK, ExtTreeMap.foldl_eq_foldl_toList, ExtTreeMap.foldl_eq_foldl_toList]
    simp only [pistonPowered_tr]
    have := foldl_insert_tr (n := n) (fun p => pistonPowered s ((posT n).g p)) s.world.toList ∅
    simp only [(posT n).gf, mapS_empty] at this
    exact this
  refine Prod.ext ?_ hpw
  apply St.eq_of
  · intro q
    show ((s.tr n).world.map _)[q]? = ((powerStage s).1.tr n).world[q]?
    rw [St.tr_world, ExtTreeMap.getElem?_map, St.tr_world]
    show _ = (s.world.map _)[(posT n).g q]?
    rw [ExtTreeMap.getElem?_map]
  · intro q
    show ((s.tr n).lists.filter _)[q]? = ((powerStage s).1.tr n).lists[q]?
    rw [ExtTreeMap.getElem?_filter', St.tr_lists, St.tr_lists]
    show _ = Option.map _ ((s.lists.filter _)[(posT n).g q]?)
    rw [ExtTreeMap.getElem?_filter']
    cases s.lists[(posT n).g q]? with
    | none => rfl
    | some L =>
      simp only [Option.map_some, Option.filter_some, St.tr_get]
      split <;> rfl

theorem clearAngry_tr (s : St) (pw : ExtTreeSet Pos) :
    clearAngry (s.tr n) (mapS (posT n) pw) = (clearAngry s pw).tr n := by
  apply St.eq_of
  · intro q
    show ((s.tr n).world.map _)[q]? = ((clearAngry s pw).tr n).world[q]?
    rw [ExtTreeMap.getElem?_map, St.tr_world, St.tr_world]
    show _ = (s.world.map _)[(posT n).g q]?
    rw [ExtTreeMap.getElem?_map]
    cases s.world[(posT n).g q]? with
    | none => rfl
    | some b =>
      simp only [Option.map_some]
      congr 1
      cases b <;> try rfl
      rename_i d st an k mv
      cases mv <;> simp [contains_mapS]
  · intro q; rfl


/-! ### Discovery -/

theorem immovable_tr (o : Option Pos) (p : Pos) (b : Block) :
    immovable (o.map (posT n).f) ((posT n).f p) b = immovable o p b := by
  unfold immovable
  cases o with
  | none => rfl
  | some q =>
    have : (some ((posT n).f q) == some ((posT n).f p)) = (some q == some p) := by
      by_cases h : q = p
      · subst h; simp
      · have h' : (posT n).f q ≠ (posT n).f p := fun e => h (posT_f_inj e)
        simp [h, h']
    simp only [Option.map_some, this]

theorem singleton_tr (a : Pos) : ({(posT n).f a} : ExtTreeSet Pos) = mapS (posT n) {a} := by
  rw [ExtTreeSet.singleton_eq_insert, ExtTreeSet.singleton_eq_insert, mapS_insert, mapS_empty]

theorem adhStep_tr (s : St) (o : Option Pos) (p : Pos) (b : Block) (acc : ExtTreeSet Pos) (e : Dir) :
    adhStep (s.tr n) (o.map (posT n).f) ((posT n).f p) b (mapS (posT n) acc) e =
      mapS (posT n) (adhStep s o p b acc e) := by
  unfold adhStep
  rw [← posT_add, St.tr_get_f]
  cases s.get (p.add e) with
  | none => rfl
  | some nb =>
    simp only [immovable_tr]
    split <;> simp [mapS_insert]

theorem adhesion_tr (s : St) (o : Option Pos) (acc : ExtTreeSet Pos) (p : Pos) :
    adhesion (s.tr n) (o.map (posT n).f) (mapS (posT n) acc) ((posT n).f p) =
      mapS (posT n) (adhesion s o acc p) := by
  unfold adhesion
  rw [St.tr_get_f]
  cases s.get p with
  | none => rfl
  | some b =>
    simp only
    split
    · generalize Dir.all = L
      induction L generalizing acc with
      | nil => rfl
      | cons e L ih => simp only [List.foldl_cons, adhStep_tr, ih]
    · rfl

theorem expandStep_tr (s : St) (dir : Dir) (o : Option Pos) (acc : ExtTreeSet Pos) (p : Pos) :
    expandStep (s.tr n) dir (o.map (posT n).f) (mapS (posT n) acc) ((posT n).f p) =
      mapS (posT n) (expandStep s dir o acc p) := by
  unfold expandStep
  simp only [adhesion_tr, ← posT_add, St.tr_get_f]
  split <;> simp [mapS_insert]

theorem expand_tr (s : St) (dir : Dir) (o : Option Pos) (S : ExtTreeSet Pos) :
    expand (s.tr n) dir (o.map (posT n).f) (mapS (posT n) S) = mapS (posT n) (expand s dir o S) := by
  unfold expand
  rw [foldl_mapS, ExtTreeSet.foldl_eq_foldl_toList, ExtTreeSet.foldl_eq_foldl_toList]
  generalize S.toList = L
  generalize hI : S = I
  rw [← hI] at *
  clear hI
  induction L generalizing S with
  | nil => rfl
  | cons a L ih => simp only [List.foldl_cons, expandStep_tr, ih]

theorem closure_tr (c : Config) (s : St) (dir : Dir) (o : Option Pos) (k : Nat) (S : ExtTreeSet Pos) :
    closure c (s.tr n) dir (o.map (posT n).f) k (mapS (posT n) S) =
      (closure c s dir o k S).map (mapS (posT n)) := by
  induction k generalizing S with
  | zero => rfl
  | succ k ih =>
    unfold closure
    simp only [size_mapS, expand_tr, toList_mapS, List.all_map]
    split
    · rfl
    · have : (List.all (expand s dir o S).toList fun a => (mapS (posT n) S).contains ((posT n).f a)) =
          (expand s dir o S).toList.all S.contains := by
        congr 1; funext a; rw [contains_mapS_f]
      simp only [Function.comp_def, this]
      split
      · rfl
      · exact ih _

theorem discover_tr (c : Config) (s : St) (first : Pos) (dir : Dir) (o : Option Pos) (pl : Bool) :
    discover c (s.tr n) ((posT n).f first) dir (o.map (posT n).f) pl =
      (discover c s first dir o pl).map (List.map (posT n).f) := by
  unfold discover
  rw [St.tr_get_f]
  cases s.get first with
  | none => rfl
  | some fb =>
    simp only
    split
    · rfl
    · have hsize : (s.tr n).world.size = s.world.size := size_mapK _ _
      rw [hsize, singleton_tr, closure_tr]
      cases closure c s dir o (s.world.size + 1) {first} with
      | none => rfl
      | some S =>
        simp only [Option.map_some, toList_mapS, List.any_map, List.length_map]
        have key : ∀ x : Pos, (St.tr n s).get ((posT n).f x) = s.get x := fun x => St.tr_get_f s x
        simp only [Function.comp_def, key]
        simp only [immovable_tr]
        split <;> rfl


/-! ### Piston actions -/

theorem foldlM_trE {α α' : Type} (L : List α) (F : Ctx → α → Except Err Ctx)
    (G : Ctx → α' → Except Err Ctx) (m : α → α')
    (h : ∀ cx a, a ∈ L → trE n (Ctx.tr n) (F cx a) = G (cx.tr n) (m a)) (cx : Ctx) :
    trE n (Ctx.tr n) (L.foldlM F cx) = (L.map m).foldlM G (cx.tr n) := by
  induction L generalizing cx with
  | nil => rfl
  | cons a L ih =>
    simp only [List.foldlM_cons, List.map_cons]
    have ha := h cx a (by simp)
    cases hF : F cx a with
    | ok cx' =>
      rw [hF] at ha
      simp only [trE] at ha
      rw [← ha]
      simp only [bind, Except.bind]
      exact ih (fun cx a hm => h cx a (by simp [hm])) cx'
    | error e =>
      rw [hF] at ha
      simp only [trE] at ha
      rw [← ha]
      rfl

theorem trE_foldlM_pure {α α' : Type} (L : List α) (F : Ctx → α → Except Err Ctx)
    (G : Ctx → α' → Except Err Ctx) (m : α → α')
    (h : ∀ cx a, a ∈ L → trE n (Ctx.tr n) (F cx a) = G (cx.tr n) (m a)) (cx : Ctx)
    (D D' : List Pos) (hD : D.map (posT n).f = D') :
    trE n (fun r => (r.1.tr n, r.2.map (posT n).f)) (L.foldlM F cx >>= fun cx => pure (cx, D)) =
      ((L.map m).foldlM G (cx.tr n) >>= fun cx => pure (cx, D')) := by
  rw [← foldlM_trE L F G m h cx]
  cases L.foldlM F cx with
  | ok r => simp [trE, bind, Except.bind, pure, Except.pure, hD]
  | error e => rfl

theorem St.tr_finishMovedBlock (s : St) (p : Pos) :
    (finishMovedBlock s p).tr n = finishMovedBlock (s.tr n) ((posT n).f p) := by
  unfold finishMovedBlock
  rw [St.tr_get_f]
  cases s.get p with
  | none => rfl
  | some b => cases b <;> simp [St.tr_set]

theorem St.tr_foldl_finish (s : St) (L : List Pos) :
    (L.foldl finishMovedBlock s).tr n = (L.map (posT n).f).foldl finishMovedBlock (s.tr n) := by
  induction L generalizing s with
  | nil => rfl
  | cons p L ih => simp only [List.foldl_cons, List.map_cons, ← St.tr_finishMovedBlock, ih]

theorem finishMovement_tr (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (st an : Bool)
    (next : Fin 4) :
    trE n (Ctx.tr n) (finishMovement c cx pos d st an next) =
      finishMovement c (cx.tr n) ((posT n).f pos) d st an next := by
  unfold finishMovement
  have hl : (cx.tr n).st.list ((posT n).f pos) = (cx.st.list pos).map (posT n).f :=
    St.tr_list cx.st pos
  simp only [Ctx.tr] at hl ⊢
  rw [hl, ← St.tr_foldl_finish]
  have h := St.tr_setList (n := n) c ((cx.st.list pos).foldl finishMovedBlock cx.st) pos []
  simp only [List.map_nil] at h
  rw [← h]
  cases St.setList c ((cx.st.list pos).foldl finishMovedBlock cx.st) pos [] with
  | ok s2 => simp [trE, bind, Except.bind, pure, Except.pure, St.tr_set, Ctx.tr]
  | error e => rfl

def entryTr (n : Int) (e : Pos × Block × List Pos) : Pos × Block × List Pos :=
  ((posT n).f e.1, e.2.1, e.2.2.map (posT n).f)

theorem moveBlocks_tr (c : Config) (cx : Ctx) (sources : List Pos) (dir : Dir) :
    trE n (fun r => (r.1.tr n, r.2.map (posT n).f)) (moveBlocks c cx sources dir) =
      moveBlocks c (cx.tr n) (sources.map (posT n).f) dir := by
  unfold moveBlocks
  -- the entries
  have hent : ((sources.map (posT n).f).filterMap fun p =>
      ((cx.tr n).st.get p).map fun b => (p, b, (cx.tr n).st.list p)) =
      (sources.filterMap fun p => (cx.st.get p).map fun b => (p, b, cx.st.list p)).map (entryTr n) := by
    rw [List.filterMap_map, List.map_filterMap]
    congr 1; funext p
    simp only [Function.comp_apply, Ctx.tr, St.tr_get_f, St.tr_list]
    cases cx.st.get p <;> rfl
  rw [hent]
  generalize hE : (sources.filterMap fun p => (cx.st.get p).map fun b => (p, b, cx.st.list p)) = E
  -- removal and placement
  have h1 : ∀ (E : List (Pos × Block × List Pos)) (cx : Ctx),
      (E.map (entryTr n)).foldl (fun cx e => cx.removeIndexed e.1) (cx.tr n) =
        (E.foldl (fun cx e => cx.removeIndexed e.1) cx).tr n := by
    intro E
    induction E with
    | nil => intro cx; rfl
    | cons e E ih =>
      intro cx
      simp only [List.map_cons, List.foldl_cons]
      rw [show (cx.tr n).removeIndexed (entryTr n e).1 = (cx.removeIndexed e.1).tr n from
        (Ctx.tr_removeIndexed cx e.1).symm, ih]
  have h2 : ∀ (E : List (Pos × Block × List Pos)) (cx : Ctx),
      (E.map (entryTr n)).foldl (fun cx e => cx.placeIndexed (e.1.add dir) e.2.1.startMoving)
        (cx.tr n) =
        (E.foldl (fun cx e => cx.placeIndexed (e.1.add dir) e.2.1.startMoving) cx).tr n := by
    intro E
    induction E with
    | nil => intro cx; rfl
    | cons e E ih =>
      intro cx
      simp only [List.map_cons, List.foldl_cons]
      rw [show (cx.tr n).placeIndexed ((entryTr n e).1.add dir) (entryTr n e).2.1.startMoving =
        (cx.placeIndexed (e.1.add dir) e.2.1.startMoving).tr n by
          rw [Ctx.tr_placeIndexed, posT_add]; rfl, ih]
  dsimp only
  rw [h1, h2]
  refine trE_foldlM_pure E _ _ (entryTr n) ?_ _ _ _ ?_
  rotate_left
  · simp only [List.map_map]
    congr 1; funext e
    simp [entryTr, posT_add]
  · rintro cx ⟨p, b, l⟩ _
    simp only [entryTr, List.isEmpty_map]
    split
    · have htl : (l.map (posT n).f).map (fun m => if (sources.map (posT n).f).contains m then
          m.add dir else m) = (l.map fun m => if sources.contains m then m.add dir else m).map
          (posT n).f := by
        simp only [List.map_map]
        congr 1; funext m
        simp only [Function.comp_apply]
        have : (sources.map (posT n).f).contains ((posT n).f m) = sources.contains m := by
          rw [Bool.eq_iff_iff, List.contains_iff_mem, List.contains_iff_mem, List.mem_map]
          exact ⟨fun ⟨a, ha, he⟩ => by rw [← posT_f_inj he]; exact ha, fun h => ⟨m, h, rfl⟩⟩
        rw [this]; split <;> simp [posT_add]
      rw [htl, show (cx.tr n).st = cx.st.tr n from rfl, ← posT_add, ← St.tr_setList]
      cases St.setList c cx.st (p.add dir) _ with
      | ok s' => rfl
      | error e => rfl
    · rfl


theorem Ctx.tr_st (cx : Ctx) : (cx.tr n).st = cx.st.tr n := rfl

theorem Ctx.tr_powered (cx : Ctx) (p : Pos) :
    (cx.tr n).powered.contains ((posT n).f p) = cx.powered.contains p := contains_mapS_f _ _ _

theorem startExtension_tr (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (st : Bool) :
    trE n (Option.map (Ctx.tr n)) (startExtension c cx pos d st) =
      startExtension c (cx.tr n) ((posT n).f pos) d st := by
  unfold startExtension
  dsimp only
  rw [← posT_add, Ctx.tr_st, show some ((posT n).f pos) = (some pos).map (posT n).f from rfl,
    discover_tr]
  cases discover c cx.st (pos.add d) d (some pos) false with
  | none => rfl
  | some sources =>
    simp only [Option.map_some]
    rw [← moveBlocks_tr]
    cases moveBlocks c cx sources d with
    | error e => rfl
    | ok r =>
      obtain ⟨cx1, dests⟩ := r
      simp only [trE, bind, Except.bind]
      rw [← Ctx.tr_placeIndexed, Ctx.tr_st, ← St.tr_set, ← St.tr_setList]
      cases St.setList c ((cx1.placeIndexed (pos.add d) (.plain .arm false)).st.set pos
        (.piston d st false 1 false)) pos dests with
      | error e => rfl
      | ok s' => rfl

theorem retractPull_tr (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (st : Bool) :
    trE n (fun r => (r.1.tr n, r.2.map (posT n).f)) (retractPull c cx pos d st) =
      retractPull c (cx.tr n) ((posT n).f pos) d st := by
  unfold retractPull
  cases st with
  | false => rfl
  | true =>
    simp only [ite_true]
    rw [← posT_add, ← posT_add, Ctx.tr_st, show some ((posT n).f pos) = (some pos).map (posT n).f
      from rfl, discover_tr]
    cases discover c cx.st ((pos.add d).add d) d.opp (some pos) true with
    | none => rfl
    | some sources => simp only [Option.map_some]; exact moveBlocks_tr c cx sources d.opp

theorem startRetraction_tr (c : Config) (cx : Ctx) (pos : Pos) (d : Dir) (st an : Bool) :
    trE n (Ctx.tr n) (startRetraction c cx pos d st an) =
      startRetraction c (cx.tr n) ((posT n).f pos) d st an := by
  unfold startRetraction
  dsimp only
  rw [← posT_add, ← Ctx.tr_removeIndexed, ← retractPull_tr]
  cases retractPull c (cx.removeIndexed (pos.add d)) pos d st with
  | error e => rfl
  | ok r =>
    obtain ⟨cx2, dests⟩ := r
    simp only [trE, bind, Except.bind]
    rw [Ctx.tr_st, ← St.tr_set, ← St.tr_setList]
    cases St.setList c (cx2.st.set pos (.piston d st an 3 false)) pos dests with
    | error e => rfl
    | ok s' => rfl

theorem pistonTurn_tr (c : Config) (cx : Ctx) (pos : Pos) :
    trE n (Ctx.tr n) (pistonTurn c cx pos) = pistonTurn c (cx.tr n) ((posT n).f pos) := by
  unfold pistonTurn
  rw [Ctx.tr_st, St.tr_get_f]
  cases cx.st.get pos with
  | none => rfl
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true => rfl
      | false =>
        simp only [Ctx.tr_powered]
        split
        · split
          · rw [← startExtension_tr]
            cases startExtension c cx pos d st with
            | error e => rfl
            | ok r =>
              cases r with
              | none =>
                simp only [trE, bind, Except.bind, Option.map_none, pure, Except.pure]
                simp only [Ctx.tr, St.tr_set]
              | some cx' => rfl
          · rfl
        · exact finishMovement_tr c cx pos d st an 2
        · split
          · rfl
          · exact startRetraction_tr c cx pos d st an
        · exact finishMovement_tr c cx pos d st an 0
    | _ => rfl


/-! ### Chunks, candidates, ticks -/

theorem beq_chunkT (a b : Chunk) : ((chunkT n).f a == (chunkT n).f b) = (a == b) := by
  by_cases h : a = b
  · subst h; simp
  · have : (chunkT n).f a ≠ (chunkT n).f b := fun e => h ((chunkT n).f_inj e)
    simp [h, this]

theorem foldl_chunk_tr (c : Config) (L : List (Pos × Block)) (init : ExtTreeSet Chunk) :
    L.foldl (fun a b => a.insert ((chunkT n).f (c.chunkOf b.1))) (mapS (chunkT n) init) =
      mapS (chunkT n) (L.foldl (fun a b => a.insert (c.chunkOf b.1)) init) := by
  induction L generalizing init with
  | nil => rfl
  | cons a L ih => simp only [List.foldl_cons, ← mapS_insert, ih]

theorem occupiedChunks_tr (c : Config) (s : St) :
    occupiedChunks c (s.tr n) = (occupiedChunks c s).map (chunkT n).f := by
  unfold occupiedChunks
  rw [← toList_mapS]
  congr 1
  show (mapK (posT n) s.world).foldl _ ∅ = _
  rw [foldl_mapK, ExtTreeMap.foldl_eq_foldl_toList, ExtTreeMap.foldl_eq_foldl_toList]
  simp only [chunkOf_posT]
  have := foldl_chunk_tr (n := n) c s.world.toList ∅
  rw [mapS_empty] at this
  exact this

theorem candidates_tr (c : Config) (s : St) (ch : Chunk) :
    candidates c (s.tr n) ((chunkT n).f ch) = (candidates c s ch).map (posT n).f := by
  unfold candidates
  show (mapK (posT n) s.world).toList.filterMap _ = _
  rw [toList_mapK, List.filterMap_map, List.map_filterMap]
  congr 1; funext e
  simp only [Function.comp_apply, chunkOf_posT, beq_chunkT]
  split <;> rfl

/-- The oracle that makes the same choices on the untranslated flyer. -/
def TickOracle.conj (n : Int) (o : TickOracle) : TickOracle where
  chunks st l := ⟨(o.chunks (st.tr n) (l.map (chunkT n).f)).val.map (chunkT n).g, by
    have := ((o.chunks (st.tr n) (l.map (chunkT n).f)).property).map (chunkT n).g
    rw [List.map_map] at this
    have hid : (chunkT n).g ∘ (chunkT n).f = id := funext (chunkT n).gf
    rwa [hid, List.map_id] at this⟩
  pistons st ch l := ⟨(o.pistons (st.tr n) ((chunkT n).f ch) (l.map (posT n).f)).val.map
      (posT n).g, by
    have := ((o.pistons (st.tr n) ((chunkT n).f ch) (l.map (posT n).f)).property).map (posT n).g
    rw [List.map_map] at this
    have hid : (posT n).g ∘ (posT n).f = id := funext (posT n).gf
    rwa [hid, List.map_id] at this⟩

theorem map_g_f_chunk (l : List Chunk) : (l.map (chunkT n).g).map (chunkT n).f = l := by
  rw [List.map_map]
  have : (chunkT n).f ∘ (chunkT n).g = id := funext (chunkT n).fg
  rw [this, List.map_id]

theorem map_g_f_pos (l : List Pos) : (l.map (posT n).g).map (posT n).f = l := by
  rw [List.map_map]
  have : (posT n).f ∘ (posT n).g = id := funext (posT n).fg
  rw [this, List.map_id]

theorem tick_tr (c : Config) (o : TickOracle) (s : St) :
    tick c o (s.tr n) = trE n (St.tr n) (tick c (o.conj n) s) := by
  unfold tick
  rw [powerStage_tr]
  simp only [clearAngry_tr, occupiedChunks_tr]
  set s0 := clearAngry (powerStage s).1 (powerStage s).2
  set pw := (powerStage s).2
  have hc : clearAngry ((powerStage s).1.tr n) (mapS (posT n) pw) = s0.tr n := clearAngry_tr _ _
  rw [hc, occupiedChunks_tr]
  have hord : (o.chunks (s0.tr n) ((occupiedChunks c s0).map (chunkT n).f)).val =
      ((o.conj n).chunks s0 (occupiedChunks c s0)).val.map (chunkT n).f := by
    simp only [TickOracle.conj, map_g_f_chunk]
  rw [hord]
  have key := foldlM_trE (n := n) ((o.conj n).chunks s0 (occupiedChunks c s0)).val
    (fun cx ch => ((o.conj n).pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx)
    (fun cx ch => (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx)
    (chunkT n).f ?_ ⟨s0, pw⟩
  · simp only [Ctx.tr] at key
    rw [← key]
    generalize List.foldlM (fun cx ch =>
      ((o.conj n).pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx)
      (⟨s0, pw⟩ : Ctx) ((o.conj n).chunks s0 (occupiedChunks c s0)).val = r
    cases r with
    | ok cx => rfl
    | error e => rfl
  · intro cx ch _
    rw [Ctx.tr_st, candidates_tr]
    have hp : (o.pistons (cx.st.tr n) ((chunkT n).f ch) ((candidates c cx.st ch).map (posT n).f)).val
        = ((o.conj n).pistons cx.st ch (candidates c cx.st ch)).val.map (posT n).f := by
      simp only [TickOracle.conj, map_g_f_pos]
    rw [hp]
    exact foldlM_trE _ (pistonTurn c) (pistonTurn c) (posT n).f
      (fun cx p _ => pistonTurn_tr c cx p) cx

/-- The run oracle conjugated tick by tick. -/
def Oracle.conj (n : Int) (o : Oracle) : Oracle := fun t => (o t).conj n

theorem run_tr (c : Config) (o : Oracle) (s : St) (t : Nat) :
    run c o (s.tr n) t = trE n (St.tr n) (run c (o.conj n) s t) := by
  induction t with
  | zero => rfl
  | succ t ih =>
    show (do tick c (o t) (← run c o (s.tr n) t)) = trE n (St.tr n) (do tick c ((o t).conj n) (← run c (o.conj n) s t))
    rw [ih]
    cases run c (o.conj n) s t with
    | error e => rfl
    | ok s' => simp only [trE, bind, Except.bind]; exact tick_tr c (o t) s'

end

end FF
