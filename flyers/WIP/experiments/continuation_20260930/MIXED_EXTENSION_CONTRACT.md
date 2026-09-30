# Next 3 bps extension contract (proposed, not geometry-validated)

The user reiterated the friend's trick and clarified that the front segments
are **different bodies from the main back chain/loop**. Do not turn the helpers
into extra links in the back loop or assume they share its phase.

The exact phase table and interface bindings below are a proposal derived
from the earlier handoff. The user's fixed constraints are role separation
and the two-pusher design, not these unvalidated geometry choices.

| Body | Slots that start +X movement | Role |
| --- | --- | --- |
| Back target T | 0,1,2 | Main chain body; two pushes, then one pull |
| Middle helper M | 0,3,4 | Separate front body carrying the pulling sticky |
| Front helper F | 1,2,3 | Separate body supplying the sticky's timed power |

Slots are two simulator ticks; all bodies advance +3 in ten ticks. Shift the
whole interface's phase for other chain links. The main loop member also
drives a **separate segment in front**, using two pistons as the user described.
Do not silently give that front segment a three-pusher drive in a proposed
implementation. The table above is the older handoff's timing witness, not
a validated binding of every drive edge in the clarified architecture.
M/F remain a distinct helper subsystem; their drives and piston passengers
must be counted separately. Extra front helpers may distribute the burden.

Sticky S faces -X and is carried by M. M's slot0 motion brings S into F's
power range. S extends in slot1 while T receives its second normal push and
F moves its source away. S retracts in slot2 and pulls T. S is recovered
before M moves again in slot3. A transverse source can distinguish alignment
before/after M's move without powering S early from +X.

For an initial S base X=s, M's slot0 gives S base s+1; T's pull source must
be s-1 before slot2 and **s-3 initially**, after its two preceding pushes.
The destination is s before the pull. Initial hardware and contacts are
measured before tick0 power, not copied from the pull frame.

Validation obligations:

- Distinguish T, M and F despite overlapping or equal displacement.
- Keep two normal members in T's push group; remove the third normal from
  geometry and passenger accounting.
- Discharge M/F movement and power assumptions with actual helper drives.
- Check S's forbidden early power, empty arm sweep and intended T source.
- Reject unwanted adhesion **and occupied destinations that recruit a helper**.
  The older helper's tick6 pull recruited30 blocks through an obstruction.
- Duplicate a module on a preserved driver before closure. Separate actual
  core, helper and driver loads, and test each tagged body.
- Require full block/owner recurrence and80 full phase/RNG samples before
  banking. An externally moved fixture is only an interface check.

Reference evidence: `astra_pull3/retrofit.py` has a sustained one-interface
mixed proof at high load; `sol_extra_front_20260927/FINDINGS.md` diagnoses the
failed helper and corrected relay. Neither establishes a compact chainable
3 bps module. This records the user's clarification and the next bounded
question; it does not claim another new flyer.
