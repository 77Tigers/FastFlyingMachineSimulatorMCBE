"""Retain a concrete mandatory-contact rejection, including source code site."""
from pathlib import Path
import sys,json,importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mixed',HERE/'derived_mixed3.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
failures=[]
def trace(frame,event,arg):
    if frame.f_code.co_name=='legal' and event=='return' and arg is False:
        failures.append(dict(line=frame.f_lineno,locals={k:v for k,v in frame.f_locals.items() if k in ('p','i','t','q','j','delta','rel','rp','owner','observer','r','pp','dp','f','target','sticky','near')}))
    return trace
sys.settrace(trace);ans,reason=mod.build(0,4);sys.settrace(None)
result=dict(seed=0,spacing=4,reason=reason,failures=failures)
(HERE/'mixed3_mandatory_witness.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
