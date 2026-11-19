/-
Rows along X. A *relabelling* `σ` from `s` to `s'` maps the blocks of `s` (arms excluded)
one-to-one onto those of `s'`, keeping each block's kind, a piston's facing and stickiness, its
row (Y and Z), and the order of the blocks within each row. Then every block keeps its rank in
its row. `Rel s s'` adds: a block that moved forward had a possible forward mover in `s` (the
block of rank one less in its row is a `+X` piston, or the block of rank one more is a sticky
`-X` piston). `Rel` is reflexive and transitive.
-/
import Formal.PL1.Chain
import Formal.SpeedRest

namespace FF

open Std

def Block.sticky : Block → Bool
  | .piston _ st _ _ _ => st
  | _ => false

/-- What a block keeps when it moves or changes state: its kind, and a piston's facing and
stickiness. -/
def Block.sig (b : Block) : Kind × Dir × Bool :=
  (b.kind, if b.kind = .piston then b.dir else .px, b.sticky)

theorem Block.sig_withMoving (b : Block) (m : Bool) : (b.withMoving m).sig = b.sig := by
  cases b with
  | plain k m' => cases k <;> rfl
  | _ => rfl

theorem Block.sig_startMoving (b : Block) : b.startMoving.sig = b.sig := by
  cases b with
  | plain k m => cases k <;> rfl
  | _ => rfl

theorem Block.sig_finished (b : Block) : b.finished.sig = b.sig := by
  cases b with
  | plain k m => cases k <;> rfl
  | _ => rfl

theorem BitsOnly.sig {f : Block → Block} (hf : BitsOnly f) (b : Block) : (f b).sig = b.sig := by
  cases b with
  | piston d st an k mv =>
    obtain ⟨an', h⟩ := hf.piston d st an k mv
    rw [h]; rfl
  | plain k m => rw [hf.plain]
  | observer d p m =>
    have hk := hf.kind (.observer d p m)
    cases h : f (.observer d p m) with
    | observer d' p' m' => rfl
    | plain k' m' => rw [h] at hk; cases k' <;> simp [Block.kind] at hk
    | _ => rw [h] at hk; simp [Block.kind] at hk
  | rod d m =>
    have hk := hf.kind (.rod d m)
    cases h : f (.rod d m) with
    | rod d' m' => rfl
    | plain k' m' => rw [h] at hk; cases k' <;> simp [Block.kind] at hk
    | _ => rw [h] at hk; simp [Block.kind] at hk

/-- `P`: a `+X` piston; `Q`: a sticky `-X` piston; `O`: anything else. -/
def tyOfSig : Kind × Dir × Bool → Ty
  | (.piston, .px, _) => .P
  | (.piston, .nx, true) => .Q
  | _ => .O

def St.tyAt (s : St) (q : Pos) : Ty :=
  match (s.get q).map Block.sig with
  | some g => tyOfSig g
  | none => .O

/-- The rank of `q` in its row: the number of blocks (not arms) of the row behind it. -/
def St.rk (s : St) (q : Pos) : Nat :=
  (s.body.filter (fun p => p.y = q.y ∧ p.z = q.z ∧ p.x < q.x)).card

theorem Pos.eq_of_xyz {a b : Pos} (hx : a.x = b.x) (hy : a.y = b.y) (hz : a.z = b.z) : a = b := by
  cases a; cases b; simp_all

