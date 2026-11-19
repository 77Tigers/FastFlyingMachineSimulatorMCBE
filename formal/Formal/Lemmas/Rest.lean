/-
Rest accounting for pistons. A piston that extends was, at the end of the previous tick,
resting (state 0, not moving), or moving but `angry` (which needs a failed extension while
resting). The potential below makes this exact within a tick:

  new extensions + eligible pistons + frozen angry pistons

never rises during a tick, where a piston is *eligible* if it is in state 0 and could still
extend this tick (angry, or not moving, powered and not yet visited).
-/
import Formal.Lemmas.Cls
import Formal.Lemmas.TickPrelude

namespace FF

open Std

/-- The kind test for pistons. -/
def isPK (k : Kind) : Bool := k == .piston

/-- Whether `q` holds a nonmoving piston in state 1 in `s`. -/
def isState1 (s : St) (q : Pos) : Bool :=
  match s.get q with
  | some (.piston _ _ _ k false) => k.val == 1
  | _ => false

/-- A state-0 piston that could still extend this tick. -/
def eligB (pw : ExtTreeSet Pos) (V : List Pos) (q : Pos) : Block → Bool
  | .piston _ _ an k mv => k.val == 0 && (an || (!mv && pw.contains q && !decide (q ∈ V)))
  | _ => false

/-- A nonmoving state-1 piston at a cell that did not hold one at the tick start `s0`. -/
def newExtB (s0 : St) (q : Pos) : Block → Bool
  | .piston _ _ _ k false => k.val == 1 && !isState1 s0 q
  | _ => false

/-- A frozen (nonmoving, state 1-3) angry piston. -/
def faB : Block → Bool
  | .piston _ _ an k false => an && k.val != 0
  | _ => false

def Ctx.elig (cx : Ctx) (V : List Pos) : Finset Pos := cx.st.cellsWith (eligB cx.powered V)

def St.newExt (s s0 : St) : Finset Pos := s.cellsWith (newExtB s0)

def St.fAngry (s : St) : Finset Pos := s.cellsWith fun _ b => faB b

/-- The potential. -/
def pot (s0 : St) (cx : Ctx) (V : List Pos) : Nat :=
  (cx.st.newExt s0).card + (cx.elig V).card + cx.st.fAngry.card

/-! ### Block-level facts -/

theorem eligB_mono {pw pw' : ExtTreeSet Pos} {V V' : List Pos} {q : Pos} {b : Block}
    (hpw : pw'.contains q = true → pw.contains q = true) (hV : q ∈ V → q ∈ V')
    (h : eligB pw' V' q b = true) : eligB pw V q b = true := by
  cases b with
  | piston d st an k mv =>
    simp only [eligB, Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true',
      decide_eq_false_iff_not, beq_iff_eq] at h ⊢
    obtain ⟨hk, h⟩ := h
    refine ⟨hk, ?_⟩
    rcases h with h | ⟨⟨hm, hp⟩, hv⟩
    · exact Or.inl h
    · exact Or.inr ⟨⟨hm, hpw hp⟩, fun hq => hv (hV hq)⟩
  | _ => simp [eligB] at h

