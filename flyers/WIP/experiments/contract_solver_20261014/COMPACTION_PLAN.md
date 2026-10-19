# Rear-first PL12 compaction plan

User steering, 2026-10-18. First test the synthesis tools on additional existing 3 bps flyers above PL12, aiming to bring complete designs to PL12. Prioritize reducing loads of segments near the back. Preserve distinctive mechanisms when useful; reproducing the original20-body and tm_smol PL12 designs alone does not demonstrate successful modification or new architecture design.

## Initial benchmark queue

1. `flyers/bank/pl13/exclusive_roles_3bps.flyer`: close-to-target case with a pull-only body.
2. `flyers/bank/pl14/mmwmw_two_pulls.flyer`: different motion word and twice-pulled rail; tests broader coverage.
3. `flyers/bank/pl18/n3_five_body.flyer`: smaller body-count architecture and a harder compaction target, after the nearer cases.

These are selected inputs, not new results or claims that their architectures can reach PL12. Their catalogue baselines and hashes are in results/compaction_benchmarks.json. Start with an action/body ledger of the first flyer; identify rear segments and their actual peak strokes before choosing a bounded change. Keep existing bank inputs intact.

## Directional load tradeoff

User steering2026-10-19: prioritize reducing rear push loads in exchange for greater loads or more hardware toward the front, within the complete flyer limit. Use complete per-stroke front budgets, and spend front capacity on rear recovery or power when useful. Minimize rear overload and recovery conflicts; total block count and equal loading across bodies are secondary. Fixed-geometry connector costs still count.

## Work cycle and acceptance

Account for every stroke: permanent glue, power blocks, attached hardware, spent pistons and transient passengers. Record which body carries each piston after firing, what powers it, when power switches off, and how it is recovered. Reduce rear peaks first, checking downstream loads so a rear improvement does not conceal an overloaded front. Replace or regenerate only the implicated interface initially; change roles or geometry when its complete budget cannot fit.

Reintegrate promising hardware in the complete natural flyer. Supplied interfaces and geometric feasibility remain component evidence. Accept a complete design only after independent80-case checking and80x10000 natural ticks with distance3000, conservation and zero movement/extension failures. Report both global peak and rear-body stroke loads. Preserve reproducible constructors and exact artifacts.

## Architecture experiments after the compaction benchmarks

Build a few explicit, budgeted hypotheses: interacting mirrored 3 bps flyers; a20-segment rear loop with four-way rotational symmetry; tm_smol-style interfaces; a front loop pushed once from behind, once from itself, and pulled once from ahead. Test power, recovery and all three moves before extensive layout search. These are user-proposed experiments, not demonstrated mechanisms. Seek both modifications of existing flyers and construction of new designs.

PL11 remains a longer-term hard research objective. The validated joint H module is available evidence, but its G strokes are supplied and closure is unproved. Do not resume unchanged local repair campaigns without a credible whole-interface allocation. No computation is active at this priority change.

## Medium-term sequence after accepted rear reroute

Five-body reroute is preserved and fully verified, with2 net glue reductions, rear peak17 and global18. One changed-context follow-up has exhausted1161 connected reroutes without another improvement. Move to a fresh spatial architecture rather than unchanged local repair.

The initial20-module stacked-ring role ledger is results/quarter_ring20_role_plan.json, reproduced by plan_quarter_ring.py. Its80 bodies/240 actions close in phase after5 links per quarter. With optimistic body masses X8/T7/G8/H6 it has rear max11/global12. H6 reserves RB+observer and allows only4 glue; power entries are obligations, not spatially verified implementations. Next establish a bounded closed quadrant geometry and material/contact assignment, then build/test a natural module with firing, switch-off and recovery. Close the complete flyer and require independent80 plus80x10000 before accepting a design. If its budgets or geometry fail, record the conflict and change the carrier/power allocation or try interacting mirrors. PL11 stays longer-term.
