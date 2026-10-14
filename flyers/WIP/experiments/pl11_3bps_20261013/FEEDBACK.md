# Feedback on extension contracts and the extension bank (running notes, 2026-10-13)

From using the bank and tools on a real target (3 bps at PL11). Each item: observation, evidence,
suggestion. "Tested" means a change was implemented and checked.

## Bank content and lookup

1. **Fixture loads hide rider cost.** 189/320 new fixtures only pass after dropping lone-piston
   passengers (hopping pistons that would fire out of turn once their neighbours are removed).
   Their natural loads are then 2-3 below the reference (sticky-chain pulls 9 vs 12 in tm_smol).
   For PL work the riders are the dominant cost (load law: avg load = 3 + cells/body), so a load
   in the bank is a *mechanism* load, not a placement cost. Suggestion: every entry should state
   reference load, fixture load and the rider deficit (now in `catalogue.json` `selected_loads`);
   lookup should rank by reference load or show both.
2. **`endogenous max` mixes the primitive with unrelated natural strokes** of kept hardware
   (n2_01: 6 from K1's pull, primitive 5). Catalogue now records per-selected-action loads.
3. **Order sensitivity is common:** 99/320 pass before_natural only (mostly single pushes by a
   lone kept piston). Two causes seen: a kept, powered, ready piston fires before the supplied
   stroke that originally preceded it; interchangeable pistons swap roles. Suggestion: label the
   *reason* in the entry (one-order because of actor race vs. because of supplied-stroke order).
4. **Human flyers are not exactly periodic** (interchangeable pistons, full state every 48 ticks):
   22/52 tm_smol fixtures need bounded recurrence or keeping three periods of actors. An
   `advance` recurrence (every identity at origin + k*advance, ports exact) in the Python checker
   would let many of these be exact-on-identities instead of bounded.
5. **yz symmetry**: physics is symmetric under the 8 yz symmetries (chunk phases cover the grid);
   the extractor dedups modulo them (123 duplicates). Bank entries are stored in one arbitrary
   orientation; a transform helper (ports, required_cells, piston/observer facings) would make a
   rotated reuse one call. Not a blocker.
6. Generated ring flyers (n3_five_body, five_segment_ring_*) give no entries under a load<=12
   filter: every action is 17-18. Fine, but worth saying so the bank's coverage is clear.

## Contract format / composition

7. **No composition check.** Two contracts that share a body (A's output body is B's input) have
   no tool that unions them, replaces B's supplied strokes by A's natural ones and checks caps
   and contacts. That is exactly the assembly step of "flyer from pieces". Suggestion: a
   `compose` command keyed on shared required_cells (bodies identified by pinned cells).
8. **Caps are reference measurements, not budgets.** For assembly the cap on a supplied stroke
   should be "PL minus what the other pieces put on this body in this slot". A per-body per-slot
   load budget table (output of the role ILP) is the natural source; contracts could import it.
9. Hardware keep-out regions are not expressible, so pieces designed separately can collide
   when assembled (and a symmetric twin has no declared envelope).

10b. **What actually worked as a method (2026-10-14):** abstract timing + rider accounting first (role ILP),
    then small hand-specified pieces as prescribed-input contracts, built by an agent and checked in the
    real simulator. Pieces A and B passed within an hour each and the obstacles were reported with exact
    geometry. Blind contract-search on large reference fixtures (n3_65, n3_135 at cap 11) made no useful
    progress and should not be the default use of the bank.
10c. **Bank R/F entries are the most useful entries for redesign work**: "back loop with front pulls
    supplied" (n3_134, natural max 10) immediately showed that human_3bps_original's back is fine and its
    12s come from front pistons. Consider promoting R/F extraction for every new flyer.
10d. **Contracts lack a geometric keep-out/neighbourhood notion**, so a link that passes in isolation (piece
    B with a one-cell stand-in neighbour) says nothing about whether the real neighbour fits. The failure
    was only found by a separate adjacency enumeration (geom*.py). A contract field for "this supplied body
    stands in for a real body of shape class S anchored to port P" would make such stand-ins honest.
10e. **satflyer5 race gap**: it treats a hopping piston touching two co-moving bodies as a safe leaf race,
    but the first mover can drag it into the other body's not-yet-vacated cell (found by the model ->
    contract bridge `model/sol2contract.py`; real sim blocks).

## Exact solver (satflyer5) as a contract solver

10. Its riders are hopping pistons (carrier chosen per slot), so it can solve 3 bps pieces with
    the human piston logistics. But power is deterministic: a piston may be powered only at its
    own fire slot, so the human "column of powered pistons, one random fires" cannot be expressed.
    Designs it finds are stricter than necessary (observer/rod per pusher).
11. Open-end chains need care: open-end riders still need carriers (fixed in `model/ring10.py`
    by giving module 0 no riders).
