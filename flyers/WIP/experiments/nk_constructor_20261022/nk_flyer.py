"""The N_k constructor: python nk_flyer.py K [OUT.flyer]
Builds the square-ring N_k flyer (cycle 2(k+2) ticks, +k) from square_table.json and saves it with its push limit
set to the predicted minimum (largest body + k).  Prints the body count, predicted PL and build time."""
import sys, json, time, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sqbuild


def build(k):
    """joint-CP square ring if joint_table.json has k (and it is better), else the square_table.json ring."""
    table = json.load(open(HERE / 'square_table.json'))
    ring = sqbuild.build_fast(k, table)
    jt = HERE / 'joint_table.json'
    if jt.exists():
        jtab = json.load(open(jt))
        if str(k) in jtab and jtab[str(k)][0] < max(ring.size()):
            import joint_build
            res = json.load(open(HERE / 'modules_joint.json'))[str(k)]
            ring = joint_build.build(k, res, jtab[str(k)][1])
    return ring, max(ring.size()) + k


if __name__ == '__main__':
    k = int(sys.argv[1])
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'out' / f'n{k}.flyer'
    t = time.time(); ring, pl = build(k); dt = time.time() - t
    out.parent.mkdir(exist_ok=True); ring.flyer(pl).save(str(out))
    print(f'N{k}: {ring.T.L} bodies, predicted PL {pl}, built in {dt:.2f}s -> {out}')
