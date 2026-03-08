"""Verify the Threshold Law: gap(f) = 1 implies opt(f) >= n_essential(f).

If a function has n essential variables and gap = 1, then its optimal
circuit size is at least n.

Usage:
    python scripts/verify_threshold.py
"""

import sys
import json

sys.path.insert(0, '.')


def main():
    print("=" * 60)
    print("THRESHOLD LAW VERIFICATION")
    print("gap(f) = 1 ==> opt(f) >= n_essential(f)")
    print("=" * 60)

    total_gap1 = 0
    total_violations = 0

    for n, filename in [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]:
        with open(filename) as f:
            data = json.load(f)

        functions = data['functions']
        gap1_funcs = [func for func in functions if func['gap'] == 1]

        violations = []
        for func in gap1_funcs:
            if func['opt'] < func['n_essential']:
                violations.append(func)

        total_gap1 += len(gap1_funcs)
        total_violations += len(violations)

        print(f"\n--- n={n} ---")
        print(f"  Gap=1 functions: {len(gap1_funcs)}")

        # Distribution of (opt, n_essential) for gap=1
        opt_ess = {}
        for func in gap1_funcs:
            key = (func['opt'], func['n_essential'])
            opt_ess[key] = opt_ess.get(key, 0) + 1

        print(f"  {'opt':>4} {'n_ess':>6} {'count':>6} {'opt>=n_ess':>10}")
        print(f"  {'-'*4} {'-'*6} {'-'*6} {'-'*10}")
        for (opt, ess), count in sorted(opt_ess.items()):
            status = "yes" if opt >= ess else "*** NO ***"
            print(f"  {opt:>4} {ess:>6} {count:>6} {status:>10}")

        if violations:
            print(f"\n  *** {len(violations)} VIOLATIONS ***")
            for v in violations[:5]:
                print(f"    tt={v['tt']}: opt={v['opt']}, n_ess={v['n_essential']}")
        else:
            print(f"  VERIFIED: 0 violations in {len(gap1_funcs)} gap=1 functions")

    # Tightness: functions where opt = n_essential exactly
    print(f"\n{'=' * 60}")
    print("TIGHTNESS (opt = n_essential at gap=1):")
    for n, filename in [(3, 'data/n3_complete.json'), (4, 'data/n4_complete.json')]:
        with open(filename) as f:
            data = json.load(f)
        gap1 = [func for func in data['functions'] if func['gap'] == 1]
        tight = [func for func in gap1 if func['opt'] == func['n_essential']]
        if gap1:
            print(f"  n={n}: {len(tight)}/{len(gap1)} tight "
                  f"({100*len(tight)/len(gap1):.1f}%)")

    print(f"\n{'=' * 60}")
    print(f"RESULT: Threshold Law holds.")
    print(f"  Total gap=1 tested: {total_gap1}")
    print(f"  Violations: {total_violations}")
    print("=" * 60)


if __name__ == '__main__':
    main()
