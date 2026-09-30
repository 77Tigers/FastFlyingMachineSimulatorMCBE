from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[3]
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_bytes(s.encode('utf-8'))
p=h/'FINDINGS.md';s=read(p)
s=s.replace('New connected pruning44497 removes5 cells in first round; full run pending.','Connected pruning44497 completed:5 cells removed, full exact10k encoded\n+  verify/audit pass, maximum remains102. No extra80 sweep launched.\n+  All-ten-body rerouting77512 is live; accepted smaller bodies so far keep102.')
s+='''
## mmmmww late-burst source separation

`mmmm_planar.py` derives a planar four-port interface for mmmmww. The first
two sources belong to the target (redstone then observer); the next two
belong to the separate body with phase4 (redstone then observer). The
one-dimensional source alignment enumeration admits exactly these four
choices: target supplies0/1, phase4 helper supplies2/3. This is a timing
result only.32 physical layouts all reject:29 mandatory contact conflicts,
3 source attachment failures. `mmmm_planar_mandatory_witness.json` shows
the target's port temporarily becomes adjacent to the foreign source after
its first move. Direct side power does not preserve that source owner.

`mmmm_glazed_ports.py` then separates the late-burst source by a glazed
solid terminal: a rod powers the first late member through the terminal,
and a helper observer powers the second. The helper pushes its glazed
terminal by a sticky cell immediately behind; glazed does not adhere to
the target. Six separate bodies permit every target/helper pair to have
opposite materials. All four movements of every target still require a
physical piston and all four recovery movements require legal contacts;
no helper motion is injected externally. Terminal trajectories are fixed
obligations, with global mediated-power gates added before routing.

The first eight narrow layouts give7 mandatory failures/1 source overlap.
`mmmm_glazed_mandatory_witness.json` localizes this failure to neighbouring
module sources, rather than the target's own late-burst source. The wider
six-module placement (`--wide`, native41199) now passes that gate and has
one routed candidate after three attempts. Short physical simulation is
pending; the terminal transport assumptions are not proven until it passes.
This is not a higher-speed record and does not change mmmmwwPL22.

Pure-pull all-body rerouting77512 operates on the already trimmed102 lead,
intersects prior selected ports with surviving contacts, and preserves the
first102 bank evidence.5-cell pruning passed full encoded verification and
audit but did not lower the maximum load. New rerouting reduces more cell
counts while keeping102 in short exact checks; full result pending.

`bank_pending_pull3.py` (native50608) waits for the already-live15441 sample
command's completion report, then invokes the unchanged strict `bank_pull3`
gate. It will bank102 only on all80 complete, full10000-tick exact cases;
the result goes to `pending_pull3_bank_result.json`. A failed/partial sweep
does not bank. This completes an authorized audit even if model usage stops
before the native sweep finishes. No reset, purchase or simulator change.

Current live sessions:15441 pure102 samples;50608 gated bank follow-through;
16380 old local11 eight-copy80;35226 compact local8 endpoint80;61702 mixed
gauged closure;77512 pure all-body reroute;41199 wider glazed mmmmww ports.
Latest usage ordinary allowed,80% five-hour and98% weekly. Goal remains active.
'''
write(p,s)
p=root/'flyers/RESEARCH_LOG.md';s=read(p);s=s.replace('PL102 is undergoing80-case certification and further connected pruning.','PL102 is undergoing80-case certification; connected pruning removed5 cells without lowering102, and all-body rerouting continues. A strict gated native follow-through banks102 only when that full sweep completes.')
write(p,s)
