/-
The rest accounting over one tick: for every oracle,
* the number of pistons is kept and their X sum rises by at most the number of moving
  pistons afterwards;
* new extensions + moving angry + frozen angry pistons afterwards are at most the resting
  (state 0, not moving) + moving angry + frozen angry pistons before;
* pistons in states 1 and 2 before are exactly those in states 2 and 3 after (as counts).
-/
import Formal.Lemmas.Rest
import Formal.Lemmas.Static

namespace FF

open Std

/-- Resting pistons: state 0, not moving. -/
def St.restP (s : St) : Finset Pos := s.cellsWith fun _ b => match b with
  | .piston _ _ _ k false => k.val == 0
  | _ => false

/-- Moving pistons. -/
def St.movP (s : St) : Finset Pos := s.cellsWith fun _ b => b.isPiston && b.moving

/-- Moving angry pistons. -/
def St.angryMov (s : St) : Finset Pos := s.cellsWith fun _ b => match b with
  | .piston _ _ true _ true => true
  | _ => false

/-- Angry tokens: moving angry and frozen angry pistons. -/
def St.tokens (s : St) : Nat := s.angryMov.card + s.fAngry.card

/-! ### The powered set -/

theorem powerStage_pw_piston {s : St} {q : Pos} (h : (powerStage s).2.contains q = true) :
    ∃ d st an k, s.get q = some (.piston d st an k false) := by
  have key : ∀ (L : List (Pos × Block)) (acc : ExtTreeSet Pos),
      (L.foldl (fun acc e => if pistonPowered s e.1 then acc.insert e.1 else acc) acc).contains q
        = true → acc.contains q = true ∨ pistonPowered s q = true := by
    intro L
    induction L with
    | nil => intro acc h; exact Or.inl h
    | cons e L ih =>
      intro acc h
      simp only [List.foldl_cons] at h
      rcases ih _ h with h' | h'
      · split at h'
        · rename_i hp
          rw [ExtTreeSet.contains_insert] at h'
          rcases Bool.or_eq_true_iff.mp h' with h'' | h''
          · have : e.1 = q := by simpa using h''
            subst this; exact Or.inr hp
          · exact Or.inl h''
        · exact Or.inl h'
      · exact Or.inr h'
  have hpw : (powerStage s).2 = s.world.foldl
      (fun acc p _ => if pistonPowered s p then acc.insert p else acc) ∅ := rfl
  rw [hpw, ExtTreeMap.foldl_eq_foldl_toList] at h
  rcases key _ _ h with h' | h'
  · simp at h'
  · unfold pistonPowered at h'
    split at h'
    · rename_i d st an k hg
      exact ⟨d, _, _, _, hg⟩
    · cases h'

/-! ### The tick invariant -/

structure TickInv2 (c : Config) (s0 : St) (pw0 : ExtTreeSet Pos) (cx : Ctx) (V : List Pos) :
    Prop where
  base : TickInv c s0 cx V
  lists_unv : ∀ p, p ∉ V → cx.st.lists[p]? = s0.lists[p]?
  cells_unv : ∀ p, p ∉ V → ∀ q ∈ cx.st.list p, cx.st.get q = s0.get q
  pw_sub : ∀ q, cx.powered.contains q = true → ∃ d st an k, s0.get q = some (.piston d st an k false)
  kc : (cx.st.cls isPK).card = (s0.cls isPK).card
  psi : cx.st.xsum isPK ≤ s0.xsum isPK + (V.map fun p => (cx.st.lcount isPK p : Int)).sum
  pot : pot s0 cx V ≤ pot s0 ⟨s0, pw0⟩ []
  st2v : ∀ q ∈ V, HasState s0 q 2 → HasState cx.st q 2 ∨ HasState cx.st q 3
  st2fromv : ∀ q ∈ V, HasState cx.st q 2 → HasState s0 q 1 ∨ HasState s0 q 2

section
variable {c : Config} {s0 : St} {pw0 : ExtTreeSet Pos}

theorem list_cell_moving {s : St} (hW : Wf s) {p q : Pos} (hq : q ∈ s.list p) :
    ∃ b, s.get q = some b ∧ b.moving = true := by
  cases hl : s.lists[p]? with
  | none => simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl] at hq
  | some L =>
    have : s.list p = L := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl]
    exact hW.list_moving p L q hl (this ▸ hq)

