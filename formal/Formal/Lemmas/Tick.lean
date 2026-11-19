/-
One tick on a well-formed state, for every oracle: it succeeds, keeps `Wf`, keeps the
number of non-arm blocks, raises the X sum by at most the number of blocks in piston
lists afterwards, every piston in state 1 at the start is in state 2 at the end, and every
piston in state 3 at the end was in state 2 at the start.
-/
import Formal.Lemmas.TickPrelude
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace FF

open Std

/-- The number of cells in piston lists. -/
def St.listTotal (s : St) : Nat := ∑ p ∈ s.lists.keys.toFinset, (s.list p).length

structure TickInv (c : Config) (s0 : St) (cx : Ctx) (V : List Pos) : Prop where
  wf : Wf cx.st
  lok : ListsOK c cx.st
  nodup : V.Nodup
  frozen : ∀ q, q ∉ V → ∀ d st an k, (Frozen cx.st q d st an k ↔ Frozen s0 q d st an k)
  one_two : ∀ q ∈ V, HasState s0 q 1 → HasState cx.st q 2
  three_two : ∀ q ∈ V, HasState cx.st q 3 → HasState s0 q 2
  count : cx.st.N = s0.N
  phi : cx.st.phi ≤ s0.phi + ((V.map fun p => ((cx.st.list p).length : Int)).sum)
  phiF : cx.st.phi ≤ s0.phi + ((V.map fun p => cx.st.fwdLen p).sum)
  hiD : ∀ q ∈ V, ∀ d st an (k : Fin 4), cx.st.get q = some (.piston d st an k false) →
    (k.val = 2 ∨ k.val = 3) →
    ∃ (st' an' : Bool) (k' : Fin 4), s0.get q = some (.piston d st' an' k' false)

section
variable {c : Config} {s0 : St}

theorem hasState_frozen {s : St} {q : Pos} {k : Fin 4} (hk : k.val ≠ 0) :
    HasState s q k ↔ ∃ d st an, Frozen s q d st an k :=
  ⟨fun ⟨d, st, an, h⟩ => ⟨d, st, an, hk, h⟩, fun ⟨d, st, an, _, h⟩ => ⟨d, st, an, h⟩⟩

