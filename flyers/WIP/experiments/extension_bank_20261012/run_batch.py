#!/usr/bin/env python3
"""Batch contract-search over contracts/<id>/ fixtures, then confirm finalists.

usage (repo root): python flyers/WIP/experiments/extension_bank_20261012/run_batch.py [--secs 240] [--only n2_01,n2_02] [--skip-search]
For every id: eval-only seed (endogenous max = reference), search with --target ref-1 (6 threads, SECS seconds),
write contracts/<id>/search/{summary.json,pareto_*.flyer,best.flyer,log.txt,confirm/,results.json}.
Recurrence for search: `advance` if the seed passes it, otherwise the contract's own (bounded, envelope from the contract).
Confirmation: Rust own-mode and advance, 80 samples, every applicable order; Python checker in the contract's own mode
(--samples), plus a tight-envelope bounded variant (finalist permanent bbox) for bounded contracts.
"""
import os as _research_os
import glob, hashlib, json, os, subprocess, sys, time

ROOT = os.getcwd()
EX = 'flyers/WIP/experiments/extension_bank_20261012'
CON = f'{EX}/contracts'
EXE = os.path.abspath(('target/release/contract-search' + ('.exe' if _research_os.name == 'nt' else '')))
BEFORE_ONLY = {'n2_04', 'n3_08', 'n3_09'}
DEFAULT_IDS = ['n2_01', 'n2_02', 'n2_03', 'n2_04', 'n2_05', 'n2_06', 'n3_07', 'n3_08', 'n3_09', 'n3_10', 'n3_11']

secs = 240
only = None
skip_search = False
sub = 'search'
extra_args = []
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == '--secs':
        secs = int(args[i + 1]); i += 1
    elif args[i] == '--only':
        only = args[i + 1].split(','); i += 1
    elif args[i] == '--sub':
        sub = args[i + 1]; i += 1
    elif args[i] == '--extra':
        extra_args = args[i + 1].split(); i += 1
    elif args[i] == '--skip-search':
        skip_search = True
    i += 1

sys.path.insert(0, '.')
from fastflyer import Flyer


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw).stdout.strip()


def evalonly(contract, order, extra=(), samples=False):
    cmd = [EXE, contract, '0', '1', 'x', '--eval-only', '--order', order, *extra]
    if samples:
        cmd.append('--samples')
    out = run(cmd)
    try:
        return json.loads(out)
    except Exception:
        return {'pass': False, 'first_failure': out[:200]}


def sha(path):
    return hashlib.sha1(open(path, 'rb').read()).hexdigest()


def rebased(base_path, flyer_abs, out_dir, extra=None):
    c = json.load(open(base_path))
    base_dir = os.path.dirname(os.path.abspath(base_path))
    c['flyer'] = os.path.relpath(flyer_abs, out_dir).replace('\\', '/')
    c['prescribed_script'] = os.path.relpath(os.path.join(base_dir, c['prescribed_script']), out_dir).replace('\\', '/')
    if extra:
        c.update(extra)
    return c


def confirm(cid, search_dir, orders):
    cdir = f'{CON}/{cid}'
    out = os.path.join(search_dir, 'confirm')
    os.makedirs(out, exist_ok=True)
    own = json.load(open(f'{cdir}/before_natural.json')).get('recurrence', 'exact')
    members = sorted(glob.glob(f'{search_dir}/pareto_*.flyer'))
    seen, flyers = set(), []
    for f in members + [f'{search_dir}/best.flyer']:
        if os.path.exists(f) and sha(f) not in seen:
            seen.add(sha(f)); flyers.append(f)
    seed_sha = sha(f'{cdir}/candidate.flyer')
    results = []
    for f in flyers:
        name = os.path.basename(f)[:-6]
        fl = Flyer.load(f)
        pos = [p for p, b in fl.blocks() if b.kind.name != 'PISTON_ARM']
        lo = [min(p[k] for p in pos) for k in range(3)]
        hi = [max(p[k] for p in pos) for k in range(3)]
        rec = {'file': os.path.basename(f), 'limit': fl.push_limit, 'blocks': len(pos), 'rust': {}, 'python': {}}
        for o in orders:
            cp = os.path.join(out, f'{name}_{o}_rust.json')
            json.dump(rebased(f'{cdir}/{o}_natural.json', os.path.abspath(f), out), open(cp, 'w'), indent=1)
            e = evalonly(cp, o, ['--recurrence', 'advance'])
            rec['rust'][f'{o}_advance_single'] = {k: e.get(k) for k in ('pass', 'max_load', 'all_max_load', 'count_at_max', 'max_prescribed_input_load', 'first_failure')}
            for label, extra in (('advance', ['--recurrence', 'advance']), (own, [])):
                e = evalonly(cp, o, extra, samples=True)
                rec['rust'][f'{o}_{label}_samples'] = f"{e.get('samples_passed')}/{e.get('samples_total')}" + ('' if e.get('pass') else ' FIRST FAIL ' + str(e.get('first_failure'))[:100])
            e = evalonly(cp, o, ['--recurrence', 'advance', '--cycles', '8'])
            rec['rust'][f'{o}_advance_8cycles'] = e.get('pass')
        # Python in the contract's own mode, plus tight envelope for bounded contracts
        variants = [('own', None)]
        if own == 'bounded':
            variants.append(('tight0', {'recurrence': 'bounded', 'boundary_envelope': {'min': lo, 'max': hi}}))
        for o in orders:
            for vname, extra in variants:
                c = rebased(f'{cdir}/{o}_natural.json', os.path.abspath(f), out, extra)
                c['name'] = f'{cid}-{name}-{o}-{vname}'
                cp = os.path.join(out, f'{name}_{o}_{vname}.json')
                json.dump(c, open(cp, 'w'), indent=1)
                single = run(['python', 'tools/extension_contract.py', cp])
                ok = ': PASS' in single
                entry = {'single': 'PASS' if ok else 'FAIL ' + single.split('—')[-1].strip()[:140]}
                if ok:
                    entry['samples'] = run(['python', 'tools/extension_contract.py', cp, '--samples']).split('(')[1].split(';')[0] if True else ''
                rec['python'][f'{o}_{vname}'] = entry
        rec['is_seed'] = (sha(f) == seed_sha)
        results.append(rec)
    return results


