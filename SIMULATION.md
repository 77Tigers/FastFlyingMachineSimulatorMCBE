# Simulation rules implemented

`Flyer::tick()` performs one power stage, then one piston stage. It returns a
`TickReport` with counts. It uses the state already present in the flyer; it
does not validate whether a loaded arrangement is reachable in Minecraft.

## Power stage

Stationary rods and powered observers hard-power a solid block directly in the
direction they face. The solid kinds are slime, honey, smooth stone, and glazed
terracotta. A rod or redstone block soft-powers each adjacent piston, and a
powered observer soft-powers an adjacent piston only when facing it. The piston
ignores every source and hard-powered neighbour directly in front of it.
Moving sources emit no power; moving targets receive none. Piston power is
calculated from the stage's starting arrangement and cached until the next
power stage. The cache is cleared when a piston moves. Finally, all observers
are turned off, including moving observers.

## Piston stage and chunks

All nonmoving, unpowered pistons have `angry` cleared before any piston update.
Moving pistons keep `angry`. The chunks that contain blocks at this point form
the fixed chunk list for this tick. Chunks use world-aligned boundaries:
`(local_x + phase_x).div_euclid(16)` and the same for Z. The stored disk
subchunks use local boundaries, so the two groupings may differ.

One SplitMix64 draw advances the flyer's saved RNG state and provides the tick
shuffle seed. Chunk order is a Fisher–Yates shuffle of sorted chunk positions.
Each chunk's piston positions are read when that chunk's turn starts, sorted,
then Fisher–Yates shuffled with a seed derived from the tick seed and the
chunk's position relative to the occupied chunk set. This keeps the order
unchanged when saving shifts flyer coordinates. Moving pistons are omitted.
Each candidate is checked again before
its update because an earlier piston may have moved it.

An angry piston that was moving during the clearing pass can finish moving
before its destination chunk's turn, then act without power in that chunk.

## Discovering blocks to move

The piston first discovers the full source set without modifying the world.
For extension, the first block is directly in front and movement follows the
piston's facing. For a sticky retraction, the block immediately in front is
deleted first; discovery starts two blocks ahead and movement goes toward the
piston. A directly pulled glazed terracotta block is ignored.

For each selected block, an occupied destination adds its occupant to the set
as a pushed obstruction. A selected slime or honey block also adds all six
face neighbours that it sticks to. Slime and honey do not stick to each other;
neither sticks to glazed terracotta. Any immovable neighbour is skipped by
adhesion. Immovable destinations fail the move. The initiating piston is
immovable and nonsticky for its own move. Other immovable blocks are moving
blocks, piston arms, and pistons in states 1, 2, or 3. Each source counts once
toward `push_limit`; the initiating piston and its arm do not count.

The search repeats until no new blocks appear. If it fails, extension remains
in state 0 and becomes angry; a failed sticky pull still retracts without
pulling. On success, all source blocks are removed before any destinations are
filled. The destination blocks have `moving=true`, and their positions are
stored in the piston list. A successful extension creates a nonmoving arm in
front and enters state 1. A retraction removes whatever was in front, then
enters state 3. State 1 or 3 clears `moving` on listed destinations, empties
the list, and enters state 2 or 0 respectively.
An observer in that list becomes `powered=true` as soon as its movement
finishes. The next power stage consumes that pulse and turns it off.

The retraction discovery uses the same obstruction rule as extension: an
attached block can push a further movable obstruction backward. Glazed
terracotta can join through that collision, though it cannot be pulled
directly or by adhesion.
