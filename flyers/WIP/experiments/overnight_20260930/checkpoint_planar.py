from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[3]
def write(p,s):p.write_bytes(s.encode('utf-8'))
p=h/'FINDINGS.md';s=p.read_text(encoding='utf-8')
s=s.replace('- Banked mmwmmw3.333bps:PL57, all80 full audits,161 boundary blocks.','- Banked mmwmmw3.333bps:PL57, all80 full audits,161 boundary blocks.\n  New planarPL37 (109 blocks) passes encoded10000-tick exact verification\n  and conservation audit;80 samples live in67993. Connected trimming10068\n  is separate and must not overwrite thePL37 evidence.')
s=s.replace('tagged1000-tick ledger gives target300 actions/min7/max8. No copy proof yet.','tagged1000-tick ledger gives target300 actions/min7/max8. Literal1/2/4/8\n  bridged copies now pass short240-tick exact checks at whole limits\n  66/83/119/195. Full tagged/case validation live in35226; no full copy\n  proof yet. Fixed connectors and unchanged translated tile are preserved\n  in `compact_mixed_tile_bridge.json` and `compact_mixed_tile_bridged`.')
s=s.replace('- Distributed mixed8-cell role ring: v2 is live in50516; first4 short cases\n  clean3bps/max54–56.','- Distributed mixed8-cell role ring: v2 completed32 attempts,5 routed,\n  all5 clean3bps/max54–56 in short tests.')
s+='''
## Coplanar mmwmmw ports and smaller literal mixed chains

`mmw_planar.py` keeps the three different movement words and twelve normal
piston lifecycles, places each body's four target contacts on one initial
X plane, and uses nine mandatory sticky cells in a transverse cross. The
two late-burst pistons start one cell farther back, keeping their owned
sources unaligned during the first burst. Per-source observer directions
and intermediate contact/cross-power gates are enforced before routing.
Recovery is covered with physical contacts, then connected rails are routed;
no helper movement is assumed externally.

48 bounded attempts (three triangle layouts,16 seeds) gave11 routed/clean
240-tick cases. The safe triangle seed1 needs onlyPL37 and109 boundary
blocks:55 slime,28 honey,6 redstone,6 observers,12 pistons and2 arms.
`mmw_planar_safe_s001_pl37.flyer` passes full encoded10k verification at
+4/12 and all833 exact cell/owner boundaries, conservation and zero failures.
The independent80-case sweep is pending. This is a strong pattern-specific
lead, not a banked record yet and not an improvement on mmmmwwPL22.
`trim_planar_mmw.py` reuses the existing connected deletion/exact-cycle gate;
its diagnostics and geometry go to `trim_planar_mmw`, not prior evidence.

The smaller five-cell mixed target now has literal translated1/2/4/8 copies.
`duplicate_compact_mixed_tile.py` freezes one interface, and
`bridge_compact_mixed_tile.py` creates fixed helper connectors from two
copies which are then repeated unchanged. All assemblies remain connected
and match complete +3/10 boundaries in240-tick checks, with whole loads
66/83/119/195. `validate_compact_mixed_tiles.py` checks every copy for3000
actions/10000 ticks and max local load8, then runs1/8-copy80-case sweeps.
Driver overhead remains separate; this is not a wholePL8 flyer.

Live native sessions at this checkpoint:15441 purePL102 encoded80;
16380 old eight-tilePL21780;67993 planarPL37 encoded80;35226 compact tile
full validation;10068 connected planar trimming. Resume confirmed live
sessions rather than restarting observation timeouts. Native32070 bridge
finished all four short checks;30646 planar synthesis finished.
'''
write(p,s)
p=root/'flyers/RESEARCH_LOG.md';s=p.read_text(encoding='utf-8').replace('both with all80 full exact audits','all with all80 full exact audits')
s=s.replace('This does not beat the separate mmmmwwPL22 record.','A new coplanar-port candidate reaches **PL37** with109 blocks and passes the full encoded10000-tick exact audit; its80-case sweep and connected trimming are running. This does not beat the separate mmmmwwPL22 record.')
s=s.replace('with full exact single-extension validation at whole-assemblyPL53.','with full exact single-extension validation at whole-assemblyPL53. Literal1/2/4/8 copies now pass short exact tests at whole limits66/83/119/195; full tagged and80-case audits are running.')
write(p,s)
p=root/'flyers/WIP/experiments/INDEX.md';s=p.read_text(encoding='utf-8');s+='\nLatest overnight checkpoint: planar `mmwmmw`PL37 passes full exact10k;80-case sweep and connected pruning pending. Compact mixed local8 tiles pass short literal1/2/4/8 chains; full checks pending. See the authoritative checkpoint in overnight findings before repeating work.\n';write(p,s)
