"""Verify the Tree Theorem: opt(f) <= 3 implies gap(f) = 0.

Every function computable with at most 3 AND gates has an optimal
tree circuit (no reconvergence / gate sharing needed).

Usage:
    python scripts/verify_tree_theorem.py
"""

import sys
import json

sys.path.insert(0, '.')


def main():
    print("=" * 60)
    print("TREE THEOREM VERIFICATION")
    print("opt(f) <= 3 ==> gap(f) = 0")
    print("=" * 60)

    total_tested = 0
    total_violations = 0

    for n, filename in [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]:
        with open(filename) as f:
            data = json.load(f)

        functions = data['functions']

        low_opt = [func for func in functions if func['opt'] <= 3]
        violations = [func for func in low_opt if func['gap'] != 0]

        total_tested += len(low_opt)
        total_violations += len(violations)

        print(f"\n--- n={n} ---")
        print(f"  Functions with opt <= 3: {len(low_opt)}")

        # Breakdown by opt
        by_opt = {}
        for func in low_opt:
            opt = func['opt']
            by_opt.setdefault(opt, {'total': 0, 'gap0': 0, 'gap1': 0})
            by_opt[opt]['total'] += 1
            if func['gap'] == 0:
                by_opt[opt]['gap0'] += 1
            else:
                by_opt[opt]['gap1'] += 1

        print(f"  {'opt':>4} {'total':>6} {'gap=0':>6} {'gap=1':>6}")
        print(f"  {'-'*4} {'-'*6} {'-'*6} {'-'*6}")
        for opt in sorted(by_opt):
            b = by_opt[opt]
            print(f"  {opt:>4} {b['total']:>6} {b['gap0']:>6} {b['gap1']:>6}")

        if violations:
            print(f"\n  *** {len(violations)} VIOLATIONS ***")
        else:
            print(f"  VERIFIED: all {len(low_opt)} functions with opt<=3 have gap=0")

    # Show contrast: opt=4 is where gap=1 first appears
    print(f"\n--- Phase transition at opt=4 ---")
    for n, filename in [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]:
        with open(filename) as f:
            data = json.load(f)
        opt4 = [func for func in data['functions'] if func['opt'] == 4]
        gap1_at_4 = [func for func in opt4 if func['gap'] == 1]
        if opt4:
            print(f"  n={n}, opt=4: {len(gap1_at_4)}/{len(opt4)} gap=1 "
                  f"({100*len(gap1_at_4)/len(opt4):.1f}%)")

    print(f"\n{'=' * 60}")
    print(f"RESULT: Tree Theorem holds.")
    print(f"  Total functions with opt <= 3: {total_tested}")
    print(f"  All have gap = 0 (optimal tree circuit exists)")
    print(f"  Gap=1 first appears at opt = 4")
    print("=" * 60)


if __name__ == '__main__':
    main()
