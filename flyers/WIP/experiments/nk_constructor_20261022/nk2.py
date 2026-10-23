"""nk2: the nk ring model generalised to any body graph (tower segments etc.).
- Timing2: every body has its own rest slot r (rests r, r+1) and a hopper carrier nxt[i] that must rest at r+2.
- Ring2: modules may carry rigid pistons 'RIG': list of dict(pos=(x, y, z), dir=+1 (pusher) or -1 (sticky), victim=Y).
  A rigid piston rides its host H and fires in H's rest: a pusher extends at H-local 0 (victim Y moves then) and
  retracts at H-local 1; a sticky extends empty at H-local 0 and pulls Y at H-local 1 (Y's last move before its rest).
  Contacts (next body's cover) come from every body whose carrier is X, not only the ring predecessor.
Power is not modelled here (redstone blocks are placed by the builder); every flyer is verified by simulation."""
from collections import defaultdict
from nk import Timing, Ring, D6, add


class _View:
    """read-only view of a slot world without rigid pistons and their arms (for the base checker)"""
    __slots__ = ('occ',)
    def __init__(self, occ): self.occ = occ
    def get(self, c, default=None):
        lst = self.occ.get(c)
        if not lst: return default if default is not None else []
        return [e for e in lst if e[1] != 'RIG' and not (e[1] == 'arm' and isinstance(e[2], tuple))]


class Timing2(Timing):
    def __init__(self, k, rests, nxt):
        self.k, self.S = k, k + 2
        self.L = len(rests)
        self.rest = list(rests)
        self._nxt = list(nxt)
        self._prv = defaultdict(list)
        for i, j in enumerate(nxt):
            if j is not None:
                assert (rests[j] - rests[i]) % self.S == 2, (i, j)
                self._prv[j].append(i)
        self._shift = [[0] * (2 * self.S + 1) for _ in range(self.L)]
        for i in range(self.L):
            for s in range(2 * self.S):
                self._shift[i][s + 1] = self._shift[i][s] + (1 if self.moves(i, s) else 0)

    def nxt(self, i): return self._nxt[i]
    def carried_by_me(self, j): return self._prv[j]


