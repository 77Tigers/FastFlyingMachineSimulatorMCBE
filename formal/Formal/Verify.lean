/-
Checking a concrete flyer under every oracle.

`allTicks c s` lists every possible outcome of one tick (every chunk order, and at every
chunk turn every order of its candidate pistons); `tick_mem_allTicks` shows the oracle's tick
is always one of them. Together with translation (`Formal/Shift/Sim.lean`) this reduces
"flies under every oracle" to a finite check.
-/
import Formal.Shift.Sim
import Formal.Speed
import Mathlib.Data.List.Permutation
import Mathlib.Tactic.Ring

namespace FF

open Std

/-- All outcomes of the chunk turns in `order`, from `cx`. -/
def chunkFold (c : Config) : List Chunk → Ctx → List (Except Err Ctx)
  | [], cx => [.ok cx]
  | ch :: rest, cx =>
    (candidates c cx.st ch).permutations.flatMap fun ps =>
      match ps.foldlM (pistonTurn c) cx with
      | .ok cx' => chunkFold c rest cx'
      | .error e => [.error e]

/-- All outcomes of one tick. -/
def allTicks (c : Config) (s : St) : List (Except Err St) :=
  let s0 := clearAngry (powerStage s).1 (powerStage s).2
  (occupiedChunks c s0).permutations.flatMap fun order =>
    (chunkFold c order ⟨s0, (powerStage s).2⟩).map fun r => r.map Ctx.st

