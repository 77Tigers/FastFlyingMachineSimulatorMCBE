"""Enumerate zero-span end caps for the alternating rigid chain.

The chain continues to one side. Segment 'C0' is the last chain segment (M or W), 'C1' its chain neighbour,
whose other move is caused by the rest of the (infinite) chain. Cap segments 0..m-1 plus C0, C1.
Rear cap: chain continues forward from C1 (C1 is ahead of C0). C1's pull from ahead is external.
Front cap: chain continues backward from C1 (C1 behind C0). C1's push from behind is external.
Pistons per segment <= MAXP (C0, C1 count their chain pistons too).
Zero span: every segment's pistons and contacts share local x  => exact potentials.
Each action: push X->Y at k: c_Y + pos_Y(k) = c_X + pos_X(k) + 1 ; pull Z of Y at k: c_Z + pos_Z(k) = c_Y + pos_Y(k) + 2.
"""
import itertools, sys, os
from topo import contact_ok, pos, still
WORDS = [(0,1),(1,2),(2,3),(0,3)]
FREEW = [(0,1),(1,2),(2,3),(0,3),(0,2),(1,3)]
MAXP = int(os.environ.get('MAXP', '2'))
RELAX = int(os.environ.get('RELAX', '0'))

def consistent(n, words, acts):
    adj = {i: [] for i in range(n)}
    for typ, a, t, k in acts:
        d = (pos(words[a], k) - pos(words[t], k) + 1) if typ == 'push' else (pos(words[a], k) - pos(words[t], k) - 2)
        adj[a].append((t, d)); adj[t].append((a, -d))   # c_t - c_a = d
    c = {}
    for s0 in range(n):
        if s0 in c: continue
        c[s0] = 0; st = [s0]
        while st:
            x = st.pop()
            for y, d in adj[x]:
                if y not in c: c[y] = c[x] + d; st.append(y)
                elif c[y] != c[x] + d: return False
    return True

def run(m, side, c0phase):
    n = m + 2; C0, C1 = m, m+1
    w0 = (0,1) if c0phase == 'M' else (2,3); w1 = (2,3) if c0phase == 'M' else (0,1)
    results = []
    for cw in itertools.product(FREEW, repeat=m):
        words = list(cw) + [w0, w1]
        # required moves: all cap segs both moves; C0 both moves; C1: one move from C0-side:
        #  rear cap: C1 is ahead of C0: C1 gets push from C0 (its first move), pull from ahead external.
        #  front cap: C1 behind C0: C1 gets pull from C0 (second move), push from behind external.
        need = []
        for t in range(m + 1):
            for k in words[t]: need.append((t, k))
        k1 = words[C1][0] if side == 'rear' else words[C1][1]
        need.append((C1, k1))
        opts = []
        for (t, k) in need:
            o = []
            for a in range(n):
                if a == t: continue
                if still(words[a], (k, k+1)) and words[a] in WORDS: o.append(('push', a, t, k))
                if still(words[a], (k-1, k)) and words[a] in WORDS: o.append(('pull', a, t, k))
            if side == 'rear' and t == C1: o = [x for x in o if x[1] == C0 and x[0] == 'push']
            if side == 'front' and t == C1: o = [x for x in o if x[1] == C0 and x[0] == 'pull']
            opts.append(o)
        # external pistons: C1 carries its chain piston toward the continuing chain (1), C0 none extra
        base_pc = [0]*n; base_pc[C1] = 1
        def rec(i, cur, pc):
            if i == len(opts):
                yield tuple(cur); return
            for o in opts[i]:
                if pc[o[1]] >= MAXP: continue
                pc[o[1]] += 1; cur.append(o)
                yield from rec(i+1, cur, pc)
                cur.pop(); pc[o[1]] -= 1
        for acts in rec(0, [], list(base_pc)):
            if not contact_ok(words, acts): continue
            if not consistent(n, words, acts):
                if not RELAX: continue
                from topo import solve
                sp = solve(n, words, acts)
                if sp is None or sp[0] > RELAX: continue
            else: sp = (0, 0, ())
            # every cap segment must be connected to chain (implied by causes) ; record
            pc = [sum(1 for x in acts if x[1] == i) + base_pc[i] for i in range(n)]
            results.append((words, acts, pc, sp))
    return results

if __name__ == '__main__':
    m = int(sys.argv[1]); side = sys.argv[2]; ph = sys.argv[3]
    res = run(m, side, ph)
    print(len(res), 'zero-span caps')
    res.sort(key=lambda r: (r[3][0], r[3][1], max(r[2])))
    for w, a, pc, sp in res[:12]: print(w, a, 'pistons', pc, 'span', sp)
