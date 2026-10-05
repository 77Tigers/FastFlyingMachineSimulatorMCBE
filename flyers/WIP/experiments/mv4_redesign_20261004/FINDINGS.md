# mv4 redesign: Astra's eight-task plan

The banked PL43 flyer remains the best verified result. No candidate from this
bounded session lowers the push limit. The control builder reproduces the bank's
exact content hash and passes the 80-case, 300-tick screen (`control.json`).

1. `builder.py` exposes piston sites, ribbon and observer positions/directions,
   OWN/PREVIOUS pickup faces, and following/previous carrier graphs. The default
   reproduces the saved PL43 flyer (`control.py`). The old builder is untouched.
2. At the first 43-cell action, tick 122, bank 5/piston 22 moves 33 glue, eight
   identified passenger pistons and two observers. The piston passengers are
   three of bank 4 on their following carrier, three of bank 5 on their own
   carrier, and two of bank 3 on their previous carrier (`peak.json/csv`). Piston
   identities are tied to unique YZ positions after checking the save translation
   Y+8,Z+16, rather than to normalized X.
3. All 4096 allowed carrier graphs were surveyed on 57 saved regular placements;
   60 graphs are connected half-turn-symmetric, 4032 connected relaxed, and four
   disconnected. Of 3427 sorted graph/placement interfaces tried with the actual
   static builder, 63 distinct graphs had an interface; ten were selected,
   including three with a relaxed repeated motif. The top graph uses F=i+1,
   P=i-1, with 12 mandatory glue cells per bank. Static validity does not imply
   a route (`graphs.py`, `graph_results.json`).
4. All 60 prescribed short route attempts on those ten interfaces failed to
   complete the joint route: caps 32/29/25, two seeds, three seconds each
   (`graph_routes/status.json`). This is a bounded router result, not a lower
   bound or a simulation failure.
5. The four-cardinal-piston/one-hub fixture reproduced the old three-spoke
   control, then rejected all 192 observer/pickup variants: 96 wrong firing
   plane, 16 observer/ribbon overlaps, 43 hardware failures, 37 body-contact
   failures (`four_spokes_results.json`). No global route was launched.
6. Both proposed balanced 2+2 hubs were screened over 46 and 56 unique pickup
   face sets, respectively, on the top three carrier graphs. One of 15,756
   combinations passed static checks: offset-pair hub on the best graph, with
   max mandatory glue 14. Six short routes at the same caps/seeds all failed
   joint routing. The first square-column rejection is a hardware collision in
   bank 0 at local coordinate (-2,3,2) (`two_hubs_results.json`,
   `hub_routes/status.json`).
7. In a 240-tick Rust trace of the bank, 456 complete fire-to-reset cycles all
   took three ticks, and 169 reset-to-pickup overlaps occurred on the same tick.
   Thus the conditional four-unavailable-ticks capacity premise is false as a
   universal statement. In the saved abstract competition contract, reversing
   reset and competing motor order at tick 0/member 3 changes pickup to a miss;
   same-tick pickup is not guaranteed for every update order. This screen does
   not prove a three-member design impossible, nor does it show an order-robust
   three-member contract (`lifecycle_result.json`). No new Rust confirmation was
   claimed for the reversed abstract order.
8. A 12rt kinematic front-helper screen (`helper_contract.py/json`) tested all
   six even rotations of `mmwmmw` and `mmmmww` and axial offsets -2..4. A normal
   sticky needs four stationary ticks for extend, finish, retract/pull, reset;
   `mmwmmw` has no such window. Two `mmmmww` rotations can pull the phase-2 core.
   The selected rotation starts helper moves at ticks 4,6,8,10, so its word is
   `wwmmmm` from tick 0. It rests at ticks 0–3, extends a backward-facing sticky
   empty at 0, and pulls the phase-2 rear core at 2. The helper base starts two
   X cells ahead of that core. Its observer's final ride settles at 11, supplying
   the tick-0 pulse; power is off for the tick-2 retraction. The three rear
   phases still move once each three ticks. The phase-2 core is natively driven
   at ticks 5,8,11 and pulled at tick 2. The helper itself rides rear core phases
   1,0,2,1 at ticks 4,6,8,10, advancing four blocks per 12rt. Rear cores remain
   the main drivers. This is a timing and relative-position contract only: no
   physical contact, power source location, order-robust ownership, or PL gain
   has been demonstrated. Carrying a helper may increase the other core loads.

**Power correction (discussion follow-up):** A fixed observer-to-sticky connection
on this helper pulses at ticks 6,8,10 as well as 0. At those three ride starts,
power is cached before transport; the sticky may extend before its carrier moves.
The self-observer proposal therefore does not supply the desired selective pulse
reliably. The table is a desired motion schedule with unresolved power gating,
not an electrically closed interface. The even-rotation screen also excludes
odd-offset helper words; it is not a complete mixed-word timing census.

| Tick | Rear mv4 phase moving | Initiator | Front helper | Sticky/power |
|---:|---:|---|---|---|
| 0 | 0 | rear | stationary | observer pulse powers extension into air |
| 1 | 1 | rear | stationary | power off; extension finishes |
| 2 | 2 | helper pull | stationary | unpowered retraction pulls core |
| 3 | 0 | rear | stationary | sticky resets |
| 4 | 1 | rear | carried by phase 1 | idle |
| 5 | 2 | rear | ride settles | idle |
| 6 | 0 | rear | carried by phase 0 | unwanted observer pulse; gating unresolved |
| 7 | 1 | rear | ride settles | idle |
| 8 | 2 | rear | carried by phase 2 | unwanted observer pulse; gating unresolved |
| 9 | 0 | rear | ride settles | idle |
| 10 | 1 | rear | carried by phase 1 | unwanted observer pulse; gating unresolved |
| 11 | 2 | rear | ride settles | observer queues next tick-0 pulse |

The four helper pickup contacts would need relative axial offsets 1,1,2,2
against their respective source cores at ticks 4,6,8,10. These offsets are
kinematic constraints, not constructed adhesive faces.

Next difficult questions: Can a repeated, physically separated set of contacts
carry the helper at those four starts while avoiding pickups in the other eight
core moves? Can its own moved observer power the sticky exactly once per period
without foreign-core adhesion or order dependence? Can moving one bank-4
following passenger off bank 5's tick-2 peak reduce the actual maximum after the
helper's four rides are counted? If not, the compact carrier graph's failure
suggests changing the pickup/owner mechanism, not just rerouting glue.