def main():
    ids = only or DEFAULT_IDS
    for extra_id in sorted(os.listdir(CON)):
        if extra_id.startswith('n4_') and extra_id not in ids and not only:
            notes = f'{CON}/{extra_id}/NOTES.md'
            if os.path.exists(notes) and 'PASS' in open(notes, encoding='utf-8').read():
                ids.append(extra_id)
    for cid in ids:
        cdir = f'{CON}/{cid}'
        sd = f'{cdir}/{sub}'
        orders = ['before'] if cid in BEFORE_ONLY else ['before', 'after']
        order_arg = 'before' if cid in BEFORE_ONLY else 'both'
        ofull = ['before'] if cid in BEFORE_ONLY else ['before', 'after']
        base = f'{cdir}/before_natural.json'
        own = json.load(open(base)).get('recurrence', 'exact')
        seed_own = evalonly(base, order_arg)
        seed_adv = evalonly(base, order_arg, ['--recurrence', 'advance'])
        mode = 'advance' if seed_adv.get('pass') else own
        ref = seed_own.get('max_load')
        info = {'id': cid, 'orders': order_arg, 'own_recurrence': own, 'search_recurrence': mode,
                'seed_own': seed_own, 'seed_advance': seed_adv, 'ref_endogenous_max': ref}
        print(f'== {cid}: ref endogenous {ref} (all {seed_own.get("all_max_load")}) own={own} advance_pass={seed_adv.get("pass")} -> search {mode}', flush=True)
        if not seed_own.get('pass'):
            print('   seed does not pass, skipping', flush=True)
            continue
        os.makedirs(sd, exist_ok=True)
        if not skip_search:
            for old in glob.glob(f'{sd}/pareto_*.flyer'):
                os.remove(old)
            t0 = time.time()
            cmd = [EXE, base, str(secs), '6', sd, '--target', str(max(ref - 1, 0)), '--order', order_arg,
                   '--recurrence', mode, '--seed', '1'] + extra_args
            with open(f'{sd}/log.txt', 'w') as lf:
                subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
            info['search_cmd'] = ' '.join(['contract-search', base, str(secs), '6', sd, '--target', str(max(ref - 1, 0)), '--order', order_arg, '--recurrence', mode, '--seed', '1'] + extra_args)
            print(f'   search done in {time.time() - t0:.0f}s', flush=True)
        try:
            info['summary'] = json.load(open(f'{sd}/summary.json'))
        except Exception as e:
            info['summary_error'] = str(e)
        info['confirm'] = confirm(cid, sd, [{'before': 'before', 'after': 'after'}[o] for o in ofull] if False else [o + '' for o in ofull])
        json.dump(info, open(f'{sd}/results.json', 'w'), indent=1)
        b = (info.get('summary') or {}).get('best') or {}
        print(f'   best: excess {b.get("excess")} end_max {b.get("max_load")} all_max {b.get("all_max_load")} count {b.get("count_at_max")} blocks {b.get("blocks")} diff {b.get("diff_vs_seed")}', flush=True)


main()
