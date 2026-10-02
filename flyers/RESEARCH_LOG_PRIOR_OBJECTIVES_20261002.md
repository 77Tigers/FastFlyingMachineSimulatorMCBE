# Prior objectives preserved 2026-10-02

Historical section moved intact from RESEARCH_LOG.md; newer verified records are in the active log.

## Objectives and verified records

**Previous best, 2026-09-27: PL10 at 2.5 bps, pulling-only.** `bank/pl10/pulling_alternating.flyer` uses four -X sticky pistons and travels **2,500 blocks in 10,000 Rust ticks**. All 80 RNG/phase samples passed conservation and complete translated state/owner-list recurrence every eight ticks, with zero extension failures. A full traced run confirms maximum successful load 10 and zero movement failures. `bank/results.csv` includes the result. Details below.

The previous normal-piston PL11/PL12 records remain banked as `bank/pl11/diagonal_alternating.flyer` and `bank/pl12/diagonal_alternating.flyer`. Each also moves 2,500/10,000 with 5,000 extensions and 21 end blocks and passed the same 80-case audit: RNG `[0,1,2,5,42]`, independent X/Z phases `[0,7,8,15]`.

**Primary objective: 3 bps at PL17 or lower.** The user's friend reports a **PL12/3 bps** two-push/one-pull design; this is the stronger aspiration, but no coordinates or file were supplied. It is guidance, not a verified result here. The user explicitly authorized improving **3.333 bps concurrently**, superseding the earlier deferral of that track. Current verified references remain `WIP/three_push_ring_pl19.flyer` (3,000/10,000) and `bank/pl22/four_push_ring.flyer` (3,333/10,000; original retained in WIP). The bank now spans PL8–PL24; empty limits are not evidence of a working design.

The user permits Sol subagents and any format-valid initial state. Give each agent a concrete, distinct task and its own experiment directory. Sol agents hit a usage limit during this continuation; unfinished scripts/results remain on disk. Do not mistake an interrupted task for an exhausted search.