theorem fwdLen_ne {cx cx' : Ctx} {pos p : Pos} (hW : Wf cx.st) (hE : TurnEffect c cx cx' pos)
    (hp : p ≠ pos) : cx'.st.fwdLen p = cx.st.fwdLen p := by
  unfold St.fwdLen
  have hl : cx'.st.list p = cx.st.list p := by
    simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hE.lists_ne p hp]
  rw [hl]
  cases hL : cx.st.lists[p]? with
  | none =>
    have : cx.st.list p = [] := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hL]
    rw [this]; simp
  | some L =>
    obtain ⟨d, st, an, k, hk, h13⟩ := hW.list_owner p L hL
    have hf : Frozen cx.st p d st an k := ⟨by omega, hk⟩
    have hf' := ((hE.frozen_ne p hp d st an k).mpr hf).2
    rw [hk, hf']

theorem tickInv_step {cx : Ctx} {V : List Pos} {pos : Pos} (hI : TickInv c s0 cx V)
    (hpos : pos ∉ V) : ∃ cx', pistonTurn c cx pos = .ok cx' ∧ TickInv c s0 cx' (V ++ [pos]) := by
  obtain ⟨cx', h, hE⟩ := turn_effect (pos := pos) hI.wf hI.lok
  refine ⟨cx', h, hE.wf, hE.lok, ?_, ?_, ?_, ?_, hE.count.trans hI.count, ?_, ?_, ?_⟩
  · exact List.nodup_append.mpr ⟨hI.nodup, List.nodup_singleton _,
      fun a ha b hb e => hpos (by simp at hb; rw [← hb, ← e]; exact ha)⟩
  · intro q hq d st an k
    simp only [List.mem_append, List.mem_singleton, not_or] at hq
    exact (hE.frozen_ne q hq.2 d st an k).trans (hI.frozen q hq.1 d st an k)
  · intro q hq h1
    rcases List.mem_append.mp hq with hqV | hq
    · have hne : q ≠ pos := by rintro rfl; exact hpos hqV
      replace hq := hqV
      obtain ⟨d, st, an, hf⟩ := (hasState_frozen (by decide)).mp (hI.one_two q hq h1)
      exact (hasState_frozen (by decide)).mpr ⟨d, st, an, (hE.frozen_ne q hne d st an 2).mpr hf⟩
    · simp at hq; subst hq
      obtain ⟨d, st, an, hf⟩ := (hasState_frozen (by decide)).mp h1
      have := ((hI.frozen _ hpos d st an 1).mpr hf).2
      exact ⟨d, st, an, hE.one_two d st an this⟩
  · intro q hq h3
    rcases List.mem_append.mp hq with hqV | hq
    · have hne : q ≠ pos := by rintro rfl; exact hpos hqV
      replace hq := hqV
      obtain ⟨d, st, an, hf⟩ := (hasState_frozen (by decide)).mp h3
      exact hI.three_two q hq ((hasState_frozen (by decide)).mpr
        ⟨d, st, an, (hE.frozen_ne q hne d st an 3).mp hf⟩)
    · simp at hq; subst hq
      obtain ⟨d, st, an, h3'⟩ := h3
      have h2 := hE.three_two d st an h3'
      exact (hasState_frozen (by decide)).mpr
        ⟨d, st, an, (hI.frozen _ hpos d st an 2).mp ⟨by decide, h2⟩⟩
  · have hsum : (V.map fun p => ((cx'.st.list p).length : Int)) =
        (V.map fun p => ((cx.st.list p).length : Int)) := by
      apply List.map_congr_left
      intro p hp
      have hne : p ≠ pos := by rintro rfl; exact hpos hp
      simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hE.lists_ne p hne]
    simp only [List.map_append, List.map_cons, List.map_nil, List.sum_append, List.sum_cons,
      List.sum_nil, hsum]
    have := hE.phi
    have := hI.phi
    omega
  · have hsum : (V.map fun p => cx'.st.fwdLen p) = (V.map fun p => cx.st.fwdLen p) := by
      apply List.map_congr_left
      intro p hp
      have hne : p ≠ pos := by rintro rfl; exact hpos hp
      exact fwdLen_ne hI.wf hE hne
    simp only [List.map_append, List.map_cons, List.map_nil, List.sum_append, List.sum_cons,
      List.sum_nil, hsum]
    have := hE.phiF
    have := hI.phiF
    omega
  · intro q hq d st an k hg hk
    rcases List.mem_append.mp hq with hqV | hq
    · have hne : q ≠ pos := by rintro rfl; exact hpos hqV
      have hf := (hE.frozen_ne q hne d st an k).mp ⟨by omega, hg⟩
      exact hI.hiD q hqV d st an k hf.2 hk
    · simp at hq; subst hq
      obtain ⟨st', an', k', h', hk'⟩ := hE.dirK d st an k hg hk
      exact ⟨st', an', k', ((hI.frozen _ hpos d st' an' k').mp ⟨hk', h'⟩).2⟩

theorem tickInv_fold (ps : List Pos) : ∀ (cx : Ctx) (V : List Pos), TickInv c s0 cx V →
    ps.Nodup → (∀ p ∈ ps, p ∉ V) →
    ∃ cx', ps.foldlM (pistonTurn c) cx = .ok cx' ∧ TickInv c s0 cx' (V ++ ps) := by
  induction ps with
  | nil => intro cx V hI _ _; exact ⟨cx, rfl, by simpa using hI⟩
  | cons p ps ih =>
    intro cx V hI hnd hdis
    obtain ⟨cx1, h1, hI1⟩ := tickInv_step hI (hdis p (by simp))
    have hnd' := List.nodup_cons.mp hnd
    obtain ⟨cx', h', hI'⟩ := ih cx1 (V ++ [p]) hI1 hnd'.2 (by
      intro q hq hqV
      rcases List.mem_append.mp hqV with h | h
      · exact hdis q (by simp [hq]) h
      · simp at h; subst h; exact hnd'.1 hq)
    refine ⟨cx', ?_, by simpa using hI'⟩
    simp only [List.foldlM_cons]
    rw [h1]
    exact h'

/-- The chunk-level invariant: also, the visited cells lie in finished chunks, and every
frozen piston of a finished chunk has been visited. -/
structure ChunkInv (c : Config) (s0 : St) (cx : Ctx) (V : List Pos) (D : List Chunk) : Prop where
  tick : TickInv c s0 cx V
  vchunks : ∀ p ∈ V, c.chunkOf p ∈ D
  done : ∀ q, c.chunkOf q ∈ D → (∃ d st an k, Frozen s0 q d st an k) → q ∈ V

theorem chunkInv_step (o : TickOracle) {cx : Ctx} {V : List Pos} {D : List Chunk} {ch : Chunk}
    (hI : ChunkInv c s0 cx V D) (hch : ch ∉ D) :
    ∃ cx', (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx = .ok cx' ∧
      ∃ V', ChunkInv c s0 cx' V' (D ++ [ch]) := by
  set ps := (o.pistons cx.st ch (candidates c cx.st ch)).val with hps
  have hperm := (o.pistons cx.st ch (candidates c cx.st ch)).property
  have hnd : ps.Nodup := hperm.nodup_iff.mpr candidates_nodup
  have hmem : ∀ p, p ∈ ps ↔ p ∈ candidates c cx.st ch := fun p => hperm.mem_iff
  have hdis : ∀ p ∈ ps, p ∉ V := by
    intro p hp hpV
    have := ((mem_candidates.mp ((hmem p).mp hp)).2)
    exact hch (this ▸ hI.vchunks p hpV)
  obtain ⟨cx', h, hT⟩ := tickInv_fold ps cx V hI.tick hnd hdis
  refine ⟨cx', h, V ++ ps, hT, ?_, ?_⟩
  · intro p hp
    rcases List.mem_append.mp hp with hp | hp
    · exact List.mem_append.mpr (Or.inl (hI.vchunks p hp))
    · have := ((mem_candidates.mp ((hmem p).mp hp)).2)
      simp [this]
  · intro q hq hf
    rcases List.mem_append.mp hq with hq | hq
    · exact List.mem_append.mpr (Or.inl (hI.done q hq hf))
    · simp at hq
      by_cases hqV : q ∈ V
      · exact List.mem_append.mpr (Or.inl hqV)
      · obtain ⟨d, st, an, k, hfz⟩ := hf
        have hfz' := (hI.tick.frozen q hqV d st an k).mpr hfz
        have : q ∈ candidates c cx.st ch :=
          mem_candidates.mpr ⟨⟨_, hfz'.2, rfl, rfl⟩, hq⟩
        exact List.mem_append.mpr (Or.inr ((hmem q).mpr this))

theorem chunkInv_fold (o : TickOracle) (order : List Chunk) :
    ∀ (cx : Ctx) (V : List Pos) (D : List Chunk), ChunkInv c s0 cx V D → order.Nodup →
      (∀ ch ∈ order, ch ∉ D) →
      ∃ cx', order.foldlM (fun cx ch =>
          (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' ∧
        ∃ V', ChunkInv c s0 cx' V' (D ++ order) := by
  induction order with
  | nil => intro cx V D hI _ _; exact ⟨cx, rfl, V, by simpa using hI⟩
  | cons ch order ih =>
    intro cx V D hI hnd hdis
    obtain ⟨cx1, h1, V1, hI1⟩ := chunkInv_step o hI (hdis ch (by simp))
    have hnd' := List.nodup_cons.mp hnd
    obtain ⟨cx', h', V', hI'⟩ := ih cx1 V1 (D ++ [ch]) hI1 hnd'.2 (by
      intro c' hc' hcD
      rcases List.mem_append.mp hcD with h | h
      · exact hdis c' (by simp [hc']) h
      · simp at h; subst h; exact hnd'.1 hc')
    refine ⟨cx', ?_, V', by simpa using hI'⟩
    simp only [List.foldlM_cons]
    rw [h1]
    exact h'

end

/-! ### The tick -/

structure TickResult (c : Config) (s s' : St) : Prop where
  wf : Wf s'
  lok : ListsOK c s'
  count : s'.N = s.N
  phi : s'.phi ≤ s.phi + s'.listTotal
  one_two : ∀ q, HasState s q 1 → HasState s' q 2
  three_two : ∀ q, HasState s' q 3 → HasState s q 2

/-- The forward-moving cells in piston lists. -/
def St.fwdTotal (s : St) : Int := ∑ p ∈ s.lists.keys.toFinset, s.fwdLen p

theorem sum_fwd_le_fwdTotal {s : St} {V : List Pos} (hV : V.Nodup) :
    ((V.map fun p => s.fwdLen p).sum) ≤ s.fwdTotal := by
  classical
  have h1 : ((V.map fun p => s.fwdLen p).sum) = ∑ p ∈ V.toFinset, s.fwdLen p := by
    rw [List.sum_toFinset _ hV]
  have h0 : ∀ p, p ∉ s.lists.keys.toFinset → s.fwdLen p = 0 := by
    intro p hp
    rw [List.mem_toFinset, ExtTreeMap.mem_keys] at hp
    have : s.lists[p]? = none := ExtTreeMap.getElem?_eq_none hp
    simp [St.fwdLen, St.list, ExtTreeMap.getD_eq_getD_getElem?, this]
  have h2 : ∑ p ∈ V.toFinset, s.fwdLen p ≤ ∑ p ∈ s.lists.keys.toFinset ∪ V.toFinset, s.fwdLen p :=
    Finset.sum_le_sum_of_subset_of_nonneg Finset.subset_union_right
      (fun p _ _ => St.fwdLen_nonneg s p)
  have h3 : ∑ p ∈ s.lists.keys.toFinset, s.fwdLen p =
      ∑ p ∈ s.lists.keys.toFinset ∪ V.toFinset, s.fwdLen p :=
    Finset.sum_subset Finset.subset_union_left (fun p _ hp => h0 p hp)
  rw [h1, St.fwdTotal, h3]; exact h2

theorem sum_list_le_listTotal {s : St} {V : List Pos} (hV : V.Nodup) :
    ((V.map fun p => ((s.list p).length : Int)).sum) ≤ s.listTotal := by
  have h1 : ((V.map fun p => ((s.list p).length : Int)).sum) =
      ((∑ p ∈ V.toFinset, (s.list p).length : Nat) : Int) := by
    rw [List.sum_toFinset _ hV, Nat.cast_list_sum, List.map_map]
    rfl
  rw [h1, St.listTotal]
  have : ∑ p ∈ V.toFinset, (s.list p).length ≤ ∑ p ∈ s.lists.keys.toFinset, (s.list p).length := by
    apply Finset.sum_le_sum_of_ne_zero
    intro p _ hne
    rw [List.mem_toFinset, ExtTreeMap.mem_keys]
    by_contra hk
    apply hne
    have : s.lists[p]? = none := ExtTreeMap.getElem?_eq_none hk
    simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, this]
  exact_mod_cast this

theorem tick_spec {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (o : TickOracle) :
    ∃ s', tick c o s = .ok s' ∧ TickResult c s s' := by
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hW0 : Wf s0 := tickStart_wf hW
  have hL0 : ListsOK c s0 := tickStart_lok hW hL
  have hI0 : ChunkInv c s0 ⟨s0, pw⟩ [] [] :=
    ⟨⟨hW0, hL0, List.nodup_nil, fun _ _ _ _ _ _ => Iff.rfl, fun _ h => by simp at h,
      fun _ h => by simp at h, rfl, by simp, by simp, fun _ h => by simp at h⟩,
      fun _ h => by simp at h, fun _ h => by simp at h⟩
  set order := (o.chunks s0 (occupiedChunks c s0)).val with horder
  have hperm := (o.chunks s0 (occupiedChunks c s0)).property
  obtain ⟨cx', hfold, V, hI⟩ := chunkInv_fold o order ⟨s0, pw⟩ [] [] hI0
    (hperm.nodup_iff.mpr occupiedChunks_nodup) (fun _ _ h => by simp at h)
  have htick : tick c o s = .ok cx'.st := by
    unfold tick
    simp only [bind, Except.bind, pure, Except.pure]
    rw [show clearAngry (powerStage s).1 (powerStage s).2 = s0 from rfl]
    rw [hfold]
  refine ⟨cx'.st, htick, ⟨hI.tick.wf, hI.tick.lok, ?_, ?_, ?_, ?_⟩⟩
  · rw [hI.tick.count]; exact (tickStart_count hW).1
  · have := hI.tick.phi
    have := sum_list_le_listTotal (s := cx'.st) hI.tick.nodup
    rw [(tickStart_count hW).2] at *
    omega
  · -- every frozen piston was visited
    have hvis : ∀ q, (∃ d st an k, Frozen s0 q d st an k) → q ∈ V := by
      intro q hf
      refine hI.done q ?_ hf
      obtain ⟨d, st, an, k, -, hq⟩ := hf
      simp only [List.nil_append]
      exact hperm.mem_iff.mpr (chunk_mem_occupied (by rw [hq]; rfl))
    intro q h1
    have h1' := (tickStart_hasState hW).mpr h1
    obtain ⟨d, st, an, hf⟩ := (hasState_frozen (by decide)).mp h1'
    exact hI.tick.one_two q (hvis q ⟨d, st, an, 1, hf⟩) h1'
  · have hvis : ∀ q, (∃ d st an k, Frozen s0 q d st an k) → q ∈ V := by
      intro q hf
      refine hI.done q ?_ hf
      obtain ⟨d, st, an, k, -, hq⟩ := hf
      simp only [List.nil_append]
      exact hperm.mem_iff.mpr (chunk_mem_occupied (by rw [hq]; rfl))
    intro q h3
    apply (tickStart_hasState hW).mp
    by_cases hqV : q ∈ V
    · exact hI.tick.three_two q hqV h3
    · obtain ⟨d, st, an, hf⟩ := (hasState_frozen (by decide)).mp h3
      have := (hI.tick.frozen q hqV d st an 3).mp hf
      exact absurd (hvis q ⟨d, st, an, 3, this⟩) hqV

end FF
