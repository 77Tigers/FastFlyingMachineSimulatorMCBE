/-
One piston turn on a well-formed state, summarised: it succeeds, keeps `Wf` and short,
duplicate-free lists, changes no other list and no other frozen piston (a nonmoving
piston in state 1, 2 or 3), and at its own cell only performs the state changes of the
piston cycle.
-/
import Formal.Lemmas.Count

namespace FF

open Std

/-- Every stored list has at most `pushLimit` cells and no duplicates. -/
def ListsOK (c : Config) (s : St) : Prop :=
  ∀ (p : Pos) (L : List Pos), s.lists[p]? = some L → L.length ≤ c.pushLimit ∧ L.Nodup

/-- A nonmoving piston in state 1, 2 or 3 (it cannot be moved). -/
def Frozen (s : St) (q : Pos) (d : Dir) (st an : Bool) (k : Fin 4) : Prop :=
  k.val ≠ 0 ∧ s.get q = some (.piston d st an k false)

structure TurnEffect (c : Config) (cx cx' : Ctx) (pos : Pos) : Prop where
  wf : Wf cx'.st
  lok : ListsOK c cx'.st
  lists_ne : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?
  powered : ∀ q, cx'.powered.contains q = true → cx.powered.contains q = true
  frozen_ne : ∀ q, q ≠ pos → ∀ d st an k, (Frozen cx'.st q d st an k ↔ Frozen cx.st q d st an k)
  /-- a piston in state 1 finishes to state 2 -/
  one_two : ∀ d st an, cx.st.get pos = some (.piston d st an 1 false) →
    cx'.st.get pos = some (.piston d st an 2 false)
  /-- a piston in state 3 after its turn was in state 2 before -/
  three_two : ∀ d st an, cx'.st.get pos = some (.piston d st an 3 false) →
    cx.st.get pos = some (.piston d st an 2 false)
  /-- the number of blocks other than arms is kept -/
  count : cx'.st.N = cx.st.N
  /-- the X sum rises by at most the number of blocks moved (the new list's length) -/
  phi : cx'.st.phi ≤ cx.st.phi + (cx'.st.list pos).length

section
variable {c : Config} {cx : Ctx} {pos : Pos}

theorem ListsOK.of_lists {s s' : St} {pos : Pos} (h : ListsOK c s)
    (hne : ∀ q, q ≠ pos → s'.lists[q]? = s.lists[q]?)
    (hpos : ∀ L, s'.lists[pos]? = some L → L.length ≤ c.pushLimit ∧ L.Nodup) : ListsOK c s' := by
  intro p L hL
  by_cases hp : p = pos
  · subst hp; exact hpos L hL
  · rw [hne p hp] at hL; exact h p L hL

theorem perm_map_ok {S : List Pos} {d : Dir} {L : List Pos} (hl : S.length ≤ c.pushLimit)
    (hn : S.Nodup) (hp : L.Perm (S.map (·.add d))) : L.length ≤ c.pushLimit ∧ L.Nodup :=
  ⟨by rw [hp.length_eq]; simpa using hl,
   hp.nodup_iff.mpr (List.Pairwise.map _ (fun _ _ hab heq => hab (Pos.add_inj.mp heq)) hn)⟩

/-- An idle turn changes nothing. -/
theorem turnEffect_refl (hW : Wf cx.st) (hL : ListsOK c cx.st)
    (h13 : ∀ d st an (k : Fin 4), cx.st.get pos = some (.piston d st an k false) →
      k.val ≠ 1 ∧ k.val ≠ 3) :
    TurnEffect c cx cx pos where
  wf := hW
  lok := hL
  lists_ne _ _ := rfl
  powered _ h := h
  frozen_ne _ _ _ _ _ _ := Iff.rfl
  one_two d st an h := absurd rfl (h13 d st an 1 h).1
  three_two d st an h := absurd rfl (h13 d st an 3 h).2
  count := rfl
  phi := by omega

/-- Frozen pistons are immovable for every owner. -/
theorem Frozen.immov {s : St} {q : Pos} {d : Dir} {st an : Bool} {k : Fin 4}
    (h : Frozen s q d st an k) (o : Option Pos) :
    immovable o q (.piston d st an k false) = true := by
  simp [immovable, Block.isPiston, Block.kind, Block.state, h.1]

theorem startMoving_not_frozen {b : Block} {o : Option Pos} {p : Pos} {d : Dir} {st an : Bool}
    {k : Fin 4} (hi : immovable o p b = false) (_hk : k.val ≠ 0) :
    b.startMoving ≠ .piston d st an k false := by
  intro h
  have := (Block.startMoving_piston hi h).2.1
  cases this

/-! ### Extension -/

theorem ext_effect {cx cx' : Ctx} {d : Dir} {st an : Bool} {S : List Pos}
    (hW : Wf cx.st) (hL : ListsOK c cx.st) (hb : cx.st.get pos = some (.piston d st an 0 false))
    (hS : discover c cx.st (pos.add d) d (some pos) false = some S)
    (hR : ExtResult cx cx' pos d st S)
    (hpw : ∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) :
    TurnEffect c cx cx' pos where
  wf := ext_wf hW hb hS hR
  lok := ListsOK.of_lists hL hR.lists_ne fun L hL' =>
    perm_map_ok (discover_length_le hS) (discover_nodup hS) (hR.lists_pos L hL')
  lists_ne := hR.lists_ne
  powered := hpw
  frozen_ne q hq d' st' an' k := by
    constructor
    · rintro ⟨hk, h⟩
      refine ⟨hk, ?_⟩
      rcases ext_cases hW hb hS hR h with ⟨h1, -⟩ | ⟨-, h1⟩ | ⟨-, -, h1⟩ | ⟨b, -, -, hi, h1⟩
      · exact absurd h1 hq
      · cases h1
      · exact h1
      · exact absurd h1.symm (startMoving_not_frozen hi hk)
    · rintro hf
      exact ⟨hf.1, ext_keep hW hb hS hR hf.2 (hf.immov _) hq⟩
  one_two d' st' an' h := by rw [hb] at h; cases h
  three_two d' st' an' h := by rw [hR.get] at h; simp at h
  count := (count_ext hW hb hS hR).1
  phi := (count_ext hW hb hS hR).2

/-! ### Failed extension -/

theorem fail_effect {d : Dir} {st an : Bool} (hW : Wf cx.st) (hL : ListsOK c cx.st)
    (hb : cx.st.get pos = some (.piston d st an 0 false)) :
    TurnEffect c cx { cx with st := cx.st.set pos (.piston d st true 0 false) } pos where
  wf := hW.set_angry hb
  lok := ListsOK.of_lists hL (fun q _ => by rw [St.lists_set]; simp [Block.isPiston, Block.kind])
    (fun L h => hL pos L (by rw [St.lists_set] at h; simpa [Block.isPiston, Block.kind] using h))
  lists_ne q _ := by rw [St.lists_set]; simp [Block.isPiston, Block.kind]
  powered _ h := h
  frozen_ne q hq _ _ _ _ := by simp only [Frozen]; rw [St.get_set_ne (Ne.symm hq)]
  one_two d' st' an' h := by rw [hb] at h; cases h
  three_two d' st' an' h := by simp at h
  count := (count_fail hb).1
  phi := (count_fail hb).2

/-! ### Finishing -/

theorem finish_effect {cx' : Ctx} {d : Dir} {st an : Bool} {k next : Fin 4}
    (hW : Wf cx.st) (hL : ListsOK c cx.st) (hb : cx.st.get pos = some (.piston d st an k false))
    (hk : k.val = 1 ∨ k.val = 3) (hnext : next.val = if k.val = 1 then 2 else 0)
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an next false)
      else if q ∈ cx.st.list pos then (cx.st.get q).map Block.finished else cx.st.get q)
    (hl : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?)
    (hlp : cx'.st.lists[pos]? = none) (hpw : cx'.powered = cx.powered) :
    TurnEffect c cx cx' pos := by
  -- listed cells hold moving blocks
  have hLm : ∀ q ∈ cx.st.list pos, ∃ b, cx.st.get q = some b ∧ b.moving = true := by
    intro q hq
    cases hl' : cx.st.lists[pos]? with
    | none => simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl'] at hq
    | some L' =>
      have : cx.st.list pos = L' := by simp [St.list, ExtTreeMap.getD_eq_getD_getElem?, hl']
      exact hW.list_moving pos L' q hl' (this ▸ hq)
  refine ⟨finish_wf hW hb hk hnext hget hl hlp, ?_, hl, fun q h => hpw ▸ h, ?_, ?_, ?_,
    (count_finish hb hget).1, (count_finish hb hget).2⟩
  · exact ListsOK.of_lists hL hl (fun L h => by rw [hlp] at h; cases h)
  · intro q hq d' st' an' k'
    constructor
    · rintro ⟨hk', h⟩
      refine ⟨hk', ?_⟩
      rw [hget, if_neg hq] at h
      split at h
      · rename_i hqL
        obtain ⟨b, hb', hm⟩ := hLm q hqL
        rw [hb'] at h
        simp only [Option.map_some, Option.some.injEq] at h
        obtain ⟨an₁, mv₁, rfl⟩ := Block.finished_piston h
        have hmv : mv₁ = true := by simpa [Block.moving] using hm
        subst hmv
        exact absurd (hW.moving_piston _ _ _ _ _ hb') hk'
      · exact h
    · rintro ⟨hk', h⟩
      refine ⟨hk', ?_⟩
      rw [hget, if_neg hq, if_neg, h]
      intro hqL
      obtain ⟨b, hb', hm⟩ := hLm q hqL
      rw [h] at hb'; cases hb'; simp [Block.moving] at hm
  · intro d' st' an' h
    rw [hb] at h; cases h
    rw [hget, if_pos rfl]
    have : next = 2 := Fin.ext (by simp [hnext])
    rw [this]
  · intro d' st' an' h
    rw [hget, if_pos rfl] at h
    simp only [Option.some.injEq, Block.piston.injEq] at h
    obtain ⟨rfl, rfl, rfl, hn, -⟩ := h
    rw [hn] at hnext
    rcases hk with h1 | h1 <;> simp only [h1] at hnext <;> exact absurd hnext (by decide)

/-! ### Retraction -/

theorem retract_effect {cx' : Ctx} {d : Dir} {st an : Bool}
    (hW : Wf cx.st) (hL : ListsOK c cx.st) (hb : cx.st.get pos = some (.piston d st an 2 false))
    (hget : ∀ q, cx'.st.get q =
      if q = pos then some (.piston d st an 3 false)
      else moveWorld (cx.st.remove (pos.add d)) (pulled c cx.st pos d st) d.opp q)
    (hl : ∀ q, q ≠ pos → cx'.st.lists[q]? = cx.st.lists[q]?)
    (hlp : ∀ L, cx'.st.lists[pos]? = some L →
      L.Perm ((pulled c cx.st pos d st).map (·.add d.opp)))
    (hls : pulled c cx.st pos d st ≠ [] → ∃ L, cx'.st.lists[pos]? = some L)
    (hpw : ∀ q, cx'.powered.contains q = true → cx.powered.contains q = true) :
    TurnEffect c cx cx' pos := by
  have hM := pulled_moveOK (c := c) (cx := cx) (pos := pos) (d := d) (st := st)
  have harm := hW.arm_front pos d st an 2 false hb (Or.inr rfl)
  have hlen := pulled_length (c := c) (cx := cx) (pos := pos) (d := d) (st := st)
  refine ⟨retract_wf hW hb hget hl hlp, ?_, hl, hpw, ?_, ?_, ?_,
    (count_retract hW hb hget hlp hls).1, (count_retract hW hb hget hlp hls).2⟩
  · exact ListsOK.of_lists hL hl (fun L h => perm_map_ok hlen.1 hlen.2 (hlp L h))
  · intro q hq d' st' an' k
    have hqf : ∀ b, cx.st.get q = some b → b.isPiston = true → q ≠ pos.add d := by
      intro b hqb hp e; rw [e, harm] at hqb; cases hqb; simp [Block.isPiston, Block.kind] at hp
    constructor
    · rintro ⟨hk, h⟩
      refine ⟨hk, ?_⟩
      rw [hget, if_neg hq] at h
      rcases mw_cases hM h with ⟨h1, -, -⟩ | ⟨b, -, -, hi, h1⟩
      · have hf : q ≠ pos.add d := by rintro rfl; simp at h1
        rwa [St.get_remove_ne (Ne.symm hf)] at h1
      · exact absurd h1.symm (startMoving_not_frozen hi hk)
    · rintro hf
      refine ⟨hf.1, ?_⟩
      rw [hget, if_neg hq]
      have hne := hqf _ hf.2 rfl
      exact mw_immovable hM (by rw [St.get_remove_ne (Ne.symm hne), hf.2]) (hf.immov _)
  · intro d' st' an' h; rw [hb] at h; cases h
  · intro d' st' an' h
    rw [hget, if_pos rfl] at h
    simp only [Option.some.injEq, Block.piston.injEq] at h
    obtain ⟨rfl, rfl, rfl, -, -⟩ := h
    exact hb

/-! ### Any turn -/

theorem turn_effect (hW : Wf cx.st) (hL : ListsOK c cx.st) :
    ∃ cx', pistonTurn c cx pos = .ok cx' ∧ TurnEffect c cx cx' pos := by
  cases hg : cx.st.get pos with
  | none =>
    refine ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnEffect_refl hW hL ?_⟩
    intro d st an k h; rw [hg] at h; cases h
  | some b =>
    cases b with
    | piston d st an k mv =>
      cases mv with
      | true =>
        refine ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnEffect_refl hW hL ?_⟩
        intro d' st' an' k' h; rw [hg] at h; cases h
      | false =>
        have hk4 := k.isLt
        rcases (show k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 by omega) with
          hk | hk | hk | hk
        · obtain rfl : k = 0 := Fin.ext hk
          by_cases hfire : (cx.powered.contains pos || an) = true
          · cases hS : discover c cx.st (pos.add d) d (some pos) false with
            | none => exact ⟨_, extFail_spec hg hfire hS, fail_effect hW hL hg⟩
            | some S =>
              obtain ⟨cx', h1, hR, hpw⟩ := ext_result hW hg hfire hS
              exact ⟨cx', h1, ext_effect hW hL hg hS hR hpw⟩
          · refine ⟨cx, ?_, turnEffect_refl hW hL ?_⟩
            · unfold pistonTurn; rw [hg]
              simp only [Fin.val_zero]
              rw [if_neg hfire]; rfl
            · intro d' st' an' k' h; rw [hg] at h; cases h; simp
        · obtain rfl : k = 1 := Fin.ext hk
          obtain ⟨cx', h1, h2, h3, h4, h5⟩ := finish_spec (c := c) (next := 2) hW hg
            (Or.inl rfl) rfl
          exact ⟨cx', h1, finish_effect hW hL hg (Or.inl rfl) rfl h2 h3 h4 h5⟩
        · obtain rfl : k = 2 := Fin.ext hk
          by_cases hpw : cx.powered.contains pos = true
          · refine ⟨cx, ?_, turnEffect_refl hW hL ?_⟩
            · unfold pistonTurn; rw [hg]
              simp only [show (2 : Fin 4).val = 2 from rfl, hpw, ite_true]; rfl
            · intro d' st' an' k' h; rw [hg] at h; cases h; simp
          · obtain ⟨cx', h1, h2, h3, h4, h5, h6⟩ := retract_spec (c := c) hW hg
              (Bool.eq_false_iff.mpr hpw)
            refine ⟨cx', h1, retract_effect hW hL hg h2 h3 ?_
              (fun h => (h5 h).imp fun _ h' => h'.1) h6⟩
            intro L hL'
            by_cases hS0 : pulled c cx.st pos d st = []
            · rw [h4 hS0] at hL'; cases hL'
            · obtain ⟨L', hL'', hperm⟩ := h5 hS0
              rw [hL'] at hL''; cases hL''
              exact hperm
        · obtain rfl : k = 3 := Fin.ext hk
          obtain ⟨cx', h1, h2, h3, h4, h5⟩ := finish_spec (c := c) (next := 0) hW hg
            (Or.inr rfl) rfl
          exact ⟨cx', h1, finish_effect hW hL hg (Or.inr rfl) rfl h2 h3 h4 h5⟩
    | _ =>
      refine ⟨cx, by unfold pistonTurn; rw [hg]; rfl, turnEffect_refl hW hL ?_⟩
      all_goals (intro d st an k h; rw [hg] at h; cases h)

end

end FF
