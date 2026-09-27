# Diagonal `mwmw` one-interface fixture

`diagonal.rs` is a bounded diagnostic with one A interface and a **scripted B
driver**. It is not a self-running flyer. The script temporarily installs a
normal +X piston and redstone block behind B before slots 1 and 3, and removes
that fixture hardware after each two-tick extension. Both A and B movements,
moving ownership, retractions, observer pulses, power consumption, and source
discovery use unmodified `Flyer::tick_traced` at encoded push limit 12. The
observer pulse arises naturally when Rust finishes each B movement.

Initial coordinates: H `(0,0,0)`, O `(0,-1,0)` output +Y and powered, normal
P0 `(0,0,1)`, normal P1 `(-1,1,0)`, five slime A cells
`(-1,1,1) (0,1,1) (1,1,1) (1,0,1) (1,1,0)`.

| Rust ticks | Event | Exact outcome |
| --- | --- | --- |
| 0–1 | O powers H, P0 fires | P0 moves five slime plus P1 (six sources), finishes extended; P1 reaches `(0,1,0)` |
| Before 2 | Script installs B driver | Normal driver at `(-1,0,0)` with redstone at `(-2,0,0)`. |
| 2–3 | Rust B move; P0 retracts | B moves H, O, P1 (three sources). P0 is extended and immovable. Observer powers naturally at tick 3; script removes the temporary driver and its arm. |
| 4–5 | O powers H, P1 fires | P1 moves five slime plus P0 (six sources), finishes extended; P0 reaches `(1,0,1)` |
| Before 6 | Script installs B driver | Normal driver at `(0,0,0)` with redstone at `(-1,0,0)`. |
| 6–7 | Rust B move; P1 retracts | B moves H, O, P0 (three sources). P1 is extended and immovable. Observer powers naturally at tick 7; script removes the temporary driver and its arm. |

Immediately before tick 8, the full serialized block state including observer
power matches tick 0 translated +2 X. The same actions succeed through tick 15.
Each real A movement contains only the five slime cells and the idle piston;
the initiating piston, H, and O do not join. No extension fails, and the
fixture asserts block conservation (with the temporary piston arm counted).

Rust traces show that each B action has exactly three sources: H, O, and the
retracted piston. The other neighbouring piston is in state 2 and excluded by
adhesion. The scripted installation/removal of the driver means its source
piston is not recycled as part of this fixture. This file establishes the
one-interface timing and adhesion, while a separate full layout is needed to
establish autonomous B drive and its actual load.

For this fixed contact geometry, all five slime rail cells have a specific
role. `(-1,1,1)` picks P1 during P0's push; `(1,0,1)` and `(1,1,0)` are the
two piston faces; `(0,1,1)` and `(1,1,1)` connect these contacts. Removing
any one disconnects a required pickup/contact from the source set. A mirrored
interface's honey H cannot simply replace one of these slime cells: honey
does not adhere to slime, so the rail breaks. Sharing a source piston or
finding a different contact position could change this bound; the five-cell
claim applies only to these fixed terminals and this connected slime route.

Reproduce from repository root in PowerShell:

```powershell
$lib = (Get-ChildItem target/release/deps/libfastflyer-*.rlib | Select-Object -First 1).FullName
rustc --edition=2021 -O flyers/WIP/experiments/sol_mwmw_fixture/diagonal.rs --extern fastflyer=$lib -L dependency=target/release/deps -o $env:TEMP/sol_mwmw_diagonal.exe
& $env:TEMP/sol_mwmw_diagonal.exe
```
