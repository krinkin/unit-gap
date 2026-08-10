"""Report the distribution of gap(f) = tree(f) - opt(f), and exhibit the counterexamples.

This used to verify gap in {0, 1}. That is false; it only appeared to hold because the data
carried tree_ub rather than tree. See README.md.

Usage:
    python scripts/verify_unit_gap.py
"""

import sys
import json

sys.path.insert(0, '.')


def main():
    print("=" * 60)
    print("GAP DISTRIBUTION")
    print("gap(f) := tree(f) - opt(f), tree = exact minimum formula size")
    print("=" * 60)

    worst = {}

    for n, filename in [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]:
        with open(filename) as f:
            data = json.load(f)

        functions = data['functions']
        total = len(functions)

        gap_counts = {}
        for func in functions:
            g = func['gap']
            gap_counts[g] = gap_counts.get(g, 0) + 1

        max_gap = max(gap_counts)
        worst[n] = max_gap

        scope = "non-trivial functions" if n == 3 else "functions, opt <= 6"
        print(f"\n--- n={n} ({total} {scope}) ---")
        print(f"{'gap':>5} {'count':>8} {'fraction':>10}")
        print(f"{'-'*5} {'-'*8} {'-'*10}")
        for g in sorted(gap_counts):
            print(f"{g:>5} {gap_counts[g]:>8} {gap_counts[g]/total:>10.1%}")

        gaps = sorted(gap_counts)
        gap_by_opt = {}
        for func in functions:
            gap_by_opt.setdefault(func['opt'], {})
            gap_by_opt[func['opt']][func['gap']] = \
                gap_by_opt[func['opt']].get(func['gap'], 0) + 1

        head = ' '.join(f"{'gap=' + str(g):>7}" for g in gaps)
        print(f"\n  {'opt':>4} {head} {'%gap>=2':>8}")
        print(f"  {'-'*4} {' '.join('-'*7 for _ in gaps)} {'-'*8}")
        for opt in sorted(gap_by_opt):
            row = gap_by_opt[opt]
            tot = sum(row.values())
            big = sum(c for g, c in row.items() if g >= 2)
            cells = ' '.join(f"{row.get(g, 0):>7}" for g in gaps)
            print(f"  {opt:>4} {cells} {100*big/tot:>7.1f}%")

        violations = [f for f in functions if f['gap'] > 1]
        if violations:
            smallest = min(violations, key=lambda f: (f['opt'], f['tt']))
            width = 2 if n == 3 else 4
            print(f"\n  gap > 1 for {len(violations)} of {total} functions; max gap = {max_gap}")
            print(f"  smallest counterexample: tt=0x{smallest['tt']:0{width}x} "
                  f"opt={smallest['opt']} tree={smallest['tree']} gap={smallest['gap']}")
        else:
            print(f"\n  max gap = {max_gap}")

    print(f"\n{'=' * 60}")
    print("RESULT: the Unit Gap Theorem is FALSE.")
    print(f"  n=3: 248 functions, max gap = {worst[3]} (3-variable parity, opt 6, tree 9)")
    print(f"  n=4: 20,660 functions of opt <= 6, max gap = {worst[4]} over that subset;")
    print("       over all 65,536 the gap reaches 6 (parity-4: opt 9, tree 15)")
    print("  Counterexample and certificates: L. A. Busnello,")
    print("  doi:10.5281/zenodo.21630762. The paper is withdrawn (arXiv:2603.08033v4).")
    print("=" * 60)


if __name__ == '__main__':
    main()
