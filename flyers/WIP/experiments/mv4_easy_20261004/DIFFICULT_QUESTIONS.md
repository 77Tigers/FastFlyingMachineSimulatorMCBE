# Questions for the user and Astra

**Astra response:** [ASTRA_PLAN.md](ASTRA_PLAN.md) gives concise answers,
conditional reasoning and eight small implementation tasks. Use that plan next;
the questions below retain the original handoff context.

These are the mechanism or global-layout problems left after the easy work in
Astra's existing directions. No new mechanism family has been investigated.
Read `FINDINGS.md` for final bounds, artifacts and the finite search coverage.

1. **What is the minimum practical core footprint for the present interfaces?**
   The best verified flyer needs about33 glue cells in its largest template.
   Greedy pruning, fixed-neighbor rerouting and the saved-layout sweeps do not
   establish a lower bound. Can a connectivity/Steiner formulation prove what
   the mandatory ports and swept keepouts require, or produce a much smaller
   repeated template? Distinguish routing failure from interface impossibility.

2. **Can the fourth piston share the first three pistons' power arrangement?**
   The existing bank has a three-member shared hub and a separate fourth-member
   ribbon/source. Can all four members share a compact pulsed interface without
   attaching the observer to the driven core, powering an unintended member, or
   removing a required pickup? Co-locating these terminal clusters is likely a
   bigger saving than another shortest-path seed. Preserve the settlement pulse;
   the already-tested direct rod replacement stalled.

3. **Are four members per bank really necessary for mv4?**
   Earlier bounded three-member and pickup-removal tests failed, but they were
   not a proof for every interface. Can a smaller member group recover and hand
   off under every reachable update order? Use the set of reachable passenger
   states, not one rigid assumed member itinerary. If four are necessary, which
   passenger moves or loads can be shared across banks instead?

4. **Can a genuinely simple backbone satisfy the present interfaces?**
   The one/two-backbone tests failed for the selected layouts and terminal-stub
   domains. Is the extra routing depth forced by these port obligations, or can
   another regular placement make a comb-like body work? Which local port changes
   would make a straight, teachable template possible? Do not turn the bounded
   domain negatives into a general impossibility claim.

5. **What sets the passenger overhead in the largest action?**
   Load accounting on the compact PL43 bank shows its43-cell peak is33 glue,
   eight piston passengers and two observers, occurring84 times in10,000 ticks
   (`load_profile.csv`; zero movement failures). The conservative glue+10 search
   allowance is therefore attained in this tested run. Which passengers are forced
   into the peak load, and can a different valid handoff reduce that peak while
   keeping all rear mv4 cores doing the driving? Front helpers should support or
   pull them, rather than become an engine pushing passive mv4 attachments.
   If that10-cell overhead remains, the observed33-glue peak body would need
   to shrink to25 glue to reach PL35. This arithmetic is not a global lower bound.

6. **How should correctness be certified beyond the80 sampled cases?**
   Core geometry and moving duration are exact in every tested tick, while full
   piston/owner-state recurrence remains unestablished. Is there a finite
   reachable-state certificate that accounts for cached power, same-tick
   settlement and chunk order, or a justified equivalence for interchangeable
   piston identities? A quotient must preserve safety and phase timing; merely
   ignoring owner lists would not be a certificate.

The preferred PL<36 target remains a research question. These questions should
be resolved before launching another broad new mechanism search. Any direction
outside Astra's listed work requires checking with the user first.
