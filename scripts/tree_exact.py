"""Exact minimum formula size (tree) for all functions of n <= 4.

Model: AIG over U2 -- 2-input AND gates, inversions free on every edge and on the output.
A formula is a circuit with every gate at fan-out 1; inputs may be reused.

Exact because in a minimum formula the two subformulas are structurally independent: a minimum
formula of size k is (a AND b) with subformulas of sizes i + j = k - 1, each minimum for its own
function. Levels are complement-closed, which is what makes inversions free.

Replaces the field tree_ub, which was min over f = AND(a, b) of [1 + opt(a) + opt(b)] evaluated
once against the exact opt table -- the DAG measure opt where the formula measure needs tree.
Iterating that recurrence to its fixed point gives tree; one step from opt gives neither.
See README.md.

Cross-checked against Cox and Healy (research.swtch.com/boolean): parity is 9 gates at n = 3,
15 at n = 4.

Usage: python scripts/tree_exact.py [--write]
"""

import json
import sys

import numpy as np

DATA = [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]


def tree_table(n):
    """tree(f) for every f on n variables, as a uint8 array indexed by truth table."""
    nf = 1 << (1 << n)
    mask = nf - 1
    lits = set()
    for v in range(n):
        t = 0
        for a in range(1 << n):
            if (a >> v) & 1:
                t |= 1 << a
        lits.add(t)
        lits.add((~t) & mask)

    inf = 255
    cost = np.full(nf, inf, dtype=np.uint8)
    cost[np.array(sorted(lits), dtype=np.uint32)] = 0
    levels = {0: np.flatnonzero(cost == 0).astype(np.uint32)}

    empty = np.zeros(0, dtype=np.uint32)
    k = 0
    limit = 1 << (n + 3)          # runaway backstop only
    while int((cost != inf).sum()) < nf:
        k += 1
        if k > limit:
            raise RuntimeError(f'no progress up to size {k}; {nf} functions not covered')
        found = []
        for i in range((k - 1) // 2 + 1):
            j = k - 1 - i
            a, b = levels.get(i, empty), levels.get(j, empty)
            if a.size == 0 or b.size == 0:
                continue
            chunk = max(1, 4_000_000 // max(1, b.size))
            for s in range(0, a.size, chunk):
                found.append(np.unique((a[s:s + chunk][:, None] & b[None, :]).ravel()))
        # An empty level is legitimate; size k+1 may still add something.
        if found:
            cand = np.unique(np.concatenate(found))
            cand = np.union1d(cand, (~cand) & mask).astype(np.uint32)
            cand = cand[cost[cand] == inf]
        else:
            cand = empty
        cost[cand] = k
        levels[k] = cand
    return cost


def parity(n):
    tt = 0
    for a in range(1 << n):
        if bin(a).count('1') & 1:
            tt |= 1 << a
    return tt


def main():
    write = '--write' in sys.argv
    status = {}
    tables = {n: tree_table(n) for n in (3, 4)}

    for n in (3, 4):
        got = int(tables[n][parity(n)])
        want = {3: 9, 4: 15}[n]
        assert got == want, f'parity-{n}: tree = {got}, Cox and Healy give {want}'
        print(f'cross-check: tree(parity-{n}) = {got}')

    for n, path in DATA:
        with open(path) as fh:
            data = json.load(fh)
        tree = tables[n]

        dist = {}
        regap = 0
        under = 0
        bad = 0
        for rec in data['functions']:
            t = int(tree[rec['tt']])
            g = t - rec['opt']
            if rec.get('tree', t) != t or rec['gap'] != g:
                bad += 1
            if rec['gap'] != g:
                regap += 1
            if rec.get('tree_ub', t) < t:
                under += 1
            new = {'tt': rec['tt'], 'opt': rec['opt'], 'tree': t, 'gap': g,
                   'n_essential': rec['n_essential'], 'npn_rep': rec['npn_rep']}
            rec.clear()
            rec.update(new)
            dist[g] = dist.get(g, 0) + 1
        data['gap_distribution'] = {str(g): dist[g] for g in sorted(dist)}

        print(f'n={n}: {len(data["functions"])} functions; {under} had a tree_ub below the '
              f'true formula size; {regap} gap values change')
        print(f'      gap distribution {data["gap_distribution"]}')

        if write:
            with open(path, 'w') as fh:
                json.dump(data, fh, indent=2)
            print(f'  wrote {path}')
        else:
            status[path] = bad

    if not write:
        if any(status.values()):
            print('\nMISMATCH: ' + ', '.join(f'{p}: {c}' for p, c in status.items() if c))
            sys.exit(1)
        print('\nshipped data matches; run with --write to regenerate')


if __name__ == '__main__':
    main()