theorem chunkFold_mem (c : Config) (o : TickOracle) (order : List Chunk) (cx : Ctx) :
    order.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx ∈
      chunkFold c order cx := by
  induction order generalizing cx with
  | nil => simp [chunkFold]; rfl
  | cons ch rest ih =>
    simp only [List.foldlM_cons, chunkFold, List.mem_flatMap]
    refine ⟨(o.pistons cx.st ch (candidates c cx.st ch)).val,
      List.mem_permutations.mpr (o.pistons cx.st ch (candidates c cx.st ch)).property, ?_⟩
    cases h : (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx with
    | ok cx' => simp only [bind, Except.bind]; exact ih cx'
    | error e => simp [bind, Except.bind]

theorem tick_mem_allTicks (c : Config) (o : TickOracle) (s : St) : tick c o s ∈ allTicks c s := by
  unfold tick allTicks
  simp only [List.mem_flatMap, List.mem_map]
  set s0 := clearAngry (powerStage s).1 (powerStage s).2
  refine ⟨_, List.mem_permutations.mpr (o.chunks s0 (occupiedChunks c s0)).property, ?_⟩
  refine ⟨_, chunkFold_mem c o _ _, ?_⟩
  generalize (List.foldlM (fun cx ch =>
      (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx)
      (⟨s0, (powerStage s).2⟩ : Ctx) (o.chunks s0 (occupiedChunks c s0)).val) = r
  cases r <;> rfl

/-- All outcomes of `k` ticks. -/
def allRuns (c : Config) (s : St) : Nat → List (Except Err St)
  | 0 => [.ok s]
  | k + 1 => (allRuns c s k).flatMap fun r =>
    match r with
    | .ok s' => allTicks c s'
    | .error e => [.error e]

theorem run_mem_allRuns (c : Config) (o : Oracle) (s : St) (k : Nat) :
    run c o s k ∈ allRuns c s k := by
  induction k with
  | zero => simp [run, allRuns]
  | succ k ih =>
    simp only [allRuns, List.mem_flatMap]
    refine ⟨run c o s k, ih, ?_⟩
    show (do tick c (o k) (← run c o s k)) ∈ _
    cases run c o s k with
    | ok s' => exact tick_mem_allTicks c (o k) s'
    | error e => simp [bind, Except.bind]

/-! ### Translations compose; the minimum X moves with them -/

theorem posT_g_add (a b : Int) (q : Pos) : (posT a).g ((posT b).g q) = (posT (a + b)).g q := by
  simp only [posT]; congr 1; ring

theorem posT_f_add (a b : Int) (q : Pos) : (posT b).f ((posT a).f q) = (posT (a + b)).f q := by
  simp only [posT]; congr 1; ring

theorem St.tr_tr (s : St) (a b : Int) : (s.tr a).tr b = s.tr (a + b) := by
  apply St.eq_of
  · intro q
    rw [St.tr_world, St.tr_world, St.tr_world, posT_g_add]
  · intro q
    rw [St.tr_lists, St.tr_lists, St.tr_lists, posT_g_add, Option.map_map]
    congr 1
    funext L
    simp only [Function.comp_apply, List.map_map]
    congr 1; funext x; simp only [Function.comp_apply, posT_f_add]

theorem St.tr_zero (s : St) : s.tr 0 = s := by
  apply St.eq_of
  · intro q; rw [St.tr_world]; simp [posT]
  · intro q
    rw [St.tr_lists]
    have : (posT 0).g q = q := by simp [posT]
    rw [this]
    cases s.lists[q]? with
    | none => rfl
    | some L =>
      simp only [Option.map_some, Option.some.injEq]
      conv => rhs; rw [← List.map_id L]
      congr 1; funext x; simp [posT]

theorem foldl_min_add (L : List Int) (a c : Int) :
    (L.map (· + c)).foldl min (a + c) = L.foldl min a + c := by
  induction L generalizing a with
  | nil => rfl
  | cons b L ih =>
    simp only [List.map_cons, List.foldl_cons]
    rw [show min (a + c) (b + c) = min a b + c from min_add_add_right a b c]
    exact ih (min a b)

theorem min?_map_add (L : List Int) (c : Int) : (L.map (· + c)).min? = L.min?.map (· + c) := by
  cases L with
  | nil => rfl
  | cons a L =>
    rw [List.map_cons, List.min?_cons', List.min?_cons', Option.map_some, foldl_min_add]

theorem St.minX?_tr (s : St) (n : Int) : (s.tr n).minX? = s.minX?.map (· + 16 * n) := by
  unfold St.minX?
  have hk : (s.tr n).world.keys = s.world.keys.map (posT n).f := by
    show (mapK (posT n) s.world).keys = _
    rw [← ExtTreeMap.map_fst_toList_eq_keys, ← ExtTreeMap.map_fst_toList_eq_keys, toList_mapK,
      List.map_map, List.map_map]
    rfl
  rw [hk, List.map_map, ← min?_map_add, List.map_map]
  rfl

/-! ### Runs split in two -/

theorem run_add (c : Config) (o : Oracle) (s : St) (t k : Nat) :
    run c o s (t + k) = (run c o s t >>= fun s' => run c (fun i => o (t + i)) s' k) := by
  induction k with
  | zero => cases run c o s t <;> rfl
  | succ k ih =>
    show (do tick c (o (t + k)) (← run c o s (t + k))) = _
    rw [ih]
    cases run c o s t with
    | error e => rfl
    | ok s' => rfl

/-! ### The finite check -/

def St.key (s : St) : List (Pos × Block) × List (Pos × List Pos) := (s.world.toList, s.lists.toList)

theorem St.eq_of_key {s t : St} (h : s.key = t.key) : s = t := by
  simp only [St.key, Prod.mk.injEq] at h
  cases s; cases t
  simp only [St.mk.injEq]
  exact ⟨ExtTreeMap.ext_toList (h.1 ▸ List.Perm.refl _), ExtTreeMap.ext_toList (h.2 ▸ List.Perm.refl _)⟩

/-- Translate by a whole number of chunks so that the minimum X lies in `0..15`. -/
def St.norm (s : St) : St × Int :=
  match s.minX? with
  | some m => (s.tr (-(m / 16)), m / 16)
  | none => (s, 0)

theorem St.norm_spec (s : St) : (s.norm.1).tr s.norm.2 = s := by
  unfold St.norm
  cases s.minX? with
  | none => exact St.tr_zero s
  | some m => simp only [St.tr_tr, neg_add_cancel, St.tr_zero]

def minLe (a b : Option Int) : Bool :=
  match a, b with
  | some x, some y => decide (x + 1 ≤ y)
  | _, _ => false

/-- Every state of `R` steps, under every oracle, to a translate of a state of `R`. -/
def closedB (c : Config) (R : List St) : Bool :=
  R.all fun r => (allTicks c r).all fun x =>
    match x with
    | .ok s' => R.any fun r' => r'.key == s'.norm.1.key
    | .error _ => false

/-- From every state of `R`, every run of `P` ticks raises the minimum X by at least 1. -/
def progressB (c : Config) (R : List St) (P : Nat) : Bool :=
  R.all fun r => (allRuns c r P).all fun x =>
    match x with
    | .ok s' => minLe r.minX? s'.minX?
    | .error _ => false

theorem reach_inv (c : Config) (R : List St) (hC : closedB c R = true) (s0 : St)
    (h0 : ∃ r ∈ R, ∃ k, s0 = r.tr k) (o : Oracle) :
    ∀ t, ∃ r ∈ R, ∃ k, run c o s0 t = .ok (r.tr k) := by
  intro t
  induction t with
  | zero => obtain ⟨r, hr, k, rfl⟩ := h0; exact ⟨r, hr, k, rfl⟩
  | succ t ih =>
    obtain ⟨r, hr, k, hrun⟩ := ih
    have hstep : run c o s0 (t + 1) = tick c (o t) (r.tr k) := by
      show (do tick c (o t) (← run c o s0 t)) = _
      rw [hrun]; rfl
    rw [hstep, tick_tr]
    have hmem := tick_mem_allTicks c ((o t).conj k) r
    have hc := List.all_eq_true.mp hC r hr
    have hx := List.all_eq_true.mp hc _ hmem
    cases hx' : tick c ((o t).conj k) r with
    | error e => rw [hx'] at hx; simp at hx
    | ok s' =>
      rw [hx'] at hx
      simp only [List.any_eq_true, beq_iff_eq] at hx
      obtain ⟨r', hr', hkey⟩ := hx
      have he : r' = s'.norm.1 := St.eq_of_key hkey
      refine ⟨r', hr', s'.norm.2 + k, ?_⟩
      simp only [trE]
      rw [← St.tr_tr, he, St.norm_spec]

theorem progress_step (c : Config) (R : List St) (P : Nat) (hP : progressB c R P = true)
    (r : St) (hr : r ∈ R) (k : Int) (o : Oracle) :
    ∃ s' m m', run c o (r.tr k) P = .ok s' ∧ (r.tr k).minX? = some m ∧ s'.minX? = some m' ∧
      m + 1 ≤ m' := by
  rw [run_tr]
  have hmem := run_mem_allRuns c (o.conj k) r P
  have hx := List.all_eq_true.mp (List.all_eq_true.mp hP r hr) _ hmem
  cases hx' : run c (o.conj k) r P with
  | error e => rw [hx'] at hx; simp at hx
  | ok s' =>
    rw [hx'] at hx
    simp only at hx
    unfold minLe at hx
    split at hx
    · rename_i x y hxr hys
      refine ⟨s'.tr k, x + 16 * k, y + 16 * k, rfl, ?_, ?_, ?_⟩
      · rw [St.minX?_tr, hxr]; rfl
      · rw [St.minX?_tr, hys]; rfl
      · simp at hx; omega
    · simp at hx

/-- If the check passes, the flyer never errs and, under every oracle, every `P` ticks raise
its minimum X by at least 1. -/
theorem flies_of_check (c : Config) (R : List St) (P : Nat) (hC : closedB c R = true)
    (hP : progressB c R P = true) (s0 : St) (h0 : ∃ r ∈ R, ∃ k, s0 = r.tr k) (o : Oracle) :
    (∀ t, ∃ s', run c o s0 t = .ok s') ∧
    ∀ t q (s s' : St) (m m' : Int), run c o s0 t = .ok s → run c o s0 (t + q * P) = .ok s' →
      s.minX? = some m → s'.minX? = some m' → m + q ≤ m' := by
  have hinv := reach_inv c R hC s0 h0 o
  refine ⟨fun t => let ⟨r, _, k, h⟩ := hinv t; ⟨_, h⟩, ?_⟩
  intro t q
  induction q generalizing t with
  | zero =>
    intro s s' m m' h1 h2 hm hm'
    simp only [Nat.zero_mul, Nat.add_zero] at h2
    rw [h1] at h2; cases h2; rw [hm] at hm'; cases hm'; omega
  | succ q ih =>
    intro s s' m m' h1 h2 hm hm'
    obtain ⟨r, hr, k, hrun⟩ := hinv t
    rw [h1] at hrun; cases hrun
    obtain ⟨s1, a, b, h3, ha, hb, hab⟩ := progress_step c R P hP r hr k (fun i => o (t + i))
    have hrun2 : run c o s0 (t + P) = .ok s1 := by
      rw [run_add, h1]; exact h3
    have := ih (t + P) s1 s' b m' hrun2 (by rw [← h2]; congr 1; ring) hb hm'
    rw [hm] at ha; cases ha
    omega


def startB (R : List St) (s0 : St) : Bool := R.any fun r => r.key == s0.norm.1.key

theorem start_of_startB {R : List St} {s0 : St} (h : startB R s0 = true) :
    ∃ r ∈ R, ∃ k, s0 = r.tr k := by
  simp only [startB, List.any_eq_true, beq_iff_eq] at h
  obtain ⟨r, hr, hk⟩ := h
  refine ⟨r, hr, s0.norm.2, ?_⟩
  rw [St.eq_of_key hk, St.norm_spec]

/-- Breadth-first exploration of the normalized states reachable under all oracles. -/
def explore (c : Config) : Nat → List St → List St → List St
  | 0, _, seen => seen
  | fuel + 1, frontier, seen =>
    let next := frontier.flatMap fun r => (allTicks c r).filterMap fun x =>
      match x with
      | .ok s' => some s'.norm.1
      | .error _ => none
    let fresh := next.foldl (fun acc s => if (seen ++ acc).any (·.key == s.key) then acc else acc ++ [s]) []
    if fresh.isEmpty then seen else explore c fuel fresh (seen ++ fresh)

end FF
