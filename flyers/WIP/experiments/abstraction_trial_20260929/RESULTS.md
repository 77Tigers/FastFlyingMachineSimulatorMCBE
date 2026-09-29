# First abstraction trial — 2026-09-29

Both workers explicitly used GPT-6 Sol with Low reasoning and fresh contexts. One reconstructed every stage from a known fixture; the other attempted forward stages 5–7 from only stages 1–4 and general documentation. Astra reviewed contracts and failure attribution but supplied no new geometry to the forward worker. No simulator/editor or bank changes were made.

Fixture: `flyers/bank/pl10/pulling_alternating.flyer`. This small two-body mechanism exercises four sticky pistons, empty extensions, payload pulls and hardware transport. It does not establish arbitrary group-member order, mixed push/pull groups, or scalable extensions.

| Stage | Reconstruction result | Independent forward evidence |
| --- | --- | --- |
| 1. Segment motion | Eight-tick, +2 schedule extracted and trace checked | Used as input |
| 2. Groups and transport | Two two-member groups and ride slots extracted; identities reference-assisted, alternate winners untested | Supplied obligations were not all implemented |
| 3. Axial contacts | Action-time port coordinates checked after correcting source/destination error | Later coordinates were incorrectly treated as initial positions |
| 4. Contact topology | Partial relation graph, no independent embedding proof | Generic adjacency obligations did not provide a complete cyclic interface plan |
| 5. Local interfaces | Reference geometry described; no isolated cycle check | Single pull and empty reset passed; full cyclic interface incomplete |
| 6. Assembly | Original generator and known parameters regenerated an identical reference | One speculative PL10 assembly failed inherited transport and power requirements |
| 7. Validation | New 160- and 10,000-tick audits passed on identical reference | Eight-tick screen exposed failure; no repeating independent build |

Reference audit: distance 2,500/10,000 ticks, maximum successful action load 10, 1,250 translated eight-tick repeat pairs, zero movement failures and zero conservation-mismatch ticks, RNG initial 5 and X/Z phase 0/0. Broader historical 80-case evidence was not rerun. See `extraction/reproduce.ps1`, `audit_160.txt` and `audit_10000.txt`.

The forward failure begins at tick 0: the required A movement happens, but pistons A1/B1 are not carried with it. The worker initialized them using later action positions. At tick 2 its B route then carries A1 to the wrong future position. Subsequent power pulses were also never implemented. Primitive pull/reset success is therefore not successful interface construction. See `forward/motif_probe.py`, `screen.txt`, and stage5–7 reports. The attempt explored one speculative assembly, not an exhaustive route family.

## Findings

The layered representation is plausible but has not demonstrated independent synthesis or token savings. Two manual Astra corrections were needed: sticky pull source versus destination in the extraction, and earliest failure attribution/phase interpretation in the forward attempt. These are precisely the checks that should eventually become routine validator work instead of Astra diagnosis.

Strengthen stage 4 to specify contact choreography: named pickup/release faces and phase-indexed adjacency, including which body carries the power elements. Strengthen stage 5 to require a complete interface cycle under explicit external inputs. Make all coordinate phases explicit and check hardware displacement against the transport schedule. These revisions are appended to PIPELINE.md; they have not been retested.

Keep lower-stage design freedom: lack of supplied Y/Z coordinates is not itself a deficient handoff. The test also does not show Sol incapable of building the mechanism; it shows this bounded attempt violated existing obligations and did not complete its local interface stage.

Next discussion: what is the natural reusable interface unit in the user's design practice — one actuator, or a whole piston group together with pickup and power relationships? Prefer refining that boundary before adding more search or tooling.
