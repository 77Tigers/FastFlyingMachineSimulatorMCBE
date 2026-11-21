"""Replay the Round 7 searches from their declared inputs."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from itertools import product
from pathlib import Path
import json
import re
import subprocess
import tempfile

import back_body
import conductors
import plates
import ports
from handoffs import HERE, FULL, read_links, NAMES
from second_pull import modes, incoming_checks
from split_sweep import sweep


def port_row(arg):
    mode,r=arg
    p=subprocess.run([HERE/'port_sweep','12',str(r),mode],capture_output=True,text=True,check=True)
    if p.stdout:
        raise ValueError('a rigid skeleton passed the gate')
    return list(map(int,re.findall('(?:poses|blocked|transport|retained)=(\\d+)',p.stderr)))


def ports_result():
    out={}
    for mode in ('free','borrowed','shared'):
        with ThreadPoolExecutor(4) as pool:
            rows=list(pool.map(port_row,((mode,r) for r in range(3,14))))
        out[mode]=dict(columns=['poses','hardware','transport','retained'],by_r=rows,
                       total=list(map(sum,zip(*rows))))
    out['pinned_cp']={str(n):ports.port_check(n,False) for n in (12,13)}
    out['four_strokes']=ports.four_strokes()
    assert out['pinned_cp']['12'][0]=='INFEASIBLE'
    assert out['pinned_cp']['13'][0]=='FEASIBLE'
    return out


def doubled():
    counters,rows,examples=modes(10)
    stage=Counter(); incoming=[]; n=0
    for row in rows:
        tries,fail,ok=incoming_checks(row);n+=tries;stage.update(fail);incoming+=ok
    bounds={s:max((r[1] for r in incoming if r[0]==s),default=None) for s in NAMES}
    edge=read_links()
    rings={}
    for changed in ((),(0,),(1,),(0,3),(1,4)):
        caps=[11,11,8]*2
        for i in changed:caps[(i+1)%6]+=1
        peak=-100;first=None
        for seq in product(range(3),repeat=6-len(changed)):
            it=iter(seq);kinds=[3 if i in changed else next(it) for i in range(6)]
            offsets=[]
            for i,a in enumerate(kinds):
                j=(i+1)%6;b=kinds[j]
                if a==3:
                    # t>=1 costs at least t+10 rigid cells, including the
                    # shared pickup, distinct direct gate and three fronts.
                    val=max(0,caps[j]-10)
                elif b==3:
                    val=bounds[NAMES[a]]
                    if val is None:break
                else:
                    val=edge[a,b,caps[j],FULL[a]]
                offsets.append(val)
            if len(offsets)==6 and sum(offsets)>peak:
                peak=sum(offsets);first=[kinds,offsets]
        rings[str(changed)]=dict(maximum=peak,first=first)
    return dict(cap9=dict(modes(9)[0]),cap10=dict(counters),input_poses=n,
                rejected=dict(stage),retained=len(incoming),max_incoming=bounds,
                rings=rings,whole_link_maxima=[[*k,v] for k,v in sorted(edge.items()) if k[3]==FULL[k[0]]],
                smallest=examples['local'],cp={
                    str(cap):back_body.local((0,1,1),(0,1,0),(0,-1,0),(1,-1,0),(1,0,0),
                                             cap=cap,pickup=(0,0,1)) for cap in (9,10)})


def conductor_result(params):
    case,stages,materials,passes=conductors.check(params)
    return dict(cases=case,stages=stages,material_outcomes=materials,passed=passes)


def gate_control():
    shape=(((0,-1),(0,1),(1,0)),((1,-1),(1,1)),((0,0),))
    fixed,empty,noglue,_,roots=plates.make_pose('T3',shape,1,3,1)
    state,layouts=plates.solve_body(fixed,empty,noglue,roots,11,native=True,maxresults=20000)
    for cells in layouts:
        if plates.first_order('O3','T3',1,3,1,shape,-1,cells,None)=='passed':
            status,selected=plates.solve_body(fixed,empty,noglue,roots,11,window=set(cells),raw_cp=True)
            assert status=='FEASIBLE' and plates.first_order('O3','T3',1,3,1,shape,-1,selected,None)=='passed'
            return dict(status=status,geometry=selected,orders='passed')
    raise ValueError('ordinary single-body gate did not pass')


def failure():
    shape=(((-1,0),(0,-1),(0,1)),((-1,-1),(-1,1)),((0,0),))
    cells=((-4,-1,1),(-3,-1,1),(-2,-1,1),(-1,-1,1),(0,-1,1),(0,1,1),
           (1,-1,1),(1,0,1),(1,1,0),(1,1,1),(1,1,2))
    return plates.first_order('O3','T3',2,-1,1,shape,-1,cells,None,detail=True)


def main():
    out={}
    out['two_plane']=ports_result()
    out['second_pull']=doubled()
    out['ordinary_control']=gate_control()
    out['one_step_failure']=failure()
    with ProcessPoolExecutor(6) as pool:
        out['carrier_glaze_or_rod']=list(pool.map(plates.detailed,plates.REQUESTED))
        out['donor_glaze']=list(pool.map(conductor_result,plates.REQUESTED))
    with tempfile.TemporaryDirectory(dir=HERE) as folder:
        a,b,file=sweep(Path(folder))
        out['crossed']=dict(programs=a,placements=b,retained=file.read_text().splitlines())
    assert out['second_pull']['cp']['9'][0]=='INFEASIBLE'
    assert out['second_pull']['cp']['10'][0]=='FEASIBLE'
    assert out['one_step_failure']['discovered']==16
    text=json.dumps(out,indent=2)+'\n'
    return text


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.write_text(main())
