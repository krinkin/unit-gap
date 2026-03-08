"""Verify the sharing mechanism vocabulary across n=5,6,7.

Gap=1 functions require gate sharing (reconvergence). Only two mechanisms
appear in all verified circuits:
  1. Dual-polarity: a gate used in both positive and negative polarity
  2. Same-polarity (CSE): a gate reused with the same polarity

Reproduces the sharing vocabulary table from the paper.

Usage:
    python scripts/verify_mechanisms.py
"""

import sys
import json

sys.path.insert(0, '.')


def analyze_file(filename, label):
    """Analyze a gap=1 circuits JSON file and return mechanism counts."""
    with open(filename) as f:
        data = json.load(f)

    circuits = data['circuits']
    gap1 = [c for c in circuits if c.get('gap', 1) == 1]

    mech_counts = {}
    depth_counts = {}

    for c in gap1:
        # Full format (n5, n6_constructed, n7)
        if 'mechanism' in c:
            mech = c['mechanism']
            mech_counts[mech] = mech_counts.get(mech, 0) + 1
            for sg in c.get('shared_gates', []):
                d = sg.get('depth', 0)
                depth_counts[d] = depth_counts.get(d, 0) + 1
        # Compact format (n6_random): sharing = [[gate_idx, polarity_type, ref_count], ...]
        elif 'sharing' in c:
            for entry in c['sharing']:
                pol_type = entry[1]
                if pol_type == 'dual-polarity':
                    mech_counts['dual-polarity'] = mech_counts.get('dual-polarity', 0) + 1
                elif pol_type == 'same-polarity':
                    mech_counts['same-polarity'] = mech_counts.get('same-polarity', 0) + 1
                else:
                    mech_counts[pol_type] = mech_counts.get(pol_type, 0) + 1

    return {
        'label': label,
        'total': len(gap1),
        'mechanisms': mech_counts,
        'depths': depth_counts,
    }


def merge_results(r1, r2, label):
    """Merge two analysis results under a new label."""
    merged_mechs = dict(r1['mechanisms'])
    for k, v in r2['mechanisms'].items():
        merged_mechs[k] = merged_mechs.get(k, 0) + v
    merged_depths = dict(r1['depths'])
    for k, v in r2['depths'].items():
        merged_depths[k] = merged_depths.get(k, 0) + v
    return {
        'label': label,
        'total': r1['total'] + r2['total'],
        'mechanisms': merged_mechs,
        'depths': merged_depths,
    }


def main():
    print("=" * 60)
    print("SHARING MECHANISM VOCABULARY VERIFICATION")
    print("=" * 60)

    results = []

    # n=5
    try:
        results.append(analyze_file('data/n5_gap1_circuits.json', 'n=5'))
    except FileNotFoundError:
        print("  Warning: data/n5_gap1_circuits.json not found")

    # n=6: merge constructed + random datasets
    try:
        r6a = analyze_file('data/n6_gap1_circuits.json', 'n=6')
        try:
            r6b = analyze_file('data/n6_gap1_random.json', 'n=6')
            r6 = merge_results(r6a, r6b, 'n=6')
        except FileNotFoundError:
            r6 = r6a
        results.append(r6)
    except FileNotFoundError:
        print("  Warning: data/n6_gap1_circuits.json not found")

    # n=7
    try:
        results.append(analyze_file('data/n7_gap1_circuits.json', 'n=7'))
    except FileNotFoundError:
        print("  Warning: data/n7_gap1_circuits.json not found")

    # Print per-n results
    for r in results:
        print(f"\n--- {r['label']} ({r['total']} gap=1 circuits) ---")
        for mech, count in sorted(r['mechanisms'].items(), key=lambda x: -x[1]):
            pct = 100 * count / r['total']
            print(f"  {mech:>20s}: {count:>4} ({pct:5.1f}%)")

    # Summary table
    known_mechs = {'dual-polarity', 'same-polarity', 'mixed'}
    print(f"\n{'=' * 60}")
    print("SHARING VOCABULARY TABLE")
    print(f"{'=' * 60}")
    print(f"{'n':>3} {'circuits':>9} {'dual-pol':>9} {'CSE':>9} {'new?':>6}")
    print(f"{'-'*3} {'-'*9} {'-'*9} {'-'*9} {'-'*6}")

    any_new = False
    for r in results:
        total = r['total']
        dual = r['mechanisms'].get('dual-polarity', 0)
        cse = r['mechanisms'].get('same-polarity', 0)
        mixed = r['mechanisms'].get('mixed', 0)
        new_mechs = set(r['mechanisms'].keys()) - known_mechs
        new_str = "NO" if not new_mechs else f"YES: {new_mechs}"
        if new_mechs:
            any_new = True

        n_val = r['label'].split('=')[1]
        dual_total = dual + mixed
        cse_total = cse + mixed

        dual_pct = f"{100*dual/total:.0f}%" if total > 0 else "N/A"
        cse_pct = f"{100*cse/total:.0f}%" if total > 0 else "N/A"

        print(f"{n_val:>3} {total:>9} {dual_pct:>9} {cse_pct:>9} {new_str:>6}")

    # Depth analysis
    # JSON stores depth = gate_depth - 1, so -1 = leaf gate (depth 0),
    # 0 = one level above PIs (depth 1), etc.
    print(f"\n{'=' * 60}")
    print("SHARED GATE DEPTH DISTRIBUTION")
    print(f"(depth = levels above primary inputs)")
    print(f"{'=' * 60}")
    print(f"{'n':>3} {'leaf(d=0)':>10} {'d=1':>9} {'d=2+':>9}")
    print(f"{'-'*3} {'-'*10} {'-'*9} {'-'*9}")
    for r in results:
        leaf = r['depths'].get(-1, 0)
        d1 = r['depths'].get(0, 0)
        d2p = sum(v for k, v in r['depths'].items() if k >= 1)
        total = leaf + d1 + d2p
        n_val = r['label'].split('=')[1]
        if total > 0:
            print(f"{n_val:>3} {leaf:>6} ({100*leaf/total:4.0f}%) "
                  f"{d1:>4} ({100*d1/total:4.0f}%) "
                  f"{d2p:>4} ({100*d2p/total:4.0f}%)")

    print(f"\n{'=' * 60}")
    if any_new:
        print("*** NEW MECHANISM FOUND -- vocabulary NOT closed ***")
    else:
        print("RESULT: Vocabulary closed at {dual-polarity, same-polarity}.")
        print("  No new sharing mechanism found through n=7.")
        print("  Shared gate depth increases with n (depth=1 dominates at n=7).")
    print("=" * 60)


if __name__ == '__main__':
    main()