theorem eligB_startMoving {pw pw' : ExtTreeSet Pos} {V V' : List Pos} {q r : Pos} {b : Block}
    (h : eligB pw' V' q b.startMoving = true) : eligB pw V r b = true := by
  cases b with
  | piston d st an k mv =>
    simp only [Block.startMoving, Block.withMoving, eligB, Bool.and_eq_true, Bool.or_eq_true,
      Bool.not_eq_true', beq_iff_eq] at h ⊢
    obtain ⟨hk, h⟩ := h
    refine ⟨hk, ?_⟩
    rcases h with h | ⟨⟨hm, -⟩, -⟩
    · exact Or.inl h
    · simp at hm
  | plain k m => cases k <;> simp [Block.startMoving, Block.withMoving, eligB] at h
  | observer => simp [Block.startMoving, eligB] at h
  | rod => simp [Block.startMoving, Block.withMoving, eligB] at h

theorem newExtB_startMoving {s0 : St} {q : Pos} {b : Block} :
    newExtB s0 q b.startMoving = false := by
  cases b with
  | piston => simp [Block.startMoving, Block.withMoving, newExtB]
  | plain k m => cases k <;> simp [Block.startMoving, Block.withMoving, newExtB]
  | observer => simp [Block.startMoving, newExtB]
  | rod => simp [Block.startMoving, Block.withMoving, newExtB]

theorem faB_startMoving {b : Block} : faB b.startMoving = false := by
  cases b with
  | piston => simp [Block.startMoving, Block.withMoving, faB]
  | plain k m => cases k <;> simp [Block.startMoving, Block.withMoving, faB]
  | observer => simp [Block.startMoving, faB]
  | rod => simp [Block.startMoving, Block.withMoving, faB]

theorem Ctx.mem_elig {cx : Ctx} {V : List Pos} {q : Pos} :
    q ∈ cx.elig V ↔ ∃ b, cx.st.get q = some b ∧ eligB cx.powered V q b = true :=
  St.mem_cellsWith

theorem St.mem_newExt {s s0 : St} {q : Pos} :
    q ∈ s.newExt s0 ↔ ∃ b, s.get q = some b ∧ newExtB s0 q b = true :=
  St.mem_cellsWith

theorem St.mem_fAngry {s : St} {q : Pos} :
    q ∈ s.fAngry ↔ ∃ b, s.get q = some b ∧ faB b = true :=
  St.mem_cellsWith

/-! ### Per action -/

section
variable {c : Config} {cx cx' : Ctx} {pos : Pos} {d : Dir} {st an : Bool} {S : List Pos}
  {s0 : St} {V : List Pos}

/-- In an extension, a cell that keeps its block was not moved. -/
theorem ext_unchanged_not_mem (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S) {q : Pos} {b' : Block}
    (hq1 : q ≠ pos) (hq2 : q ≠ pos.add d) (h : cx.st.get q = some b')
    (hb' : cx'.st.get q = some b') : q ∉ S := by
  intro hqS
  obtain ⟨b0, hb0, hi0⟩ := discover_mem hS hqS
  rw [h] at hb0; cases hb0
  rw [hR.get, if_neg hq1, if_neg hq2] at hb'
  unfold moveWorld at hb'
  split at hb'
  · cases hsrc : cx.st.get (q.add d.opp) with
    | none => rw [hsrc] at hb'; cases hb'
    | some x =>
      rw [hsrc] at hb'
      simp only [Option.map_some, Option.some.injEq] at hb'
      have hm : b'.moving = true := by rw [← hb']; simp
      simp [immovable, hm] at hi0
  · simp [hqS] at hb'

theorem pot_ext (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hfire : (cx.powered.contains pos || an) = true)
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S)
    (hpw : ∀ q, cx'.powered.contains q = true → cx.powered.contains q = true)
    (hV : pos ∉ V) (hs0 : isState1 s0 pos = false) :
    pot s0 cx' (V ++ [pos]) ≤ pot s0 cx V := by
  classical
  have hM := discover_moveOK hS
  have hposI : immovable (some pos) pos (.piston d st an 0 false) = true := by simp [immovable]
  have hposS : pos ∉ S := mw_not_mem_of_immovable hM hb hposI
  have hVV : ∀ q, q ∈ V → q ∈ V ++ [pos] := fun q h => List.mem_append_left _ h
  set σ : Pos → Pos := fun r => if r ∈ S then r.add d else r with hσ
  have hposE : pos ∈ cx.elig V := Ctx.mem_elig.mpr ⟨_, hb, by
    simp only [eligB, Fin.val_zero, beq_self_eq_true, Bool.true_and, Bool.not_false,
      Bool.and_true, decide_eq_true_eq]
    simp only [hV, decide_false, Bool.not_false, Bool.and_true]
    cases h1 : cx.powered.contains pos <;> cases an <;> simp_all⟩
  have hNE : cx'.st.newExt s0 ⊆ insert pos (cx.st.newExt s0) := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_newExt.mp hq
    rcases ext_cases hW hb hS hR hb' with ⟨rfl, -⟩ | ⟨-, h⟩ | ⟨-, -, h⟩ | ⟨b, -, -, -, h⟩
    · exact Finset.mem_insert_self _ _
    · subst h; simp [newExtB] at hk
    · exact Finset.mem_insert_of_mem (St.mem_newExt.mpr ⟨b', h, hk⟩)
    · subst h; simp [newExtB_startMoving] at hk
  have hEl : cx'.elig (V ++ [pos]) ⊆ ((cx.elig V).erase pos).image σ := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := Ctx.mem_elig.mp hq
    rcases ext_cases hW hb hS hR hb' with ⟨rfl, h⟩ | ⟨-, h⟩ | ⟨hq1, hq2, h⟩ | ⟨b, hS', hb'', -, h⟩
    · subst h; simp [eligB] at hk
    · subst h; simp [eligB] at hk
    · have hqS := ext_unchanged_not_mem hb hS hR hq1 hq2 h hb'
      refine Finset.mem_image.mpr ⟨q, Finset.mem_erase.mpr ⟨hq1, Ctx.mem_elig.mpr
        ⟨b', h, eligB_mono (hpw q) (hVV q) hk⟩⟩, by simp [hσ, hqS]⟩
    · subst h
      have hr : q.add d.opp ≠ pos := by rintro e; rw [e] at hS'; exact hposS hS'
      refine Finset.mem_image.mpr ⟨q.add d.opp, Finset.mem_erase.mpr ⟨hr, Ctx.mem_elig.mpr
        ⟨b, hb'', eligB_startMoving hk⟩⟩, by simp [hσ, hS', Pos.add_opp_add]⟩
  have hFA : cx'.st.fAngry ⊆ cx.st.fAngry := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_fAngry.mp hq
    rcases ext_cases hW hb hS hR hb' with ⟨rfl, h⟩ | ⟨-, h⟩ | ⟨-, -, h⟩ | ⟨b, -, -, -, h⟩
    · subst h; simp [faB] at hk
    · subst h; simp [faB] at hk
    · exact St.mem_fAngry.mpr ⟨b', h, hk⟩
    · subst h; simp [faB_startMoving] at hk
  have c1 := (Finset.card_le_card hNE).trans (Finset.card_insert_le _ _)
  have c2 := (Finset.card_le_card hEl).trans Finset.card_image_le
  rw [Finset.card_erase_of_mem hposE] at c2
  have c3 := Finset.card_le_card hFA
  have c4 : 1 ≤ (cx.elig V).card := Finset.card_pos.mpr ⟨pos, hposE⟩
  unfold pot
  omega


theorem pot_retract (hW : Wf cx.st) (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hpw : ∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) :
    pot s0 cx' (V ++ [pos]) ≤ pot s0 cx V := by
  classical
  set S := pulled c cx.st pos d st with hS
  set W1 := cx.st.remove (pos.add d) with hW1
  have hM : MoveOK W1 S d.opp (some pos) := pulled_moveOK
  have hW1get : ∀ q, q ≠ pos.add d → W1.get q = cx.st.get q := fun q hq =>
    St.get_remove_ne (Ne.symm hq)
  have hfrontS : pos.add d ∉ S := by
    intro h; obtain ⟨b, hb', -⟩ := hM.1 _ h; simp [hW1] at hb'
  have hVV : ∀ q, q ∈ V → q ∈ V ++ [pos] := fun q h => List.mem_append_left _ h
  set σ : Pos → Pos := fun r => if r ∈ S then r.add d.opp else r with hσ
  have hcases : ∀ q b', cx'.st.get q = some b' → (q = pos ∧ b' = .piston d st an 3 false) ∨
      (q ≠ pos ∧ cx.st.get q = some b' ∧ q ∉ S) ∨
      (∃ b, q.add d.opp.opp ∈ S ∧ cx.st.get (q.add d.opp.opp) = some b ∧ b' = b.startMoving) := by
    intro q b' hb'
    rw [hget] at hb'
    split at hb'
    · rename_i e; cases hb'; exact Or.inl ⟨e, rfl⟩
    · rename_i hq
      rcases mw_cases hM hb' with ⟨h1, hqS, -⟩ | ⟨b, hS', hb'', -, h⟩
      · have hqf : q ≠ pos.add d := by rintro rfl; simp [hW1] at h1
        exact Or.inr (Or.inl ⟨hq, by rw [← hW1get q hqf]; exact h1, hqS⟩)
      · have hrf : q.add d.opp.opp ≠ pos.add d := by
          rintro e; rw [e] at hS'; exact hfrontS hS'
        exact Or.inr (Or.inr ⟨b, hS', by rw [← hW1get _ hrf]; exact hb'', h⟩)
  have hNE : cx'.st.newExt s0 ⊆ cx.st.newExt s0 := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_newExt.mp hq
    rcases hcases q b' hb' with ⟨-, h⟩ | ⟨-, h, -⟩ | ⟨b, -, -, h⟩
    · subst h; simp [newExtB] at hk
    · exact St.mem_newExt.mpr ⟨b', h, hk⟩
    · subst h; simp [newExtB_startMoving] at hk
  have hEl : cx'.elig (V ++ [pos]) ⊆ (cx.elig V).image σ := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := Ctx.mem_elig.mp hq
    rcases hcases q b' hb' with ⟨-, h⟩ | ⟨-, h, hqS⟩ | ⟨b, hS', hb'', h⟩
    · subst h; simp [eligB] at hk
    · exact Finset.mem_image.mpr ⟨q, Ctx.mem_elig.mpr ⟨b', h, eligB_mono (hpw q) (hVV q) hk⟩,
        by simp [hσ, hqS]⟩
    · subst h
      exact Finset.mem_image.mpr ⟨q.add d.opp.opp, Ctx.mem_elig.mpr
        ⟨b, hb'', eligB_startMoving hk⟩, by simp only [hσ]; rw [if_pos hS']; exact Pos.add_opp_add q d.opp⟩
  have hFA : cx'.st.fAngry ⊆ cx.st.fAngry := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_fAngry.mp hq
    rcases hcases q b' hb' with ⟨rfl, h⟩ | ⟨-, h, -⟩ | ⟨b, -, -, h⟩
    · subst h; exact St.mem_fAngry.mpr ⟨_, hb, by simpa [faB] using hk⟩
    · exact St.mem_fAngry.mpr ⟨b', h, hk⟩
    · subst h; simp [faB_startMoving] at hk
  have c1 := Finset.card_le_card hNE
  have c2 := (Finset.card_le_card hEl).trans Finset.card_image_le
  have c3 := Finset.card_le_card hFA
  unfold pot
  omega

theorem pot_finish {k next : Fin 4} (hW : Wf cx.st)
    (hb : cx.st.get pos = some (.piston d st an k false))
    (hk : k.val = 1 ∨ k.val = 3) (hnext : next.val = if k.val = 1 then 2 else 0)
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q)
    (hpw : cx'.powered = cx.powered)
    (hnp : ∀ q ∈ cx.st.list pos, cx.powered.contains q = false) :
    pot s0 cx' (V ++ [pos]) ≤ pot s0 cx V := by
  classical
  have hVV : ∀ q, q ∈ V → q ∈ V ++ [pos] := fun q h => List.mem_append_left _ h
  have hLm : ∀ q ∈ cx.st.list pos, ∃ b, cx.st.get q = some b ∧ b.moving = true := by
    intro q hq
    cases hl' : cx.st.lists[pos]? with
    | none => simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl'] at hq
    | some L' =>
      have : cx.st.list pos = L' := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl']
      exact hW.list_moving pos L' q hl' (this ▸ hq)
  have hfin : ∀ q ∈ cx.st.list pos, ∀ b', cx'.st.get q = some b' → q ≠ pos →
      ∃ b, cx.st.get q = some b ∧ b.moving = true ∧ b' = b.finished := by
    intro q hq b' hb' hne
    rw [hget, if_neg hne, if_pos hq] at hb'
    obtain ⟨b, hb, hm⟩ := hLm q hq
    rw [hb] at hb'; cases hb'
    exact ⟨b, hb, hm, rfl⟩
  have hNE : cx'.st.newExt s0 ⊆ cx.st.newExt s0 := by
    intro q hq
    obtain ⟨b', hb', hk'⟩ := St.mem_newExt.mp hq
    by_cases hqp : q = pos
    · subst hqp
      rw [hget, if_pos rfl] at hb'; cases hb'
      rcases hk with h1 | h1
      · have : next.val = 2 := by simp [hnext, h1]
        simp [newExtB, this] at hk'
      · have : next.val = 0 := by simp [hnext, h1]
        simp [newExtB, this] at hk'
    · by_cases hqL : q ∈ cx.st.list pos
      · obtain ⟨b, hb, hm, rfl⟩ := hfin q hqL b' hb' hqp
        cases b with
        | piston d' st' an' k' mv' =>
          have : mv' = true := by simpa [Block.moving] using hm
          subst this
          have := hW.moving_piston _ _ _ _ _ hb
          simp [Block.finished, Block.withMoving, newExtB, this] at hk'
        | plain kk m => cases kk <;> simp [Block.finished, Block.withMoving, newExtB] at hk'
        | observer => simp [Block.finished, newExtB] at hk'
        | rod => simp [Block.finished, Block.withMoving, newExtB] at hk'
      · rw [hget, if_neg hqp, if_neg hqL] at hb'
        exact St.mem_newExt.mpr ⟨b', hb', hk'⟩
  have hEl : ∀ q, q ≠ pos → q ∈ cx'.elig (V ++ [pos]) → q ∈ cx.elig V := by
    intro q hqp hq
    obtain ⟨b', hb', hk'⟩ := Ctx.mem_elig.mp hq
    rw [hpw] at hk'
    by_cases hqL : q ∈ cx.st.list pos
    · obtain ⟨b, hb, hm, rfl⟩ := hfin q hqL b' hb' hqp
      refine Ctx.mem_elig.mpr ⟨b, hb, ?_⟩
      have hq0 := hnp q hqL
      cases b with
      | piston d' st' an' k' mv' =>
        have : mv' = true := by simpa [Block.moving] using hm
        subst this
        simp only [Block.finished, Block.withMoving, eligB, hq0, Bool.and_false, Bool.false_and,
          Bool.or_false, Bool.not_true] at hk' ⊢
        exact hk'
      | plain kk m => cases kk <;> simp [Block.finished, Block.withMoving, eligB] at hk'
      | observer => simp [Block.finished, eligB] at hk'
      | rod => simp [Block.finished, Block.withMoving, eligB] at hk'
    · rw [hget, if_neg hqp, if_neg hqL] at hb'
      exact Ctx.mem_elig.mpr ⟨b', hb', eligB_mono (fun h => h) (hVV q) hk'⟩
  have hFA : ∀ q, q ≠ pos → q ∈ cx'.st.fAngry → q ∈ cx.st.fAngry := by
    intro q hqp hq
    obtain ⟨b', hb', hk'⟩ := St.mem_fAngry.mp hq
    by_cases hqL : q ∈ cx.st.list pos
    · obtain ⟨b, hb, hm, rfl⟩ := hfin q hqL b' hb' hqp
      cases b with
      | piston d' st' an' k' mv' =>
        have : mv' = true := by simpa [Block.moving] using hm
        subst this
        have := hW.moving_piston _ _ _ _ _ hb
        simp [Block.finished, Block.withMoving, faB, this] at hk'
      | plain kk m => cases kk <;> simp [Block.finished, Block.withMoving, faB] at hk'
      | observer => simp [Block.finished, faB] at hk'
      | rod => simp [Block.finished, Block.withMoving, faB] at hk'
    · rw [hget, if_neg hqp, if_neg hqL] at hb'
      exact St.mem_fAngry.mpr ⟨b', hb', hk'⟩
  have hp' : cx'.st.get pos = some (.piston d st an next false) := by rw [hget, if_pos rfl]
  have c1 := Finset.card_le_card hNE
  rcases hk with h1 | h3
  · have hn2 : next.val = 2 := by simp [hnext, h1]
    have hEl' : cx'.elig (V ++ [pos]) ⊆ cx.elig V := by
      intro q hq
      by_cases hqp : q = pos
      · subst hqp
        obtain ⟨b', hb', hk'⟩ := Ctx.mem_elig.mp hq
        rw [hp'] at hb'; cases hb'; simp [eligB, hn2] at hk'
      · exact hEl q hqp hq
    have hFA' : cx'.st.fAngry ⊆ cx.st.fAngry := by
      intro q hq
      by_cases hqp : q = pos
      · subst hqp
        obtain ⟨b', hb', hk'⟩ := St.mem_fAngry.mp hq
        rw [hp'] at hb'; cases hb'
        refine St.mem_fAngry.mpr ⟨_, hb, ?_⟩
        simp [faB, hn2] at hk'
        simp [faB, h1, hk']
      · exact hFA q hqp hq
    have := Finset.card_le_card hEl'
    have := Finset.card_le_card hFA'
    unfold pot; omega
  · have hn0 : next.val = 0 := by simp [hnext, h3]
    by_cases han : an = true
    · subst han
      have hposF : pos ∈ cx.st.fAngry := St.mem_fAngry.mpr ⟨_, hb, by simp [faB, h3]⟩
      have hEl' : cx'.elig (V ++ [pos]) ⊆ insert pos (cx.elig V) := by
        intro q hq
        by_cases hqp : q = pos
        · rw [hqp]; exact Finset.mem_insert_self _ _
        · exact Finset.mem_insert_of_mem (hEl q hqp hq)
      have hFA' : cx'.st.fAngry ⊆ cx.st.fAngry.erase pos := by
        intro q hq
        by_cases hqp : q = pos
        · subst hqp
          obtain ⟨b', hb', hk'⟩ := St.mem_fAngry.mp hq
          rw [hp'] at hb'; cases hb'; simp [faB, hn0] at hk'
        · exact Finset.mem_erase.mpr ⟨hqp, hFA q hqp hq⟩
      have c2 := (Finset.card_le_card hEl').trans (Finset.card_insert_le _ _)
      have c3 := Finset.card_le_card hFA'
      rw [Finset.card_erase_of_mem hposF] at c3
      have : 1 ≤ cx.st.fAngry.card := Finset.card_pos.mpr ⟨pos, hposF⟩
      unfold pot; omega
    · have han' : an = false := by simpa using han
      subst han'
      have hEl' : cx'.elig (V ++ [pos]) ⊆ cx.elig V := by
        intro q hq
        by_cases hqp : q = pos
        · subst hqp
          obtain ⟨b', hb', hk'⟩ := Ctx.mem_elig.mp hq
          rw [hp'] at hb'; cases hb'
          simp [eligB, hn0] at hk'
        · exact hEl q hqp hq
      have hFA' : cx'.st.fAngry ⊆ cx.st.fAngry := by
        intro q hq
        by_cases hqp : q = pos
        · subst hqp
          obtain ⟨b', hb', hk'⟩ := St.mem_fAngry.mp hq
          rw [hp'] at hb'; cases hb'; simp [faB] at hk'
        · exact hFA q hqp hq
      have := Finset.card_le_card hEl'
      have := Finset.card_le_card hFA'
      unfold pot; omega

theorem pot_fail (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hfire : (cx.powered.contains pos || an) = true) (hV : pos ∉ V) :
    pot s0 { cx with st := cx.st.set pos (.piston d st true 0 false) } (V ++ [pos]) ≤
      pot s0 cx V := by
  classical
  have hVV : ∀ q, q ∈ V → q ∈ V ++ [pos] := fun q h => List.mem_append_left _ h
  have hg : ∀ q, (cx.st.set pos (.piston d st true 0 false)).get q =
      if q = pos then some (.piston d st true 0 false) else cx.st.get q := by
    intro q; rw [St.get_set]
    by_cases h : q = pos
    · subst h; simp
    · rw [if_neg (Ne.symm h), if_neg h]
  have hNE : (cx.st.set pos (.piston d st true 0 false)).newExt s0 ⊆ cx.st.newExt s0 := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_newExt.mp hq
    rw [hg] at hb'
    split at hb'
    · cases hb'; simp [newExtB] at hk
    · exact St.mem_newExt.mpr ⟨b', hb', hk⟩
  have hEl : Ctx.elig { cx with st := cx.st.set pos (.piston d st true 0 false) } (V ++ [pos]) ⊆
      cx.elig V := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := Ctx.mem_elig.mp hq
    rw [hg] at hb'
    split at hb'
    · rename_i e; subst e
      refine Ctx.mem_elig.mpr ⟨_, hb, ?_⟩
      simp only [eligB, Fin.val_zero, beq_self_eq_true, Bool.true_and]
      simp only [hV, decide_false, Bool.not_false, Bool.and_true]
      cases h1 : cx.powered.contains q <;> cases an <;> simp_all
    · exact Ctx.mem_elig.mpr ⟨b', hb', eligB_mono (fun h => h) (hVV q) hk⟩
  have hFA : (cx.st.set pos (.piston d st true 0 false)).fAngry ⊆ cx.st.fAngry := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := St.mem_fAngry.mp hq
    rw [hg] at hb'
    split at hb'
    · cases hb'; simp [faB] at hk
    · exact St.mem_fAngry.mpr ⟨b', hb', hk⟩
  have := Finset.card_le_card hNE
  have := Finset.card_le_card hEl
  have := Finset.card_le_card hFA
  unfold pot; dsimp only; omega

theorem pot_idle : pot s0 cx (V ++ [pos]) ≤ pot s0 cx V := by
  have hEl : cx.elig (V ++ [pos]) ⊆ cx.elig V := by
    intro q hq
    obtain ⟨b', hb', hk⟩ := Ctx.mem_elig.mp hq
    exact Ctx.mem_elig.mpr ⟨b', hb', eligB_mono (fun h => h)
      (fun h => List.mem_append_left _ h) hk⟩
  have := Finset.card_le_card hEl
  unfold pot; omega

end


/-! ### One turn -/

/-- What one turn does that the rest accounting needs. -/
structure TurnMore (cx cx' : Ctx) (pos : Pos) : Prop where
  kc : (cx'.st.cls isPK).card = (cx.st.cls isPK).card
  psi : cx'.st.xsum isPK ≤ cx.st.xsum isPK + cx'.st.lcount isPK pos
  keep : ∀ q b, cx.st.get q = some b → b.moving = true → q ∉ cx.st.list pos →
    cx'.st.get q = some b
  st2 : ∀ d st an, cx.st.get pos = some (.piston d st an 2 false) →
    HasState cx'.st pos 2 ∨ HasState cx'.st pos 3
  st2from : HasState cx'.st pos 2 → HasState cx.st pos 1 ∨ HasState cx.st pos 2
  pot : ∀ (s0 : St) (V : List Pos), pos ∉ V →
    (isState1 s0 pos = true → isState1 cx.st pos = true) →
    (∀ q ∈ cx.st.list pos, cx.powered.contains q = false) →
    pot s0 cx' (V ++ [pos]) ≤ pot s0 cx V

theorem turnMore_refl {cx : Ctx} {pos : Pos} : TurnMore cx cx pos where
  kc := rfl
  psi := by omega
  keep _ _ h _ _ := h
  st2 d st an h := Or.inl ⟨d, st, an, h⟩
  st2from h := Or.inr h
  pot _ _ _ _ _ := pot_idle

theorem isState1_of_state0 {s : St} {q : Pos} {d : Dir} {st an : Bool}
    (h : s.get q = some (.piston d st an 0 false)) : isState1 s q = false := by
  simp [isState1, h]

theorem turn_more {c : Config} {cx : Ctx} {pos : Pos} (hW : Wf cx.st) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧ TurnMore cx cx' pos := by
  cases hg : cx.st.get pos with
  | none => exact ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnMore_refl⟩
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true => exact ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnMore_refl⟩
      | false =>
        have hk4 := k.isLt
        rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
          hk | hk | hk | hk
        · obtain rfl : k = 0 := Fin.ext hk
          by_cases hfire : (cx.powered.contains pos || an) = true
          · cases hS : discover c cx.st (pos.add d) d (some pos) false with
            | none =>
              refine ⟨_, extFail_spec hg hfire hS, ?_⟩
              have hcl := cls_fail (P := isPK) hg
              refine ⟨by rw [hcl], ?_, ?_, ?_, ?_, ?_⟩
              · unfold St.xsum; rw [hcl]; omega
              · intro q b hq hm _
                have hne : q ≠ pos := by rintro rfl; rw [hg] at hq; cases hq; simp [Block.moving] at hm
                show (cx.st.set pos _).get q = _
                rw [St.get_set_ne (Ne.symm hne)]; exact hq
              · intro d' st' an' h; rw [hg] at h; cases h
              · rintro ⟨d', st', an', h⟩
                exfalso
                change (cx.st.set pos _).get pos = _ at h
                rw [St.get_set] at h; simp at h
              · intro s0 V hV _ _; exact pot_fail hg hfire hV
            | some S =>
              obtain ⟨cx', h1, hR, hpw⟩ := ext_result hW hg hfire hS
              obtain ⟨hkc, hps⟩ := cls_ext (P := isPK) (by decide) (by decide) hW hg hS hR
              refine ⟨cx', h1, hkc, hps, ?_, ?_, ?_, ?_⟩
              · intro q b hq hm _
                have hne : q ≠ pos := by rintro rfl; rw [hg] at hq; cases hq; simp [Block.moving] at hm
                exact ext_keep hW hg hS hR hq (by simp [immovable, hm]) hne
              · intro d' st' an' h; rw [hg] at h; cases h
              · rintro ⟨d', st', an', h⟩; rw [hR.get] at h; simp at h
              · intro s0 V hV h1s _
                refine pot_ext hW hg hfire hS hR hpw hV ?_
                cases h : isState1 s0 pos
                · rfl
                · have := h1s h; rw [isState1_of_state0 hg] at this; cases this
          · refine ⟨cx, ?_, turnMore_refl⟩
            unfold pistonTurn; rw [hg]
            simp only [Fin.val_zero]
            rw [if_neg hfire]; rfl
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx', h1, h2, h3, h4, h5⟩ := finish_spec (c := c) (next := 2) hW hg
            (Or.inl rfl) rfl
          refine ⟨cx', h1, by rw [cls_finish hg h2], by unfold St.xsum; rw [cls_finish hg h2]; omega,
            ?_, ?_, ?_, ?_⟩
          · intro q b hq hm hqL
            have hne : q ≠ pos := by rintro rfl; rw [hg] at hq; cases hq; simp [Block.moving] at hm
            rw [h2, if_neg hne, if_neg hqL, hq]
          · intro d' st' an' h; rw [hg] at h; cases h
          · intro _; exact Or.inl ⟨d, st, an, hg⟩
          · intro s0 V _ _ hnp
            exact pot_finish hW hg (Or.inl rfl) rfl h2 h5 hnp
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · refine ⟨cx, ?_, turnMore_refl⟩
            unfold pistonTurn; rw [hg]
            simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true]; rfl
          · obtain ⟨cx', h1, h2, h3, h4, h5, h6⟩ := retract_spec (c := c) hW hg
              (Bool.eq_false_iff.mpr hpw)
            have hlp : ∀ L, cx'.st.lists[pos]? = some L →
                L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)) := by
              intro L hL'
              by_cases hS0 : pulled c cx.st pos d st = []
              · rw [h4 hS0] at hL'; cases hL'
              · obtain ⟨L', hL'', hperm⟩ := h5 hS0
                rw [hL'] at hL''; cases hL''
                exact hperm
            obtain ⟨hkc, hps⟩ := cls_retract (P := isPK) (by decide) (by decide) hW hg h2 hlp
              (fun h => (h5 h).imp fun _ h' => h'.1)
            refine ⟨cx', h1, hkc, hps, ?_, ?_, ?_, ?_⟩
            · intro q b hq hm _
              have hne : q ≠ pos := by rintro rfl; rw [hg] at hq; cases hq; simp [Block.moving] at hm
              have harm := hW.arm_front pos d st an 2 false hg (Or.inr rfl)
              have hnf : q ≠ pos.add d := by
                rintro rfl; rw [harm] at hq; cases hq; simp [Block.moving] at hm
              rw [h2, if_neg hne]
              exact mw_immovable pulled_moveOK (by rw [St.get_remove_ne (Ne.symm hnf), hq])
                (by simp [immovable, hm])
            · intro _ _ _ _; exact Or.inr ⟨d, st, an, by rw [h2]; simp⟩
            · rintro ⟨d', st', an', h⟩; rw [h2] at h; simp at h
            · intro s0 V _ _ _; exact pot_retract hW hg h2 h6
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx', h1, h2, h3, h4, h5⟩ := finish_spec (c := c) (next := 0) hW hg
            (Or.inr rfl) rfl
          refine ⟨cx', h1, by rw [cls_finish hg h2], by unfold St.xsum; rw [cls_finish hg h2]; omega,
            ?_, ?_, ?_, ?_⟩
          · intro q b hq hm hqL
            have hne : q ≠ pos := by rintro rfl; rw [hg] at hq; cases hq; simp [Block.moving] at hm
            rw [h2, if_neg hne, if_neg hqL, hq]
          · intro d' st' an' h; rw [hg] at h; cases h
          · rintro ⟨d', st', an', h⟩; rw [h2] at h; simp at h
          · intro s0 V _ _ hnp
            exact pot_finish hW hg (Or.inr rfl) rfl h2 h5 hnp
    | _ => exact ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnMore_refl⟩

end FF
