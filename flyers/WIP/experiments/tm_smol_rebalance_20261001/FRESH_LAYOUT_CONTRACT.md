# Fresh 3 bps layout contract: fewer rear load-12 actions (proposal, not built)

Derived from the role analysis of the two human PL12 designs (`FINDINGS.md`). Purpose: a layout designed for the
push->pull principle, since both human fronts are geometrically saturated for retrofits.

## Accounting
- Every move: load = moved glue body (incl. its RB, stickies, observers) + riders (free pushers in transit).
- A push needs a free pusher carried +3 per cycle, mostly by the body behind its target. A pull needs a -X sticky on
  the puller (in front) plus a power source at the extension slot only.
- With mmmww rotations a puller rests 2 consecutive slots, so each body pulls at most once per cycle and every pull
  is on the victim's LAST move of its run (j_mmwmw model; all 6 tm_smol pulls and 10 original pulls obey this).
- Rider floor ~3 per move with 5-class rings (j_mmwmw `rider_floor.py`).

## Measured human structures
| | tm_smol | 3bps_original |
|---|---|---|
| layers | rear 5, middle 6, helpers 2 | rear 5, middle 5, front pullers 5, helpers 5 |
| pulled bodies | 6 (rear B11 never) | 10 (all rear + all middle) |
| rear move | 7-10 glue + up to 5 riders | 8 glue + 4 riders |
| load-12 actions | 12 (8 rear) | 14 (8 rear, 6 on B41/B42) |

## Rules for the fresh layout
1. Three layers per class (rear R <- middle M <- front F), every R and M pulled once on its last move (original's
   chain structure) so middle bodies need only 2 pushers and R carries <= 4 riders.
2. Rear bodies <= 7 cells incl. RB (6 glue + RB) => rear moves <= 11.
3. Power F's sticky with **M's own observer** (victim-observer rule: M moved at s-2, pulses at s-1; at s and s+1 it
   has moved relative to the resting F) instead of a helper-helper. This removes helpers and their pushers (which ride
   F). Leave a FREE LANE beside each F sticky reaching back ~3 cells to M's front so the observer (+<=1 support glue)
   fits; or let it hard-power an F glue cell beside the sticky. Same for M's sticky powered by R's observer only if
   R has slack (R then needs <= 6 cells).
4. Alternate materials between touching neighbours (slime vs honey) so bodies never fuse; glue beside pistons.
5. Pushers sit in the gap between a body's front face and the next body's rear face, are shoved/carried by the rear
   face and fire into the front body; give each column its own RB beside it (self-powered column).

## Predicted loads (role model)
`3bps_original` with helpers replaced by victim observers: 11 load-12 actions (vs 14), max 12, ~40 fewer blocks.
With rule 2 on the rear as well: rear 12s -> 0 if the 7-cell rear bodies can still hold contact, RB, column faces.

## Build order suggestion
Start from `3bps_original`'s rear+middle (keep them), and generate only the front layer (F bodies) from scratch with
the free lane of rule 3 and no helpers; screen with `score.py`/`loadhist.exe`; then attack the rear cell count.