theorem list_cells_disjoint {s : St} (hW : Wf s) {p p' q : Pos} (hq : q ∈ s.list p)
    (hq' : q ∈ s.list p') : p = p' := by
  cases hl : s.lists[p]? with
  | none => simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl] at hq
  | some L =>
    cases hl' : s.lists[p']? with
    | none => simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl'] at hq'
    | some L' =>
      have e1 : s.list p = L := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl]
      have e2 : s.list p' = L' := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl']
      exact hW.list_disjoint p p' L L' q hl hl' (e1 ▸ hq) (e2 ▸ hq')

theorem tickInv2_step {cx : Ctx} {V : List Pos} {pos : Pos} (hI : TickInv2 c s0 pw0 cx V)
    (hpos : pos ∉ V) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧ TickInv2 c s0 pw0 cx' (V ++ [pos]) := by
  obtain ⟨cx', h, hB⟩ := tickInv_step hI.base hpos
  obtain ⟨cx'', h', hM⟩ := turn_more (c := c) (pos := pos) hI.base.wf
  rw [h] at h'; cases h'
  obtain ⟨cx1, h1, hE⟩ := turn_effect (c := c) (pos := pos) hI.base.wf hI.base.lok
  rw [h] at h1; cases h1
  have hW := hI.base.wf
  -- cells of other lists keep their blocks
  have hkeepL : ∀ p, p ≠ pos → ∀ q ∈ cx.st.list p, cx'.st.get q = cx.st.get q := by
    intro p hp q hq
    obtain ⟨b, hb, hm⟩ := list_cell_moving hW hq
    rw [hM.keep q b hb hm (fun hq' => hp (list_cells_disjoint hW hq hq')), hb]
  have hlist : ∀ p, p ≠ pos → cx'.st.list p = cx.st.list p := by
    intro p hp
    simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hE.lists_ne p hp]
  refine ⟨cx', h, hB, ?_, ?_, ?_, hM.kc.trans hI.kc, ?_, ?_, ?_, ?_⟩
  · intro p hp
    simp only [List.mem_append, List.mem_singleton, not_or] at hp
    rw [hE.lists_ne p hp.2]; exact hI.lists_unv p hp.1
  · intro p hp q hq
    simp only [List.mem_append, List.mem_singleton, not_or] at hp
    rw [hlist p hp.2] at hq
    rw [hkeepL p hp.2 q hq]; exact hI.cells_unv p hp.1 q hq
  · intro q hq; exact hI.pw_sub q (hE.powered q hq)
  · have hsum : (V.map fun p => (cx'.st.lcount isPK p : Int)) =
        (V.map fun p => (cx.st.lcount isPK p : Int)) := by
      apply List.map_congr_left
      intro p hp
      have hne : p ≠ pos := by rintro rfl; exact hpos hp
      unfold St.lcount
      congr 2
      ext q
      simp only [Finset.mem_filter, St.mem_cls, hlist p hne]
      constructor
      · rintro ⟨⟨b, hb, hk⟩, hq⟩
        exact ⟨⟨b, by rw [← hkeepL p hne q hq]; exact hb, hk⟩, hq⟩
      · rintro ⟨⟨b, hb, hk⟩, hq⟩
        exact ⟨⟨b, by rw [hkeepL p hne q hq]; exact hb, hk⟩, hq⟩
    simp only [List.map_append, List.map_cons, List.map_nil, List.sum_append, List.sum_cons,
      List.sum_nil, hsum]
    have := hM.psi
    have := hI.psi
    omega
  · refine _root_.le_trans (hM.pot s0 V hpos ?_ ?_) hI.pot
    · intro h1
      unfold isState1 at h1 ⊢
      split at h1
      · rename_i d st an k hg
        have hk : k.val = 1 := by simpa using h1
        have hf := (hI.base.frozen pos hpos d st an k).mpr ⟨by omega, hg⟩
        rw [hf.2]; simpa using hk
      · cases h1
    · intro q hq
      cases hp : cx.powered.contains q with
      | false => rfl
      | true =>
        exfalso
        obtain ⟨d, st, an, k, hs⟩ := hI.pw_sub q hp
        obtain ⟨b, hb, hm⟩ := list_cell_moving hW hq
        rw [hI.cells_unv pos hpos q hq, hs] at hb
        cases hb; simp [Block.moving] at hm
  · intro q hq h2
    rcases List.mem_append.mp hq with hqV | hq
    · have hne : q ≠ pos := by rintro rfl; exact hpos hqV
      rcases hI.st2v q hqV h2 with ⟨d, st, an, hf⟩ | ⟨d, st, an, hf⟩
      · exact Or.inl ⟨d, st, an, ((hE.frozen_ne q hne d st an 2).mpr ⟨by decide, hf⟩).2⟩
      · exact Or.inr ⟨d, st, an, ((hE.frozen_ne q hne d st an 3).mpr ⟨by decide, hf⟩).2⟩
    · simp at hq; subst hq
      obtain ⟨d, st, an, hf⟩ := h2
      have := ((hI.base.frozen q hpos d st an 2).mpr ⟨by decide, hf⟩).2
      exact hM.st2 d st an this
  · intro q hq h2
    rcases List.mem_append.mp hq with hqV | hq
    · have hne : q ≠ pos := by rintro rfl; exact hpos hqV
      obtain ⟨d, st, an, hf⟩ := h2
      exact hI.st2fromv q hqV ⟨d, st, an, ((hE.frozen_ne q hne d st an 2).mp ⟨by decide, hf⟩).2⟩
    · simp at hq; subst hq
      rcases hM.st2from h2 with ⟨d, st, an, hf⟩ | ⟨d, st, an, hf⟩
      · exact Or.inl ⟨d, st, an, ((hI.base.frozen q hpos d st an 1).mp ⟨by decide, hf⟩).2⟩
      · exact Or.inr ⟨d, st, an, ((hI.base.frozen q hpos d st an 2).mp ⟨by decide, hf⟩).2⟩

end


section
variable {c : Config} {s0 : St} {pw0 : ExtTreeSet Pos}

theorem tickInv2_fold (ps : List Pos) : ∀ (cx : Ctx) (V : List Pos), TickInv2 c s0 pw0 cx V →
    ps.Nodup → (∀ p ∈ ps, p ∉ V) →
    ∃ cx', ps.foldlM (pistonTurn c) cx = .ok cx' ∧ TickInv2 c s0 pw0 cx' (V ++ ps) := by
  induction ps with
  | nil => intro cx V hI _ _; exact ⟨cx, rfl, by simpa using hI⟩
  | cons p ps ih =>
    intro cx V hI hnd hdis
    obtain ⟨cx1, h1, hI1⟩ := tickInv2_step hI (hdis p (by simp))
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

structure ChunkInv2 (c : Config) (s0 : St) (pw0 : ExtTreeSet Pos) (cx : Ctx) (V : List Pos)
    (D : List Chunk) : Prop where
  tick : TickInv2 c s0 pw0 cx V
  vchunks : ∀ p ∈ V, c.chunkOf p ∈ D
  done : ∀ q, c.chunkOf q ∈ D → (∃ d st an k, Frozen s0 q d st an k) → q ∈ V

theorem chunkInv2_step (o : TickOracle) {cx : Ctx} {V : List Pos} {D : List Chunk} {ch : Chunk}
    (hI : ChunkInv2 c s0 pw0 cx V D) (hch : ch ∉ D) :
    ∃ cx', (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx = .ok cx' ∧
      ∃ V', ChunkInv2 c s0 pw0 cx' V' (D ++ [ch]) := by
  set ps := (o.pistons cx.st ch (candidates c cx.st ch)).val with hps
  have hperm := (o.pistons cx.st ch (candidates c cx.st ch)).property
  have hnd : ps.Nodup := hperm.nodup_iff.mpr candidates_nodup
  have hmem : ∀ p, p ∈ ps ↔ p ∈ candidates c cx.st ch := fun p => hperm.mem_iff
  have hdis : ∀ p ∈ ps, p ∉ V := by
    intro p hp hpV
    have := ((mem_candidates.mp ((hmem p).mp hp)).2)
    exact hch (this ▸ hI.vchunks p hpV)
  obtain ⟨cx', h, hT⟩ := tickInv2_fold ps cx V hI.tick hnd hdis
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
        have hfz' := (hI.tick.base.frozen q hqV d st an k).mpr hfz
        have : q ∈ candidates c cx.st ch :=
          mem_candidates.mpr ⟨⟨_, hfz'.2, rfl, rfl⟩, hq⟩
        exact List.mem_append.mpr (Or.inr ((hmem q).mpr this))

theorem chunkInv2_fold (o : TickOracle) (order : List Chunk) :
    ∀ (cx : Ctx) (V : List Pos) (D : List Chunk), ChunkInv2 c s0 pw0 cx V D → order.Nodup →
      (∀ ch ∈ order, ch ∉ D) →
      ∃ cx', order.foldlM (fun cx ch =>
          (o.pistons cx.st ch (candidates c cx.st ch)).val.foldlM (pistonTurn c) cx) cx = .ok cx' ∧
        ∃ V', ChunkInv2 c s0 pw0 cx' V' (D ++ order) := by
  induction order with
  | nil => intro cx V D hI _ _; exact ⟨cx, rfl, V, by simpa using hI⟩
  | cons ch order ih =>
    intro cx V D hI hnd hdis
    obtain ⟨cx1, h1, V1, hI1⟩ := chunkInv2_step o hI (hdis ch (by simp))
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

/-! ### Counting at the end of the tick -/

theorem sum_lcount_le {s : St} (hW : Wf s) {V : List Pos} (hV : V.Nodup) :
    (V.map fun p => (s.lcount isPK p : Int)).sum ≤ s.movP.card := by
  classical
  have h1 : (V.map fun p => (s.lcount isPK p : Int)).sum =
      ((∑ p ∈ V.toFinset, s.lcount isPK p : Nat) : Int) := by
    rw [List.sum_toFinset _ hV, Nat.cast_list_sum, List.map_map]; rfl
  rw [h1]
  have hdisj : ∀ p ∈ V.toFinset, ∀ p' ∈ V.toFinset, p ≠ p' →
      Disjoint ((s.cls isPK).filter (· ∈ s.list p)) ((s.cls isPK).filter (· ∈ s.list p')) := by
    intro p _ p' _ hne
    rw [Finset.disjoint_left]
    intro q hq hq'
    exact hne (list_cells_disjoint hW (Finset.mem_filter.mp hq).2 (Finset.mem_filter.mp hq').2)
  have : ∑ p ∈ V.toFinset, s.lcount isPK p =
      (V.toFinset.biUnion fun p => (s.cls isPK).filter (· ∈ s.list p)).card := by
    rw [Finset.card_biUnion hdisj]; rfl
  rw [this]
  have hsub : (V.toFinset.biUnion fun p => (s.cls isPK).filter (· ∈ s.list p)) ⊆ s.movP := by
    intro q hq
    obtain ⟨p, -, hq⟩ := Finset.mem_biUnion.mp hq
    obtain ⟨hc, hl⟩ := Finset.mem_filter.mp hq
    obtain ⟨b, hb, hk⟩ := St.mem_cls.mp hc
    obtain ⟨b', hb', hm⟩ := list_cell_moving hW hl
    rw [hb] at hb'; cases hb'
    exact St.mem_cellsWith.mpr ⟨b, hb, by simp [Block.isPiston, isPK] at hk ⊢; exact ⟨hk, hm⟩⟩
  exact_mod_cast Finset.card_le_card hsub


/-! ### The tick start -/

section
variable {s : St} (hW : Wf s)
include hW

theorem ts_get_piston {q : Pos} {d : Dir} {st mv : Bool} {k : Fin 4} :
    (∃ an', (tickStart s).get q = some (.piston d st an' k mv)) ↔
      (∃ an', s.get q = some (.piston d st an' k mv)) := by
  constructor
  · rintro ⟨an', h⟩
    exact mapBits_piston (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW) h
  · rintro ⟨an', h⟩
    exact mapBits_piston' (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW) h

theorem ts_cls (P : Kind → Bool) : (tickStart s).cls P = s.cls P := by
  ext q
  rw [St.mem_cls, St.mem_cls, tickStart_get]
  cases s.get q with
  | none => simp
  | some b =>
    have hk := (tickStart_bits hW q).kind b
    simp only [Function.comp_apply] at hk
    simp [hk]

theorem ts_restP : (tickStart s).restP = s.restP := by
  ext q
  unfold St.restP
  rw [St.mem_cellsWith, St.mem_cellsWith]
  constructor
  · rintro ⟨b, hb, hk⟩
    cases b with
    | piston d st an k mv =>
      cases mv
      · obtain ⟨an', h⟩ := (ts_get_piston hW).mp ⟨an, hb⟩
        exact ⟨_, h, by simpa using hk⟩
      · simp at hk
    | _ => simp at hk
  · rintro ⟨b, hb, hk⟩
    cases b with
    | piston d st an k mv =>
      cases mv
      · obtain ⟨an', h⟩ := (ts_get_piston hW).mpr ⟨an, hb⟩
        exact ⟨_, h, by simpa using hk⟩
      · simp at hk
    | _ => simp at hk

theorem ts_angryMov : (tickStart s).angryMov = s.angryMov := by
  ext q
  unfold St.angryMov
  rw [St.mem_cellsWith, St.mem_cellsWith, tickStart_get]
  cases s.get q with
  | none => simp
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases h : (powerStage s).2.contains q <;> cases mv <;> cases an <;>
        simp [calmAt, unpulse, h]
    | observer d p m => cases p <;> simp [calmAt, unpulse]
    | _ => simp [calmAt, unpulse]

theorem ts_fAngry : (tickStart s).fAngry ⊆ s.fAngry := by
  intro q hq
  obtain ⟨b, hb, hk⟩ := St.mem_fAngry.mp hq
  rw [tickStart_get] at hb
  cases hs : s.get q with
  | none => rw [hs] at hb; cases hb
  | some b0 =>
    rw [hs] at hb
    simp only [Option.map_some, Option.some.injEq, Function.comp] at hb
    refine St.mem_fAngry.mpr ⟨b0, hs, ?_⟩
    subst hb
    cases b0 with
    | piston d st an k mv =>
      cases mv <;> simp only [unpulse, calmAt] at hk ⊢
      · split at hk <;> simp_all [faB]
      · simp [faB] at hk
    | observer d p m => cases p <;> simp [unpulse, calmAt, faB] at hk
    | _ => simp [unpulse, calmAt, faB] at hk

end

/-! ### One tick -/

structure TickResult2 (s s' : St) : Prop where
  kc : (s'.cls isPK).card = (s.cls isPK).card
  psi : s'.xsum isPK ≤ s.xsum isPK + s'.movP.card
  rest : s'.nState 1 + s'.tokens ≤ s.restP.card + s.tokens
  lo : s.nState 1 + s.nState 2 ≤ s'.nState 2 + s'.nState 3
  hi : s'.nState 2 + s'.nState 3 ≤ s.nState 1 + s.nState 2
  hiSub : s'.stateCells 2 ∪ s'.stateCells 3 ⊆ s.stateCells 1 ∪ s.stateCells 2
  dirHi : ∀ q d st an (k : Fin 4), s'.get q = some (.piston d st an k false) →
    (k.val = 2 ∨ k.val = 3) →
    ∃ (st' an' : Bool) (k' : Fin 4), s.get q = some (.piston d st' an' k' false)
  phiF : s'.phi ≤ s.phi + s'.fwdTotal

theorem tick_spec2 {c : Config} {s : St} (hW : Wf s) (hL : ListsOK c s) (o : TickOracle) :
    ∃ s', tick c o s = .ok s' ∧ TickResult2 s s' := by
  classical
  set s0 := tickStart s with hs0
  set pw := (powerStage s).2 with hpw
  have hW0 : Wf s0 := tickStart_wf hW
  have hL0 : ListsOK c s0 := tickStart_lok hW hL
  have hI0 : ChunkInv2 c s0 pw ⟨s0, pw⟩ [] [] := by
    refine ⟨⟨⟨hW0, hL0, List.nodup_nil, fun _ _ _ _ _ _ => Iff.rfl, fun _ h => by simp at h,
      fun _ h => by simp at h, rfl, by simp, by simp, fun _ h => by simp at h⟩, fun _ _ => rfl, fun _ _ _ _ => rfl, ?_, rfl,
      by simp, _root_.le_refl _, fun _ h => by simp at h, fun _ h => by simp at h⟩,
      fun _ h => by simp at h, fun _ h => by simp at h⟩
    intro q hq
    obtain ⟨d, st, an, k, h⟩ := powerStage_pw_piston hq
    obtain ⟨an', h'⟩ := (ts_get_piston hW).mpr ⟨an, h⟩
    exact ⟨d, st, an', k, h'⟩
  set order := (o.chunks s0 (occupiedChunks c s0)).val with horder
  have hperm := (o.chunks s0 (occupiedChunks c s0)).property
  obtain ⟨cx', hfold, V, hI⟩ := chunkInv2_fold o order ⟨s0, pw⟩ [] [] hI0
    (hperm.nodup_iff.mpr occupiedChunks_nodup) (fun _ _ h => by simp at h)
  have htick : tick c o s = .ok cx'.st := by
    unfold tick
    simp only [bind, Except.bind, pure, Except.pure]
    rw [show clearAngry (powerStage s).1 (powerStage s).2 = s0 from rfl]
    rw [hfold]
  have hT := hI.tick
  have hWe := hT.base.wf
  have hvis : ∀ q, (∃ d st an k, Frozen s0 q d st an k) → q ∈ V := by
    intro q hf
    refine hI.done q ?_ hf
    obtain ⟨d, st, an, k, -, hq⟩ := hf
    simp only [List.nil_append]
    exact hperm.mem_iff.mpr (chunk_mem_occupied (by rw [hq]; rfl))
  have hhiSub : cx'.st.stateCells 2 ∪ cx'.st.stateCells 3 ⊆ s.stateCells 1 ∪ s.stateCells 2 := by
      intro q hq
      rcases Finset.mem_union.mp hq with h | h
      · have h2 := St.mem_stateCells.mp h
        by_cases hqV : q ∈ V
        · rcases hT.st2fromv q hqV h2 with h' | h'
          · exact Finset.mem_union_left _ (St.mem_stateCells.mpr ((tickStart_hasState hW).mp h'))
          · exact Finset.mem_union_right _ (St.mem_stateCells.mpr ((tickStart_hasState hW).mp h'))
        · obtain ⟨d, st, an, hf⟩ := h2
          have := (hT.base.frozen q hqV d st an 2).mp ⟨by decide, hf⟩
          exact absurd (hvis q ⟨d, st, an, 2, this⟩) hqV
      · have h3 := St.mem_stateCells.mp h
        by_cases hqV : q ∈ V
        · exact Finset.mem_union_right _ (St.mem_stateCells.mpr
            ((tickStart_hasState hW).mp (hT.base.three_two q hqV h3)))
        · obtain ⟨d, st, an, hf⟩ := h3
          have := (hT.base.frozen q hqV d st an 3).mp ⟨by decide, hf⟩
          exact absurd (hvis q ⟨d, st, an, 3, this⟩) hqV
  refine ⟨cx'.st, htick, ?_, ?_, ?_, ?_, ?_, hhiSub, ?_, ?_⟩
  · rw [hT.kc, ts_cls hW]
  · have h1 := hT.psi
    have h2 := sum_lcount_le hWe hT.base.nodup
    have h3 : s0.xsum isPK = s.xsum isPK := by unfold St.xsum; rw [ts_cls hW]
    omega
  · -- new extensions
    have hn1 : cx'.st.stateCells 1 ⊆ cx'.st.newExt s0 := by
      intro q hq
      obtain ⟨d, st, an, h⟩ := St.mem_stateCells.mp hq
      refine St.mem_newExt.mpr ⟨_, h, ?_⟩
      simp only [newExtB, show (1 : Fin 4).val = 1 from rfl, beq_self_eq_true, Bool.true_and,
        Bool.not_eq_true']
      unfold isState1
      split
      · rename_i d' st' an' k' hg
        by_contra hk
        have hk1 : k' = 1 := Fin.ext (by simpa using hk)
        subst hk1
        have hqV := hvis q ⟨d', st', an', 1, by decide, hg⟩
        obtain ⟨d2, st2, an2, h2⟩ := hT.base.one_two q hqV ⟨d', st', an', hg⟩
        rw [h] at h2; cases h2
      · rfl
    have hG : cx'.st.angryMov ⊆ cx'.elig V := by
      intro q hq
      unfold St.angryMov at hq
      obtain ⟨b, hb, hk⟩ := St.mem_cellsWith.mp hq
      refine Ctx.mem_elig.mpr ⟨b, hb, ?_⟩
      cases b with
      | piston d st an k mv =>
        cases an <;> cases mv <;> simp at hk
        have := hWe.moving_piston _ _ _ _ _ hb
        simp [eligB, this]
      | _ => simp at hk
    have hpot := hT.pot
    have hstart : (Ctx.elig ⟨s0, pw⟩ []) ⊆ s0.restP ∪ s0.angryMov := by
      intro q hq
      obtain ⟨b, hb, hk⟩ := Ctx.mem_elig.mp hq
      cases b with
      | piston d st an k mv =>
        simp only [eligB, Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true] at hk
        cases mv
        · exact Finset.mem_union_left _ (St.mem_cellsWith.mpr ⟨_, hb, by simp [hk.1]⟩)
        · rcases hk.2 with h | h
          · subst h; exact Finset.mem_union_right _ (St.mem_cellsWith.mpr ⟨_, hb, rfl⟩)
          · simp at h
      | _ => simp [eligB] at hk
    have hne0 : (s0.newExt s0).card = 0 := by
      rw [Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
      intro q hq
      obtain ⟨b, hb, hk⟩ := St.mem_newExt.mp hq
      cases b with
      | piston d st an k mv =>
        cases mv
        · simp only [newExtB, isState1, hb, Bool.and_eq_true, beq_iff_eq] at hk
          simp [hk.1] at hk
        · simp [newExtB] at hk
      | _ => simp [newExtB] at hk
    have c1 := Finset.card_le_card hn1
    have c2 := Finset.card_le_card hG
    have c3 := (Finset.card_le_card hstart).trans (Finset.card_union_le _ _)
    have c4 : s0.fAngry.card ≤ s.fAngry.card := Finset.card_le_card (ts_fAngry hW)
    rw [ts_restP hW, ts_angryMov hW] at c3
    unfold pot at hpot
    unfold St.nState St.tokens
    dsimp only at hpot
    omega
  · -- states 1, 2 before go to states 2, 3 after
    have hsub : s.stateCells 1 ∪ s.stateCells 2 ⊆ cx'.st.stateCells 2 ∪ cx'.st.stateCells 3 := by
      intro q hq
      rcases Finset.mem_union.mp hq with h | h
      · have h1 := (tickStart_hasState hW).mpr (St.mem_stateCells.mp h)
        obtain ⟨d, st, an, hf⟩ := h1
        exact Finset.mem_union_left _ (St.mem_stateCells.mpr
          (hT.base.one_two q (hvis q ⟨d, st, an, 1, by decide, hf⟩) ⟨d, st, an, hf⟩))
      · have h2 := (tickStart_hasState hW).mpr (St.mem_stateCells.mp h)
        obtain ⟨d, st, an, hf⟩ := h2
        rcases hT.st2v q (hvis q ⟨d, st, an, 2, by decide, hf⟩) ⟨d, st, an, hf⟩ with h' | h'
        · exact Finset.mem_union_left _ (St.mem_stateCells.mpr h')
        · exact Finset.mem_union_right _ (St.mem_stateCells.mpr h')
    have hd1 : Disjoint (s.stateCells 1) (s.stateCells 2) := by
      rw [Finset.disjoint_left]; intro q h1 h2
      obtain ⟨_, _, _, e1⟩ := St.mem_stateCells.mp h1
      obtain ⟨_, _, _, e2⟩ := St.mem_stateCells.mp h2
      rw [e1] at e2; cases e2
    have := Finset.card_le_card hsub
    rw [Finset.card_union_of_disjoint hd1] at this
    have := Finset.card_union_le (cx'.st.stateCells 2) (cx'.st.stateCells 3)
    unfold St.nState; omega
  · have hsub := hhiSub
    have hd1 : Disjoint (cx'.st.stateCells 2) (cx'.st.stateCells 3) := by
      rw [Finset.disjoint_left]; intro q h1 h2
      obtain ⟨_, _, _, e1⟩ := St.mem_stateCells.mp h1
      obtain ⟨_, _, _, e2⟩ := St.mem_stateCells.mp h2
      rw [e1] at e2; cases e2
    have := Finset.card_le_card hsub
    rw [Finset.card_union_of_disjoint hd1] at this
    have := Finset.card_union_le (s.stateCells 1) (s.stateCells 2)
    unfold St.nState; omega

  · intro q d st an k hg hk
    by_cases hqV : q ∈ V
    · obtain ⟨st', an', k', h'⟩ := hT.base.hiD q hqV d st an k hg hk
      obtain ⟨an'', h''⟩ := (ts_get_piston hW).mp ⟨an', h'⟩
      exact ⟨st', an'', k', h''⟩
    · have := (hT.base.frozen q hqV d st an k).mp ⟨by omega, hg⟩
      exact absurd (hvis q ⟨d, st, an, k, this⟩) hqV
  · have := hT.base.phiF
    have := sum_fwd_le_fwdTotal (s := cx'.st) hT.base.nodup
    have h3 : s0.phi = s.phi := (tickStart_count hW).2
    omega

end FF
