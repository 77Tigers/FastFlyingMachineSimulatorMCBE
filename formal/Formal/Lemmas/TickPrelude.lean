/-
The start of a tick (power stage, angry clearing) only changes observer pulses and
`angry` bits, so it keeps everything the later proofs track; and the facts about the
chunk list and a chunk's candidate pistons.
-/
import Formal.Lemmas.Turn

namespace FF

open Std

/-- A nonmoving piston in state `k` sits at `q` (any facing, stickiness, angry bit). -/
def HasState (s : St) (q : Pos) (k : Fin 4) : Prop :=
  ∃ d st an, s.get q = some (.piston d st an k false)

/-- `f` changes at most an observer's pulse or a piston's angry bit. -/
structure BitsOnly (f : Block → Block) : Prop where
  kind : ∀ b, (f b).kind = b.kind
  moving : ∀ b, (f b).moving = b.moving
  piston : ∀ d st an k mv, ∃ an', f (.piston d st an k mv) = .piston d st an' k mv
  plain : ∀ k m, f (.plain k m) = .plain k m

theorem BitsOnly.piston_inv {f : Block → Block} (hf : BitsOnly f) {b : Block} {d : Dir}
    {st an mv : Bool} {k : Fin 4} (h : f b = .piston d st an k mv) :
    ∃ an', b = .piston d st an' k mv := by
  cases b with
  | piston d' st' an' k' mv' =>
    obtain ⟨an'', h'⟩ := hf.piston d' st' an' k' mv'
    rw [h'] at h; simp only [Block.piston.injEq] at h
    obtain ⟨rfl, rfl, -, rfl, rfl⟩ := h
    exact ⟨an', rfl⟩
  | plain k' m => rw [hf.plain] at h; cases h
  | observer d' p m =>
    have := hf.kind (.observer d' p m); rw [h] at this; simp [Block.kind] at this
  | rod d' m =>
    have := hf.kind (.rod d' m); rw [h] at this; simp [Block.kind] at this

theorem BitsOnly.arm_inv {f : Block → Block} (hf : BitsOnly f) {b : Block} {m : Bool}
    (h : f b = .plain .arm m) : b = .plain .arm m := by
  have hk := hf.kind b
  rw [h] at hk
  have hm := hf.moving b
  rw [h] at hm
  cases b with
  | plain k m' => cases k <;> simp_all [Block.kind, Block.moving]
  | _ => simp [Block.kind] at hk

section MapBits
variable {s s' : St} {F : Pos → Block → Block} (hF : ∀ q, BitsOnly (F q))
  (hget : ∀ q : Pos, s'.get q = (s.get q).map (F q)) (hl : ∀ q : Pos, s'.lists[q]? = s.lists[q]?)
include hF hget hl

theorem mapBits_piston {q : Pos} {d : Dir} {st an mv : Bool} {k : Fin 4}
    (h : s'.get q = some (.piston d st an k mv)) : ∃ an', s.get q = some (.piston d st an' k mv) := by
  rw [hget] at h
  cases hq : s.get q with
  | none => rw [hq] at h; cases h
  | some b =>
    rw [hq] at h
    simp only [Option.map_some, Option.some.injEq] at h
    obtain ⟨an', rfl⟩ := (hF q).piston_inv h
    exact ⟨an', rfl⟩

theorem mapBits_piston' {q : Pos} {d : Dir} {st an mv : Bool} {k : Fin 4}
    (h : s.get q = some (.piston d st an k mv)) : ∃ an', s'.get q = some (.piston d st an' k mv) := by
  obtain ⟨an', h'⟩ := (hF q).piston d st an k mv
  exact ⟨an', by rw [hget, h]; simp [h']⟩

theorem mapBits_wf (hW : Wf s) : Wf s' := by
  constructor
  · intro p L hL
    rw [hl] at hL
    obtain ⟨d, st, an, k, hp, hk⟩ := hW.list_owner p L hL
    obtain ⟨an', h'⟩ := mapBits_piston' hF hget hl hp
    exact ⟨d, st, an', k, h', hk⟩
  · intro p L q hL hq
    rw [hl] at hL
    obtain ⟨b, hb, hm⟩ := hW.list_moving p L q hL hq
    exact ⟨F q b, by rw [hget, hb]; rfl, by rw [(hF q).moving]; exact hm⟩
  · intro p p' L L' q h1 h2
    rw [hl] at h1 h2
    exact hW.list_disjoint p p' L L' q h1 h2
  · intro p d st an k h
    obtain ⟨an', h'⟩ := mapBits_piston hF hget hl h
    exact hW.moving_piston _ _ _ _ _ h'
  · intro p h
    rw [hget] at h
    cases hq : s.get p with
    | none => rw [hq] at h; cases h
    | some b =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      exact hW.arm_still p (by rw [hq, (hF p).arm_inv h])
  · intro p d st an k mv h hk
    obtain ⟨an', h'⟩ := mapBits_piston hF hget hl h
    have harm := hW.arm_front _ _ _ _ _ _ h' hk
    rw [hget, harm]; simp [(hF _).plain]
  · intro p p' d1 d2 st1 st2 an1 an2 k1 k2 mv1 mv2 h1 h2 hk1 hk2 he
    obtain ⟨_, h1'⟩ := mapBits_piston hF hget hl h1
    obtain ⟨_, h2'⟩ := mapBits_piston hF hget hl h2
    exact hW.front_unique _ _ _ _ _ _ _ _ _ _ _ _ h1' h2' hk1 hk2 he

theorem mapBits_lok {c : Config} (h : ListsOK c s) : ListsOK c s' := by
  intro p L hL; rw [hl] at hL; exact h p L hL

theorem mapBits_body : ∀ q, q ∈ s'.body ↔ q ∈ s.body := by
  intro q
  rw [St.mem_body, St.mem_body, hget]
  cases s.get q <;> simp [(hF q).kind]

theorem mapBits_hasState {q : Pos} {k : Fin 4} : HasState s' q k ↔ HasState s q k := by
  constructor
  · rintro ⟨d, st, an, h⟩
    obtain ⟨an', h'⟩ := mapBits_piston hF hget hl h
    exact ⟨d, st, an', h'⟩
  · rintro ⟨d, st, an, h⟩
    obtain ⟨an', h'⟩ := mapBits_piston' hF hget hl h
    exact ⟨d, st, an', h'⟩

theorem mapBits_list (q : Pos) : s'.list q = s.list q := by
  simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl]

end MapBits

/-! ### The power stage and angry clearing -/

def unpulse : Block → Block
  | .observer d true m => .observer d false m
  | b => b

theorem unpulse_bits : BitsOnly unpulse where
  kind b := by
    cases b with
    | observer d p m => cases p <;> rfl
    | _ => rfl
  moving b := by
    cases b with
    | observer d p m => cases p <;> rfl
    | _ => rfl
  piston _ _ an _ _ := ⟨an, rfl⟩
  plain _ _ := rfl

def calmAt (pw : ExtTreeSet Pos) (q : Pos) : Block → Block
  | .piston d st an k false => if pw.contains q then .piston d st an k false
      else .piston d st false k false
  | b => b

theorem calmAt_bits (pw : ExtTreeSet Pos) (q : Pos) : BitsOnly (calmAt pw q) where
  kind b := by
    cases b with
    | piston d st an k mv => cases mv <;> simp [calmAt] <;> split <;> rfl
    | _ => rfl
  moving b := by
    cases b with
    | piston d st an k mv => cases mv <;> simp [calmAt] <;> split <;> rfl
    | _ => rfl
  piston d st an k mv := by
    cases mv
    · simp only [calmAt]; split
      · exact ⟨an, rfl⟩
      · exact ⟨false, rfl⟩
    · exact ⟨an, rfl⟩
  plain _ _ := rfl

theorem powerStage_get (s : St) (q : Pos) :
    (powerStage s).1.get q = (s.get q).map unpulse := by
  simp only [powerStage, St.get]
  rw [ExtTreeMap.getElem?_map]
  congr 1

theorem powerStage_lists {s : St} (hW : Wf s) (q : Pos) :
    (powerStage s).1.lists[q]? = s.lists[q]? := by
  simp only [powerStage]
  rw [ExtTreeMap.getElem?_filter']
  cases hl : s.lists[q]? with
  | none => rfl
  | some L =>
    obtain ⟨d, st, an, k, hp, -⟩ := hW.list_owner q L hl
    simp [St.get] at hp
    simp [St.get, hp]

theorem clearAngry_get (s : St) (pw : ExtTreeSet Pos) (q : Pos) :
    (clearAngry s pw).get q = (s.get q).map (calmAt pw q) := by
  simp only [clearAngry, St.get]
  rw [ExtTreeMap.getElem?_map]
  cases s.world[q]? with
  | none => rfl
  | some b =>
    cases b with
    | piston d st an k mv => cases mv <;> simp [calmAt]
    | _ => rfl

theorem clearAngry_lists (s : St) (pw : ExtTreeSet Pos) (q : Pos) :
    (clearAngry s pw).lists[q]? = s.lists[q]? := rfl

/-- The state after the power stage and angry clearing. -/
def tickStart (s : St) : St := clearAngry (powerStage s).1 (powerStage s).2

theorem tickStart_get (s : St) (q : Pos) :
    (tickStart s).get q = (s.get q).map (calmAt (powerStage s).2 q ∘ unpulse) := by
  rw [tickStart, clearAngry_get, powerStage_get, Option.map_map]

theorem comp_bits {f g : Block → Block} (hf : BitsOnly f) (hg : BitsOnly g) : BitsOnly (f ∘ g) where
  kind b := by simp [hf.kind, hg.kind]
  moving b := by simp [hf.moving, hg.moving]
  piston d st an k mv := by
    obtain ⟨a1, h1⟩ := hg.piston d st an k mv
    obtain ⟨a2, h2⟩ := hf.piston d st a1 k mv
    exact ⟨a2, by simp [h1, h2]⟩
  plain k m := by simp [hf.plain, hg.plain]

section
variable {c : Config} {s : St} (hW : Wf s)
include hW

theorem tickStart_lists (q : Pos) : (tickStart s).lists[q]? = s.lists[q]? := by
  rw [tickStart, clearAngry_lists, powerStage_lists hW]

theorem tickStart_bits : ∀ q, BitsOnly (calmAt (powerStage s).2 q ∘ unpulse) :=
  fun q => comp_bits (calmAt_bits _ q) unpulse_bits

theorem tickStart_wf : Wf (tickStart s) :=
  mapBits_wf (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW) hW

theorem tickStart_lok (h : ListsOK c s) : ListsOK c (tickStart s) :=
  mapBits_lok (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW) h

theorem tickStart_count : (tickStart s).N = s.N ∧ (tickStart s).phi = s.phi :=
  St.body_congr (mapBits_body (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW))

theorem tickStart_hasState {q : Pos} {k : Fin 4} : HasState (tickStart s) q k ↔ HasState s q k :=
  mapBits_hasState (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW)

theorem tickStart_list (q : Pos) : (tickStart s).list q = s.list q :=
  mapBits_list (tickStart_bits hW) (tickStart_get s) (tickStart_lists hW) q

end

/-! ### Chunks and candidates -/

theorem mem_candidates {c : Config} {s : St} {ch : Chunk} {q : Pos} :
    q ∈ candidates c s ch ↔
      (∃ b, s.get q = some b ∧ b.isPiston = true ∧ b.moving = false) ∧ c.chunkOf q = ch := by
  unfold candidates St.get
  simp only [List.mem_filterMap]
  constructor
  · rintro ⟨⟨p, b⟩, he, hp⟩
    split at hp
    · rename_i hc
      cases hp
      simp only [Bool.and_eq_true, Bool.not_eq_true', beq_iff_eq] at hc
      exact ⟨⟨b, ExtTreeMap.mem_toList_iff_getElem?_eq_some.mp he, hc.1.1, hc.1.2⟩, hc.2⟩
    · cases hp
  · rintro ⟨⟨b, hb, hp, hm⟩, hc⟩
    refine ⟨⟨q, b⟩, ExtTreeMap.mem_toList_iff_getElem?_eq_some.mpr hb, ?_⟩
    simp [hp, hm, hc]

theorem candidates_nodup {c : Config} {s : St} {ch : Chunk} : (candidates c s ch).Nodup := by
  unfold candidates
  have hd : (s.world.toList.map Prod.fst).Nodup := by
    rw [ExtTreeMap.map_fst_toList_eq_keys]
    exact (ExtTreeMap.distinct_keys).imp fun h e => h (by simp [e])
  -- filterMap returning the key is a sublist of the keys
  have key : ∀ L : List (Pos × Block), (L.filterMap fun (p, b) =>
      if b.isPiston && !b.moving && c.chunkOf p == ch then some p else none).Sublist
      (L.map Prod.fst) := by
    intro L
    induction L with
    | nil => simp
    | cons e L ih =>
      obtain ⟨p, b⟩ := e
      by_cases hc : (b.isPiston && !b.moving && c.chunkOf p == ch) = true
      · simp only [List.filterMap_cons, hc, ite_true, List.map_cons]; exact ih.cons₂ _
      · simp only [List.filterMap_cons, hc, Bool.false_eq_true, ite_false, List.map_cons]
        exact ih.cons _
  have hsub := key s.world.toList
  exact hsub.nodup hd

theorem chunk_mem_occupied {c : Config} {s : St} {q : Pos} (hq : (s.get q).isSome) :
    c.chunkOf q ∈ occupiedChunks c s := by
  unfold occupiedChunks
  rw [ExtTreeSet.mem_toList, ExtTreeMap.foldl_eq_foldl_toList]
  have hmem : (q, (s.get q).get hq) ∈ s.world.toList :=
    ExtTreeMap.mem_toList_iff_getElem?_eq_some.mpr (by simp [St.get])
  have mono : ∀ (L : List (Pos × Block)) (acc : ExtTreeSet Chunk) (x : Chunk), x ∈ acc →
      x ∈ L.foldl (fun acc e => acc.insert (c.chunkOf e.1)) acc := by
    intro L
    induction L with
    | nil => intro acc x h; exact h
    | cons e L ih => intro acc x h; exact ih _ _ (ExtTreeSet.mem_insert.mpr (Or.inr h))
  have key : ∀ (L : List (Pos × Block)) (acc : ExtTreeSet Chunk), (q, (s.get q).get hq) ∈ L →
      c.chunkOf q ∈ L.foldl (fun acc e => acc.insert (c.chunkOf e.1)) acc := by
    intro L
    induction L with
    | nil => intro acc h; simp at h
    | cons e L ih =>
      intro acc h
      simp only [List.foldl_cons]
      rcases List.mem_cons.mp h with h | h
      · subst h
        exact mono _ _ _ (ExtTreeSet.mem_insert.mpr (Or.inl (by simp)))
      · exact ih _ h
  exact key _ _ hmem

theorem occupiedChunks_nodup {c : Config} {s : St} : (occupiedChunks c s).Nodup :=
  (ExtTreeSet.distinct_toList).imp fun h e => h (by simp [e])

end FF
