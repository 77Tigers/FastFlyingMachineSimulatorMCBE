"""compare the terrace 'cp' strip with 'cp2' (beside covers for floor 1) at each k's current word: python terr_cp2_test.py K,K"""
import sys, json, time
import families as F, terrace

def ring(k, word, pattern):
    g, gap, cv, box, pat = F.terrace_params(k, word)
    r = terrace.build(k, g, gap, cv, box, pattern=pattern)
    if r is None: return None, 'none'
    if terrace.collisions(r, bodies=list(range(min(r.T.L, 2 * (r.T.L // 4) + 4)))): return None, 'coll'
    try: terrace.route_all(r)
    except RuntimeError: return None, 'route'
    L = r.T.L; m = L // 4
    bad = r.check(sorted({(X + d) % L for X in (0, 1, m) for d in range(-2, 3)}))
    if bad: return None, 'check ' + bad[0][2][:30]
    return r, 'ok'

if __name__ == '__main__':
    bits = json.load(open('bits.json'))
    for k in [int(x) for x in sys.argv[1].split(',')]:
        w = bits[str(k)]
        if F.fam_of(w) != 'terrace': print(k, 'not terrace'); continue
        out = []
        for pat in ('cp', 'cp2'):
            t = time.time(); r, why = ring(k, w, pat)
            out.append((pat, F.predicted_pl(r) if r else why, round(time.time() - t, 1)))
            if r and pat == 'cp2': r.flyer(F.predicted_pl(r)).save(f'out/terr_cp2_{k}.flyer')
        print(k, F.terrace_params(k, w)[4], out, flush=True)
