"""N_k back-link interfaces in the extension bank (flyers/extension_bank/nk_links/links.json).
A link = one back body's module (hopper lanes P, redstone blocks R, plate cells, the next body's cover cells CONT, in
nk.py's module frame) plus the straight step to the next body. The tower family looks links up by hopper count n.
Rederive / add: python bank_links.py N K [LAT MINSTEP]  (link0 screen; keeps the best few by back-ring max and sum).
Lookup: links(n) -> list of dict(name, mod, step, back_max, back_sum, k, lateral, source), in insertion order
(a k's word stores an index into this list, so entries are only ever appended)."""
import sys, json, pathlib
BANK = pathlib.Path(__file__).resolve().parents[3] / 'extension_bank' / 'nk_links' / 'links.json'


def load():
    return json.loads(BANK.read_text()) if BANK.exists() else {}


def links(n):
    out = []
    for e in load().get(str(n), []):
        m = e['mod']
        mod = dict(P=[tuple(c) for c in m['P']], R=[tuple(c) for c in m['R']], PLATE=[tuple(c) for c in m['PLATE']],
                   CONT=[tuple(c) for c in m['CONT']], size=tuple(m['size']))
        out.append(dict(e, mod=mod, step=tuple(e['step'])))
    return out


def save(n, entries):
    data = load(); data[str(n)] = entries
    BANK.parent.mkdir(parents=True, exist_ok=True)
    BANK.write_text(json.dumps(data, indent=1))


def add(n, name, mod, step, back_max, back_sum, k, lateral, source):
    data = load(); lst = [e for e in data.get(str(n), []) if e['name'] != name]
    lst.append(dict(name=name, mod={kk: [list(c) for c in v] if isinstance(v, list) else list(v) for kk, v in mod.items()},
                    step=list(step), back_max=back_max, back_sum=back_sum, k=k, lateral=lateral, source=source))
    data[str(n)] = lst
    BANK.parent.mkdir(parents=True, exist_ok=True)
    BANK.write_text(json.dumps(data, indent=1))


if __name__ == '__main__':
    import link0, link0_screen
    n, k = int(sys.argv[1]), int(sys.argv[2])
    lat = int(sys.argv[3]) if len(sys.argv) > 3 else 0; minstep = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    L = list(link0.links(n, lat=lat, minstep=minstep))
    q = [link0_screen.quick((k, mod, step)) for mod, step, c in L]
    cand = sorted([(qq, i) for i, qq in enumerate(q) if qq])[:10]
    for (_, i) in cand:
        f = link0.evaluate(k, L[i][0], L[i][1])
        if f: add(n, f'link0_n{n}_lat{lat}_{i}', L[i][0], L[i][1], f[0], f[1], k, lat, f'link0.links({n}, lat={lat}) #{i}')
    print(json.dumps([(e['name'], e['back_max'], e['step']) for e in load()[str(n)]]))
