import re,sys
cmd=None
for ln in open(sys.argv[1]).read().splitlines():
    if ln.startswith('##'): cmd=ln[3:]
    m=re.search(r"\} (INFEASIBLE|OPTIMAL|FEASIBLE|UNKNOWN|MODEL_INVALID)\w* ([\d.]+)$",ln)
    if m: print(m[1],m[2],cmd)
    elif ln.startswith('BATCH') or 'Error' in ln: print(ln)
