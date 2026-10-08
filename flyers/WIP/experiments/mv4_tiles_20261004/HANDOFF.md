# Continue the backwards mv4 extension task

## Directions

- Build a **working all-sticky mv4 flyer with backwards tileable extensions**. Both requirements are mandatory, including the driver. A closed loop alone does not qualify.
- Add layers toward negative X, with usable rear attachments and no recovery dependency on a body behind the endpoint. Keep interior loads bounded; an end may gain fixed outgoing hardware when extended.
- Use three mv4 phases per unit; allow at most three additional bodies per unit. Symmetric six/twelve-core arrangements count as two/four units.
- Defer push-limit optimization. Prefer few pistons and at least three usable blocks below rear hardware.
- Preserve results and keep files few. **Do not change the simulator.** Full piston-state recurrence is not required; correct sustained simulator motion is.

## Context

**Status: unsolved. There is no verified all-sticky backwards tile.** Earlier work mistakenly prioritized a normal-piston loop. The user repeatedly corrected this: backwards tileability is the central objective. Do not present that loop, a separately copied independent flyer, or a short nonrepeating cascade as completion.

Workspace: `C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground`. Read `SIMULATION.md`, `flyers/RESEARCH_LOG.md`, and this directory's `FINDINGS.md`. All code here is experiment code; simulator/library files were not changed. Another agent's completed research is under `rigid_sat_20261004`; coordination was authorized via `flyers/chat.txt`.

An mv4 core starts a two-tick +X move every three ticks; layers contain phases 0/1/2. Moving power sources/targets do not participate in the power stage. A sticky extends, settles next tick, pulls two ticks after extension, and resets the following tick. Reset and movement completion can occur before a carrier acts in that same tick. Those races matter even though passenger identity recurrence is unnecessary.

### Saved controls and failed interfaces

| Artifact / script | Actual result |
| --- | --- |
| `ring_payload.json`, `ring.py` | Normal-piston reference only: 12-core quarter-turn loop, three low glue cells; 80/80 × 10,000 ticks at PL64, traced maximum action 53. Not a backwards tile. |
| `backward_prototype.json`, `backward.py` | Normal-piston driver + two rear layers, 36 cores. Passes 80/80 × 300 ticks at PL160, distance 100. Separate PL512 trace: maximum 115, no movement failures. Literal copies attempted at 1/4/8 layers collide; no tileability claim. |
| `all_sticky.json`, `sticky_backward.py --all-sticky` | 12-core loop with 48 -X sticky pullers. 0/80; first sample misses the phase-2 move at tick 8. Useful as a failed bank interface, not a working flyer. |
| `sticky_prototype.json`, `sticky_backward.py` | Normal driver + two sticky rear layers. 0/80, first sample fails at tick 8. Also fails the all-sticky-driver requirement. |
| `sticky_clock.json`, `sticky_clock.py` | 48 -X stickies with 48 observer passengers. 0/80; first sample misses phase 0 at tick 3. At PL4096 it advances only five blocks in 300 ticks. |
| `sticky_push.json`, `sticky_push.py` | Alternative using sticky +X pushers held powered until the target clears their pull range. Six members/core, 18-tick nominal itinerary. 0/80; first sample fails at tick 1. PL4096 does not rescue it. |

`BACKWARD_CHECKS.json` retains all 80 rows for each case, limits, geometry hashes and first failures. The three `*_first_failure.txt` files retain compact power/action traces. `.flyer` files outside the bank are ignored by the repository; **JSON geometry plus `check_backward.py --rebuild` regenerates them**. No failed design was banked.

### What needs solving

The four-member normal competition bank depends on the first powered pusher moving its target immediately and carrying competing idle pistons, clearing their cached power. A -X sticky extension moves no target until its later pull. Simply shifting the bank by two ticks therefore allows several extensions and unsafe subsequent pulls. Retraction removes the arm cell before discovery; another pull can remove a block the first pull just moved.

The observer-passenger clock pairs members 0↔2 and 1↔3. Each observer sits one cell +X ahead of its piston and is transported by collision on every piston ride; it faces the other member. Nominal geometry selects one pulse per 12 ticks. Actual extra pickups change the pulse timing, so the nominal argument is insufficient. Do not rerun the same geometry sweep expecting routing to fix this.

First close a **complete small repeating timing/interface contract**: one intended pull per core move, selective power, every actuator/source transport and all reset/finish orders accounted for. A revised clock, gating connection or properly driven helper remains open; none of these negatives proves helpers necessary or the problem impossible. Then route **literal interior copies**, checking adjacent copies during routing. The existing router solves each layer separately; its result is not automatically tileable. Use a compatible endpoint, test 1/2/4/8 copies and compare interior action loads as the chain grows. Only then optimize toward PL36, later PL24/12. Distinguish local tile PL from whole-flyer PL.

### Reproduce checks

From the workspace root, compile the experiment inspector against the current unchanged release library:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
python flyers/WIP/experiments/mv4_tiles_20261004/check_backward.py sticky_clock --rebuild
python flyers/WIP/experiments/mv4_tiles_20261004/check_backward.py sticky_clock --ticks 300
```

Other case names are the table's JSON basenames. Explicit phase tags handle rear cores with no observers; the older inspector misclassified those tails. The inspector checks core motion every tick, conservation, extension failures and a broad passenger transport window. Use `fastflyer-research audit` to measure successful action loads and detect failed sticky pulls; it is stronger than ordinary `measure` on that point. Do not use full-state recurrence as a prerequisite.
