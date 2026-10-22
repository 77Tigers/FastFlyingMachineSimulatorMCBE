"""Exact axial-prefix power screen for the X0-carried T0 push3 motor.
This tests direct observer or transverse RB contact, without occupancy,
carriers, loads, sticky power or native timing/recurrence acceptance.
"""
import argparse,json
from pathlib import Path

def prefix(w):return [w[:i].count('m') for i in range(5)]
def screen(word,observer):
 target=prefix('mmmww');source=prefix(word);offset=target[3]-source[3]
 contact=[offset+source[t]==target[t] for t in range(5)]
 pulses=[word[(t-1)%5]=='m' for t in range(5)] if observer else [True]*5
 powered=[t for t in range(5) if contact[t] and pulses[t]]
 return {'word':word,'observer':observer,'source_prefix':source,'motor_prefix':target,'axial_offset':offset,'powered_slots':powered,'isolates_push3':powered==[3]}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('output',type=Path);a=ap.parse_args()
 cases={f'{w}_{k}':screen(w,k=='observer') for w in ['wmmmw','mwwmm','wwmmm','mmwwm','mmmww'] for k in ['RB','observer']}
 assert cases['wmmmw_RB']['powered_slots']==[1,2,3]
 assert cases['mwwmm_RB']['powered_slots']==[3]
 assert cases['wwmmm_observer']['powered_slots']==[3]
 assert not cases['wmmmw_observer']['isolates_push3']
 a.output.write_text(json.dumps({'scope':__doc__,'cases':cases,'withdrawal':'G0 wmmmw RB shared with X0 mmmww-carried T0 push3 is not an isolated slot3 power source; initial contact geometry screens are not physical source feasibility evidence.'},indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v['powered_slots'] for k,v in cases.items()}))

if __name__=='__main__':main()
