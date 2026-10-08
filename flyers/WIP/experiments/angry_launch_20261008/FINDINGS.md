# Small angry-piston launch demo

`angry_launch_demo.flyer`: 10 occupied cells including one piston arm (9 permanent blocks), encoded push limit 3, RNG8, X phase0, Z phase15. Built from scratch; no private flyer was read or copied.

One stock-simulator test was run and passed (`check.txt`). Tick1: P fails against the powered extended sticky piston and becomes angry. Tick2: the honey carriage moves P across the Z chunk boundary. Tick3: the carrier finishes in the earlier chunk; P appears in the later chunk's candidate list and pushes the slime target without adjacent power. Tick4: target movement finishes. Tick5/6: P retracts and settles.

This is a one-shot illustration of the last diagram, NOT a self-propelled flyer or a guaranteed 5bps design. The saved seed was selected analytically to put the carrier's chunk before the receiving chunk at tick3. Other seeds/phases are not claimed to work. The carrier begins in state3 to delay pickup by one tick; P begins unarmed, so anger is actually generated during the demo. Intentional failed extension attempts are the arming mechanism, not test failures.

Generator: `python flyers/WIP/experiments/angry_launch_20261008/build.py`.
Checker: compile `check.rs` against the stock `target/release/libfastflyer.rlib`; executable is `../bin/angry_launch_check.exe`. No simulator changes, banking, long runs, or follow-up optimization. User requested a small single attempt and immediate stop on failure.
