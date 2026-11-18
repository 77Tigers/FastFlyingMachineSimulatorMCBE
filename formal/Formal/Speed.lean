/-
Statements about speed. Speed is measured as in the research tools: the change of
the minimum X over all blocks (piston arms included), and one tick is 0.1 s, so
`v` blocks per second is `v / 10` blocks per tick.
-/
import Formal.Sim
import Mathlib.Data.Rat.Defs
import Mathlib.Order.Basic

namespace FF

/-- The minimum X over all blocks (`none` for an empty world). -/
def St.minX? (s : St) : Option Int := (s.world.keys.map (·.x)).min?

/-- After `t` ticks of the run with oracle `o` from `s`, the minimum X has advanced by at
least `d` (and the run has not hit a Rust error). -/
def AdvancedBy (c : Config) (o : Oracle) (s : St) (t : Nat) (d : ℚ) : Prop :=
  ∃ s' x x', run c o s t = .ok s' ∧ s.minX? = some x ∧ s'.minX? = some x' ∧ d ≤ (x' - x : ℚ)

/-- The flyer `s` *can go faster than* `v` blocks per second: some run is, by a fixed
margin, ahead of speed `v` at arbitrarily late times. (User's reading: there is a run that
violates the bound.) -/
def CanBeFasterThan (c : Config) (s : St) (v : ℚ) : Prop :=
  ∃ o : Oracle, ∃ ε : ℚ, 0 < ε ∧ ∀ T : Nat, ∃ t ≥ T, AdvancedBy c o s t ((v / 10 + ε) * t)

/-- The uniform version: every run stays within a constant of speed `v` at all times. -/
def AlwaysAtMost (c : Config) (s : St) (v : ℚ) : Prop :=
  ∃ C : ℚ, ∀ (o : Oracle) (t : Nat) (d : ℚ), AdvancedBy c o s t d → d ≤ v / 10 * t + C

end FF
