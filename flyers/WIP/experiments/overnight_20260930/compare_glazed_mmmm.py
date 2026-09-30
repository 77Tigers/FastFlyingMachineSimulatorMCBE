from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'compare_mixed_phases.py').read_text()
a=s.index('S=[[');b=s.index('\ndef main()',a)
s=s[:a]+"S=[(1,1,1,1,0,0),(0,0,1,1,1,1),(1,1,0,0,1,1)]*2;DISP=[[sum(word[:t]) for t in range(6)] for word in S];K=[Kind.SLIME if i%2==0 else Kind.HONEY for i in range(6)]\n"+s[b:]
s=s.replace('mixed3_compact_manifest.json','mmmm_glazed_wide_manifest.json').replace('pentagon_v0_s010.flyer','six_s001.flyer').replace('mixed3_compact_candidates','mmmm_glazed_wide_candidates').replace('mixed3_pentagon_s010_snapshots.csv','mmmm_glazed_wide_s001_snapshots.csv').replace('mixed3_pentagon_s010_phase_diff.json','mmmm_glazed_wide_s001_phase_diff.json')
s=s.replace('(tick//2)%5','(tick//2)%6').replace('tick//10','tick//12').replace('cycle*3','cycle*4').replace('%5','%6')
s=s.replace('for p,owner,observer in m[\'sources\']:put(p,cycle*4+DISP[owner][slot],Block.observer(5,powered=bool(S[owner][(slot-1)%6])) if observer else Block(Kind.REDSTONE_BLOCK),\'source\'+str(owner))',"for p,owner,observer,direction,rod in m['sources']:put(p,cycle*4+DISP[owner][slot],Block.observer(direction,powered=bool(S[owner][(slot-1)%6])) if observer else (Block.rod(direction) if rod else Block(Kind.REDSTONE_BLOCK)),'source'+str(owner))\n        for p,owner in m['glazed']:put(p,cycle*4+DISP[owner][slot],Block(Kind.GLAZED_TERRACOTTA),'glazed'+str(owner))")
exec(compile(s,str(h/'compare_glazed_mmmm.py'),'exec'),dict(__file__=str(h/'compare_glazed_mmmm.py'),__name__='__main__'))