class Ring2(Ring):
    def __init__(self, T, mods, place, mat=None, extra=None):
        self.T, self.mods, self.place = T, mods, place
        L = T.L
        self.mat = mat or ['slime' if i % 2 == 0 else 'honey' for i in range(L)]
        self.extra = extra or [set() for _ in range(L)]
        self.plates, self.contacts = [set() for _ in range(L)], [set() for _ in range(L)]
        for X in range(L):
            for c in mods[X]['PLATE']: self.plates[X].add(self.mw(X, c, 0, X))
        for U in range(L):
            W = T.nxt(U)
            if W is None: continue
            for c in mods[U]['CONT']: self.contacts[W].add(self.cw(U, c))
        self.glue = [self.plates[X] | self.contacts[X] | set(self.extra[X]) for X in range(L)]

    # rigid piston state at host-local slot m: (state, arm offset or None)
    @staticmethod
    def rig_state(m): return (2, True) if m == 1 else (0, False)

    def hw(self, X, s, canon=False):
        key = (X, s, canon)
        cache = self.__dict__.setdefault('_hw', {})
        if key in cache: return cache[key]
        out = list(Ring.hw(self, X, s, canon))
        m = self.T.local(X, s)
        for i, rp in enumerate(self.mods[X].get('RIG', [])):
            st, arm = self.rig_state(m)
            w = self.mw(X, rp['pos'], s)
            out.append((w, (X, 'RIG', (i, st, rp['dir'], rp['victim']))))
            if arm: out.append(((w[0] + rp['dir'], w[1], w[2]), (X, 'arm', ('rig', i))))
        cache[key] = out
        return out

    def rig_role(self, Q, info, X, s):
        """is X the victim of Q's rigid piston `info` acting in slot s ('push' at Q-local 0, 'pull' at Q-local 1)?"""
        i, st, d, victim = info
        if victim != X: return None
        m = self.T.local(Q, s)
        if d > 0 and m == 0: return 'push'
        if d < 0 and m == 1: return 'pull'
        return None

    def cell_ok(self, X, g, worlds, why=False, strict=None):
        if strict is None: strict = self.STRICT
        T = self.T
        def bad(msg): return (False, msg) if why else False
        # rigid-piston rules first, then the base rules with rigid entries hidden
        for s in range(T.S):
            occ = worlds[s]
            w = (g[0] + T.shift(X, s), g[1], g[2])
            mX = T.moves(X, s)
            for d in D6:
                n = add(w, d)
                for Q, kind, info in occ.get(n, []):
                    if Q == X or kind not in ('RIG',): continue
                    mQ = T.moves(Q, s)
                    role = self.rig_role(Q, info, X, s)
                    if mX and not mQ and role is None: return bad(f's{s} drags {Q} rigid piston')
            if mX:
                dst = add(w, (1, 0, 0))
                for Q, kind, info in occ.get(dst, []):
                    if Q != X and kind == 'RIG': return bad(f's{s} moves into {Q} rigid piston')
        hidden = [_View(occ) for occ in worlds]
        # a sticky's arm in front of the glue it pulls is removed before the pull; other arms stay obstacles
        for s in range(T.S):
            occ = worlds[s]
            w = (g[0] + T.shift(X, s), g[1], g[2])
            if not T.moves(X, s): continue
            dst = add(w, (1, 0, 0))
            for Q, kind, info in occ.get(dst, []):
                if kind == 'arm' and isinstance(info, tuple) and Q != X:
                    rp = self.mods[Q]['RIG'][info[1]]
                    if not (rp['dir'] < 0 and rp['victim'] == X and T.local(Q, s) == 1):
                        return bad(f's{s} moves into {Q} rigid arm')
        return Ring.cell_ok(self, X, g, hidden, why, strict)

    def flyer(self, pl):
        from fastflyer import Flyer, Block, Kind
        fl = Flyer(push_limit=pl)
        mats = {'slime': Kind.SLIME, 'honey': Kind.HONEY}
        for c, lst in self.world(0, canon=True).items():
            assert len(lst) == 1, (c, lst)
            X, kind, info = lst[0]
            if kind == 'g': fl.set(c, Block(mats[self.mat[X]]))
            elif kind == 'RB': fl.set(c, Block(Kind.REDSTONE_BLOCK))
            elif kind == 'arm': fl.set(c, Block(Kind.PISTON_ARM))
            elif kind == 'RIG':
                i, st, d, victim = info
                fl.set(c, Block.piston(0 if d > 0 else 1, state=st, sticky=d < 0))
            else: fl.set(c, Block.piston(0, state=info[1]))
        return fl

    def size(self):
        return [len(self.glue[X]) + len(self.mods[X]['R']) for X in range(self.T.L)]

    def load_riders(self, X):
        """rigid pistons hosted by X (they ride X in every move)"""
        return len(self.mods[X].get('RIG', []))


def power_problems(r, bodies=None):
    """redstone blocks next to pistons at slot starts (face-adjacent, not in front of the piston):
    - a hopper may only be powered by its own body's blocks;
    - a sticky (rigid, dir -1) must be powered exactly at its host's local slot 0 and never by its own host."""
    T = r.T; out = []
    for s in range(T.S):
        occ = r.world(s, canon=False)
        rbs = [(c, e[0]) for c, lst in occ.items() for e in lst if e[1] == 'RB']
        for c, X in rbs:
            for d in D6:
                n = add(c, d)
                for Q, kind, info in occ.get(n, []):
                    if kind == 'P':
                        if Q != X and info[1] == 0 and n[0] - c[0] != 1:   # RB not directly in front
                            out.append((s, 'foreign RB powers hopper', X, Q, n))
                    elif kind == 'RIG':
                        i, st, dr, victim = info
                        front = (n[0] + dr, n[1], n[2])
                        if front == c: continue
                        m = T.local(Q, s)
                        if Q == X: out.append((s, 'own RB powers rigid piston', X, Q, n))
                        elif m != 0: out.append((s, f'rigid piston powered at local {m}', X, Q, n))
        # stickies that need power at local 0 but get none
        for c, lst in occ.items():
            for Q, kind, info in lst:
                if kind == 'RIG' and T.local(Q, s) == 0:
                    i, st, dr, victim = info
                    front = (c[0] + dr, c[1], c[2])
                    if not any(e[1] == 'RB' and e[0] != Q for d in D6 if add(c, d) != front for e in occ.get(add(c, d), [])):
                        out.append((s, 'rigid piston unpowered at local 0', None, Q, c))
    return out
