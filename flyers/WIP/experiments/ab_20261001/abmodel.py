"""Lifecycle model for A/B pair flyers (A_i honey pulled only, B_i slime pushed only; A_i,B_i share word i).

Pistons: push P on B_m at slot s (fires s, frozen s,s+1); pull Q on A_m at slot s (extends s-1, frozen s-1,s).
Every piston moves +1 in each non-frozen slot (needed for speed when L - D == 2).
Contact (b, r): glue of body b on a lateral line of the piston at b-frame x = piston_x - r ... we store
r = rel offset value piston_x(k) - b_x(k); the contact touches at slot starts k where rel_b(k) == r.
"""
import itertools


class Model:
    def __init__(self, words):
        self.words = [tuple(1 if c == 'm' else 0 for c in w) for w in words]
        self.L = len(self.words[0])
        self.D = sum(self.words[0])
        self.bodies = []
        for i in range(len(words)):
            self.bodies += [('A', i), ('B', i)]
        self.off = {}
        for b in self.bodies:
            w = self.words[b[1]]
            o = [0]
            for k in range(self.L):
                o.append(o[-1] + w[k])
            self.off[b] = o  # o[k] = offset at start of slot k (k=0..L)
        self.pistons = []
        for s in range(self.L):
            rest = [i for i, w in enumerate(self.words) if not w[s]]
            for m, w in enumerate(self.words):
                if not w[s]: continue
                self.pistons.append(dict(kind='P', s=s, f=s, victim=('B', m), anchors=[('A', r) for r in rest]))
                self.pistons.append(dict(kind='Q', s=s, f=(s - 1) % self.L, victim=('A', m), anchors=[('B', r) for r in rest if True]))
        for p in self.pistons:
            p['frozen'] = {p['f'], (p['f'] + 1) % self.L}
            # trajectory: position at slot starts relative to f (x=0 at start of f), k = f..f+L
            x = [0]
            for j in range(self.L):
                k = (p['f'] + j) % self.L
                x.append(x[-1] + (0 if k in p['frozen'] else 1))
            assert x[-1] == self.D, x
            p['x'] = x  # p['x'][j] at start of slot f+j

    def moving(self, b, k):
        return bool(self.words[b[1]][k % self.L])

    def boff(self, b, k):
        # offset of body b at start of absolute slot k (k may exceed L)
        L = self.L
        return self.off[b][k % L] + (k // L) * self.D

    def rel(self, p, b):
        """rel[j] = piston_x - body_x at start of slot f+j, j=0..L-1."""
        f = p['f']
        return [p['x'][j] - (self.boff(b, f + j) - self.boff(b, f)) for j in range(self.L)]

    def describe(self):
        for p in self.pistons:
            print(p['kind'], 's', p['s'], 'f', p['f'], 'victim', p['victim'], 'anchors', p['anchors'], 'x', p['x'])
            for b in self.bodies:
                r = self.rel(p, b)
                mv = ''.join('M' if self.moving(b, p['f'] + j) else '.' for j in range(self.L))
                print('   ', b, 'rel', r, 'mov', mv)


if __name__ == '__main__':
    import sys
    Model(sys.argv[1].split(',')).describe()
