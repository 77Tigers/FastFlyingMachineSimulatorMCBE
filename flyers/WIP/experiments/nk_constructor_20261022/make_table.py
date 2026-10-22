import json, sqbuild
from concurrent.futures import ProcessPoolExecutor
def one(k):
    r = sqbuild.build(k); return k, r.params, max(r.size())
if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex:
        res = {str(k): p for k, p, _ in ex.map(one, range(3, 25))}
    json.dump(res, open('square_table.json', 'w'), indent=0); print(res)
