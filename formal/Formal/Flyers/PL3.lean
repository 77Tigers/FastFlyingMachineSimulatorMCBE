/-
A flyer exists at push limit 3: the bank's `compact_slime` (6 blocks) flies under every oracle,
at least one block per 6 ticks (1.67 blocks per second), forever.

The finite part (its 96 states up to whole-chunk translation, all their successors under every
chunk and piston order, and all 6-tick runs) is checked by evaluation (`native_decide`), which
trusts Lean's compiler in addition to the kernel.
-/
import Formal.Verify

namespace FF

open Std

private def P3 (x y z : Int) : Pos := ⟨x, y, z⟩

/-- `flyers/bank/pl3/compact_slime.flyer`. -/
def compactSlime : St where
  world := ExtTreeMap.ofList [
    (P3 0 0 0, Block.piston .px false false 0 false),
    (P3 0 0 1, Block.plain .slime false),
    (P3 0 1 1, Block.observer .ny true false),
    (P3 1 0 0, Block.plain .slime false),
    (P3 1 0 1, Block.piston .nx true false 0 false),
    (P3 1 1 0, Block.observer .ny false false)]
  lists := ∅

def compactSlimeCfg : Config := ⟨0, 0, 3⟩

/-- Its states, up to translation by whole chunks. -/
def compactSlimeStates : List St :=
  explore compactSlimeCfg 400 [compactSlime.norm.1] [compactSlime.norm.1]

theorem compactSlime_closed : closedB compactSlimeCfg compactSlimeStates = true := by native_decide

theorem compactSlime_progress : progressB compactSlimeCfg compactSlimeStates 6 = true := by
  native_decide

theorem compactSlime_start : startB compactSlimeStates compactSlime = true := by native_decide

/-- Under every oracle the PL3 flyer never errs, and every 6 ticks its rearmost block moves
forward by at least one. -/
theorem compactSlime_flies (o : Oracle) :
    (∀ t, ∃ s', run compactSlimeCfg o compactSlime t = .ok s') ∧
    ∀ t q (s s' : St) (m m' : Int), run compactSlimeCfg o compactSlime t = .ok s →
      run compactSlimeCfg o compactSlime (t + q * 6) = .ok s' →
      s.minX? = some m → s'.minX? = some m' → m + q ≤ m' :=
  flies_of_check _ _ 6 compactSlime_closed compactSlime_progress _
    (start_of_startB compactSlime_start) o

end FF