theorem body_iff_of_sig {s s' : St} {q : Pos}
    (h : (s'.get q).map Block.sig = (s.get q).map Block.sig) : q ∈ s'.body ↔ q ∈ s.body := by
  rw [St.mem_body, St.mem_body]
  cases h1 : s'.get q with
  | none =>
    rw [h1] at h
    cases h2 : s.get q with
    | none => simp
    | some b => rw [h2] at h; cases h
  | some b' =>
    rw [h1] at h
    cases h2 : s.get q with
    | none => rw [h2] at h; cases h
    | some b =>
      rw [h2] at h
      simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at h
      simp [isNonArm, h.1]

structure Relabel (s s' : St) (σ : Pos → Pos) : Prop where
  body : ∀ q, q ∈ s'.body ↔ ∃ r ∈ s.body, σ r = q
  inj : ∀ a ∈ s.body, ∀ b ∈ s.body, σ a = σ b → a = b
  sig : ∀ r ∈ s.body, (s'.get (σ r)).map Block.sig = (s.get r).map Block.sig
  lane : ∀ r ∈ s.body, (σ r).y = r.y ∧ (σ r).z = r.z
  order : ∀ a ∈ s.body, ∀ b ∈ s.body, a.y = b.y → a.z = b.z → (a.x < b.x ↔ (σ a).x < (σ b).x)

theorem Relabel.refl (s : St) : Relabel s s id where
  body q := ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩
  inj _ _ _ _ h := h
  sig _ _ := rfl
  lane _ _ := ⟨rfl, rfl⟩
  order _ _ _ _ _ _ := Iff.rfl

theorem Relabel.mem {s s' : St} {σ : Pos → Pos} (h : Relabel s s' σ) {r : Pos} (hr : r ∈ s.body) :
    σ r ∈ s'.body := (h.body _).mpr ⟨r, hr, rfl⟩

theorem Relabel.trans {s1 s2 s3 : St} {σ τ : Pos → Pos} (h1 : Relabel s1 s2 σ)
    (h2 : Relabel s2 s3 τ) : Relabel s1 s3 (τ ∘ σ) where
  body q := by
    rw [h2.body]
    constructor
    · rintro ⟨r', hr', rfl⟩
      obtain ⟨r, hr, rfl⟩ := (h1.body r').mp hr'
      exact ⟨r, hr, rfl⟩
    · rintro ⟨r, hr, rfl⟩
      exact ⟨σ r, h1.mem hr, rfl⟩
  inj a ha b hb h := h1.inj a ha b hb (h2.inj _ (h1.mem ha) _ (h1.mem hb) h)
  sig r hr := (h2.sig _ (h1.mem hr)).trans (h1.sig r hr)
  lane r hr := by
    obtain ⟨e1, e2⟩ := h1.lane r hr
    obtain ⟨e3, e4⟩ := h2.lane _ (h1.mem hr)
    exact ⟨e3.trans e1, e4.trans e2⟩
  order a ha b hb hy hz := by
    obtain ⟨ay, az⟩ := h1.lane a ha
    obtain ⟨by', bz⟩ := h1.lane b hb
    exact (h1.order a ha b hb hy hz).trans
      (h2.order _ (h1.mem ha) _ (h1.mem hb) (by rw [ay, by']; exact hy) (by rw [az, bz]; exact hz))

theorem Relabel.tyAt {s s' : St} {σ : Pos → Pos} (h : Relabel s s' σ) {r : Pos} (hr : r ∈ s.body) :
    s'.tyAt (σ r) = s.tyAt r := by
  unfold St.tyAt; rw [h.sig r hr]

theorem Relabel.rk {s s' : St} {σ : Pos → Pos} (h : Relabel s s' σ) {r : Pos} (hr : r ∈ s.body) :
    s'.rk (σ r) = s.rk r := by
  classical
  have himg : s'.body = s.body.image σ := by
    ext q; rw [h.body, Finset.mem_image]
  unfold St.rk
  rw [himg, Finset.filter_image, Finset.card_image_of_injOn]
  · congr 1
    apply Finset.filter_congr
    intro p hp
    obtain ⟨py, pz⟩ := h.lane p hp
    obtain ⟨ry, rz⟩ := h.lane r hr
    simp only [Function.comp_apply, py, pz, ry, rz]
    constructor
    · rintro ⟨e1, e2, e3⟩; exact ⟨e1, e2, (h.order p hp r hr e1 e2).mpr e3⟩
    · rintro ⟨e1, e2, e3⟩; exact ⟨e1, e2, (h.order p hp r hr e1 e2).mp e3⟩
  · intro a ha b hb e
    exact h.inj a (Finset.mem_filter.mp ha).1 b (Finset.mem_filter.mp hb).1 e

/-! ### Movers -/

/-- `r` has a possible forward mover in `s`. -/
def HasMover (s : St) (r : Pos) : Prop :=
  ∃ p ∈ s.body, p.y = r.y ∧ p.z = r.z ∧
    ((s.rk p + 1 = s.rk r ∧ s.tyAt p = .P) ∨ (s.rk p = s.rk r + 1 ∧ s.tyAt p = .Q))

theorem Relabel.hasMover {s s' : St} {σ : Pos → Pos} (h : Relabel s s' σ) {r : Pos}
    (hr : r ∈ s.body) (hm : HasMover s' (σ r)) : HasMover s r := by
  obtain ⟨p', hp', hy, hz, hk⟩ := hm
  obtain ⟨p, hp, rfl⟩ := (h.body p').mp hp'
  obtain ⟨py, pz⟩ := h.lane p hp
  obtain ⟨ry, rz⟩ := h.lane r hr
  refine ⟨p, hp, by rw [← py, hy, ry], by rw [← pz, hz, rz], ?_⟩
  rw [h.rk hp, h.rk hr, h.tyAt hp] at hk
  exact hk

/-- A relabelling in which every block that moved forward had a possible forward mover. -/
def Rel (s s' : St) : Prop :=
  ∃ σ, Relabel s s' σ ∧ ∀ r ∈ s.body, r.x < (σ r).x → HasMover s r

theorem Rel.refl (s : St) : Rel s s := ⟨id, Relabel.refl s, fun r _ h => absurd h (lt_irrefl _)⟩

theorem Rel.trans {s1 s2 s3 : St} (h1 : Rel s1 s2) (h2 : Rel s2 s3) : Rel s1 s3 := by
  obtain ⟨σ, hσ, hm1⟩ := h1
  obtain ⟨τ, hτ, hm2⟩ := h2
  refine ⟨τ ∘ σ, hσ.trans hτ, fun r hr hlt => ?_⟩
  by_cases h : r.x < (σ r).x
  · exact hm1 r hr h
  · exact hσ.hasMover hr (hm2 _ (hσ.mem hr) (by simp only [Function.comp_apply] at hlt; omega))

/-! ### Building relabellings -/

theorem relabel_id {s s' : St} (hb : ∀ q, q ∈ s'.body ↔ q ∈ s.body)
    (hs : ∀ q ∈ s.body, (s'.get q).map Block.sig = (s.get q).map Block.sig) : Rel s s' :=
  ⟨id, { body := fun q => by rw [hb]; exact ⟨fun h => ⟨q, h, rfl⟩, fun ⟨r, hr, e⟩ => e ▸ hr⟩
         inj := fun _ _ _ _ h => h
         sig := hs
         lane := fun _ _ => ⟨rfl, rfl⟩
         order := fun _ _ _ _ _ _ => Iff.rfl },
    fun r _ h => absurd h (lt_irrefl _)⟩

theorem relabel_sig {s s' : St} (hs : ∀ q, (s'.get q).map Block.sig = (s.get q).map Block.sig) :
    Rel s s' :=
  relabel_id (fun q => body_iff_of_sig (hs q)) (fun q _ => hs q)

/-- One block moves one step along X into a cell without a block. -/
theorem relabel_move {s s' : St} {r r' : Pos} (hr : r ∈ s.body) (hr' : r' ∉ s.body)
    (hy : r'.y = r.y) (hz : r'.z = r.z) (hx : r'.x = r.x + 1 ∨ r'.x = r.x - 1)
    (hget' : (s'.get r').map Block.sig = (s.get r).map Block.sig)
    (hrn : r ∉ s'.body)
    (hothers : ∀ q, q ≠ r → q ≠ r' → (s'.get q).map Block.sig = (s.get q).map Block.sig)
    (hmover : r.x < r'.x → HasMover s r) :
    Rel s s' := by
  classical
  have hne : r ≠ r' := by rintro rfl; exact hr' hr
  have hr's : r' ∈ s'.body := by
    rw [St.mem_body] at hr ⊢
    obtain ⟨b, hb, hk⟩ := hr
    rw [hb] at hget'
    cases h : s'.get r' with
    | none => rw [h] at hget'; cases hget'
    | some b' =>
      rw [h] at hget'
      simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hget'
      exact ⟨b', rfl, by simp [isNonArm] at hk ⊢; rw [hget'.1]; exact hk⟩
  set σ : Pos → Pos := fun q => if q = r then r' else q with hσ
  refine ⟨σ, ⟨?_, ?_, ?_, ?_, ?_⟩, ?_⟩
  · intro q
    by_cases h1 : q = r'
    · subst h1; exact ⟨fun _ => ⟨r, hr, by simp [hσ]⟩, fun _ => hr's⟩
    · by_cases h2 : q = r
      · subst h2
        refine ⟨fun h => absurd h hrn, ?_⟩
        rintro ⟨p, hp, e⟩
        simp only [hσ] at e
        split at e
        · exact absurd e.symm hne
        · rename_i hpr; exact absurd e hpr
      · rw [body_iff_of_sig (hothers q h2 h1)]
        constructor
        · intro h; exact ⟨q, h, by simp [hσ, h2]⟩
        · rintro ⟨p, hp, e⟩
          simp only [hσ] at e
          split at e
          · exact absurd e.symm h1
          · exact e ▸ hp
  · intro a ha b hb e
    simp only [hσ] at e
    split at e <;> split at e
    · rename_i h1 h2; rw [h1, h2]
    · rename_i h1 h2; subst e; exact absurd hb hr'
    · rename_i h1 h2; subst e; exact absurd ha hr'
    · exact e
  · intro p hp
    simp only [hσ]
    split
    · rename_i h; subst h; exact hget'
    · rename_i h
      exact hothers p h (by rintro rfl; exact hr' hp)
  · intro p hp
    simp only [hσ]
    split
    · rename_i h; subst h; exact ⟨hy, hz⟩
    · exact ⟨rfl, rfl⟩
  · intro a ha b hb e1 e2
    simp only [hσ]
    have hxa : ∀ q ∈ s.body, q ≠ r → q.y = r.y → q.z = r.z → q.x ≠ r.x ∧ q.x ≠ r'.x := by
      intro q hq hqr hqy hqz
      refine ⟨fun h => hqr (Pos.eq_of_xyz h hqy hqz), fun h => ?_⟩
      exact hr' (Pos.eq_of_xyz (h.symm) (hy.trans hqy.symm) (hz.trans hqz.symm) ▸ hq)
    split <;> split
    · rename_i h1 h2; subst h1; subst h2; simp
    · rename_i h1 h2; subst h1
      have := hxa b hb h2 e1.symm e2.symm
      omega
    · rename_i h1 h2; subst h2
      have := hxa a ha h1 e1 e2
      omega
    · exact Iff.rfl
  · intro p hp hlt
    simp only [hσ] at hlt
    split at hlt
    · rename_i h; subst h; exact hmover hlt
    · exact absurd hlt (lt_irrefl _)

/-! ### Ranks of neighbours -/

theorem rk_succ {s : St} {p r : Pos} (hp : p ∈ s.body) (hy : p.y = r.y) (hz : p.z = r.z)
    (hx : p.x + 1 = r.x) : s.rk r = s.rk p + 1 := by
  classical
  unfold St.rk
  rw [← Finset.card_insert_of_notMem (s := s.body.filter _) (a := p)
    (by simp)]
  congr 1
  ext q
  simp only [Finset.mem_filter, Finset.mem_insert]
  constructor
  · rintro ⟨hq, e1, e2, e3⟩
    by_cases h : q.x = p.x
    · left; exact Pos.eq_of_xyz h (e1.trans hy.symm) (e2.trans hz.symm)
    · right; exact ⟨hq, e1.trans hy.symm, e2.trans hz.symm, by omega⟩
  · rintro (rfl | ⟨hq, e1, e2, e3⟩)
    · exact ⟨hp, hy, hz, by omega⟩
    · exact ⟨hq, e1.trans hy, e2.trans hz, by omega⟩

theorem rk_succ2 {s : St} {p r : Pos} (hr : r ∈ s.body) (hy : p.y = r.y) (hz : p.z = r.z)
    (hx : p.x = r.x + 2) (hmid : (⟨r.x + 1, r.y, r.z⟩ : Pos) ∉ s.body) :
    s.rk p = s.rk r + 1 := by
  classical
  unfold St.rk
  rw [← Finset.card_insert_of_notMem (s := s.body.filter _) (a := r)
    (by simp)]
  congr 1
  ext q
  simp only [Finset.mem_filter, Finset.mem_insert]
  constructor
  · rintro ⟨hq, e1, e2, e3⟩
    by_cases h : q.x = r.x
    · left; exact Pos.eq_of_xyz h (e1.trans hy) (e2.trans hz)
    · right
      refine ⟨hq, e1.trans hy, e2.trans hz, ?_⟩
      by_contra h'
      have : q.x = r.x + 1 := by omega
      apply hmid
      have e : q = ⟨r.x + 1, r.y, r.z⟩ := Pos.eq_of_xyz this (e1.trans hy) (e2.trans hz)
      exact e ▸ hq
  · rintro (rfl | ⟨hq, e1, e2, e3⟩)
    · exact ⟨hr, hy.symm, hz.symm, by omega⟩
    · exact ⟨hq, e1.trans hy.symm, e2.trans hz.symm, by omega⟩

/-- All pistons face `+X` or `-X`. -/
def XOnly (s : St) : Prop :=
  ∀ q b, s.get q = some b → b.kind = .piston → b.dir = .px ∨ b.dir = .nx

theorem Rel.xOnly {s s' : St} (h : Rel s s') (hx : XOnly s) : XOnly s' := by
  obtain ⟨σ, hσ, -⟩ := h
  intro q b hq hk
  have hqb : q ∈ s'.body := St.mem_body.mpr ⟨b, hq, by simp [isNonArm, hk]⟩
  obtain ⟨r, hr, rfl⟩ := (hσ.body q).mp hqb
  have hs := hσ.sig r hr
  rw [hq] at hs
  cases hb : s.get r with
  | none => rw [hb] at hs; cases hs
  | some b0 =>
    rw [hb] at hs
    simp only [Option.map_some, Option.some.injEq, Block.sig, Prod.mk.injEq] at hs
    obtain ⟨e1, e2, -⟩ := hs
    rw [hk] at e1
    have := hx r b0 hb e1.symm
    simp only [hk, e1.symm, ite_true] at e2
    rw [e2]; exact this

end FF
