"""Enumerate two open-plus cores sharing two hopper power blocks at the same phase."""

from itertools import combinations, product

D = {(1, 0), (-1, 0), (0, 1), (0, -1)}


def plus(a, b):
    return tuple(x + y for x, y in zip(a, b))


def around(p):
    return {plus(p, d) for d in D}


def pairs():
    a = D - {(1, 0)}
    for y, z, missing in product(range(-4, 5), range(-4, 5), D):
        s = (y, z)
        b = around(s) - {plus(s, missing)}
        if s in a or (0, 0) in b or (a & b) or s == (0, 0):
            continue
        ports = a | b
        allowed = set.union(*(around(p) for p in ports)) - ports - {s, (0, 0)}
        for rr in combinations(sorted(allowed), 2):
            if ports <= around(rr[0]) | around(rr[1]):
                yield (y, z, missing, rr)


if __name__ == "__main__":
    result = list(pairs())
    print(len(result))
    print(*result[:16], sep="\n")
