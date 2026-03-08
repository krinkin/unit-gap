# Unit Gap Theorem for Boolean Circuit Complexity

This repository contains code and data for verifying the **Unit Gap Theorem**: for any Boolean function *f* in the AND-Inverter Graph (AIG) basis, the gap between the tree upper bound and the optimal circuit size is at most 1. That is, `tree_UB(f) - opt(f) in {0, 1}`. The tree Bellman equation (minimizing `1 + opt(a) + opt(b)` over all AND/NAND decompositions `f = AND(a, b)`) is therefore a 1-additive approximation to exact circuit complexity. We also verify the Threshold Law (`gap = 1` implies `opt >= n` essential variables), the Tree Theorem (`opt <= 3` implies `gap = 0`), and catalog the sharing mechanisms that cause `gap = 1`, finding exactly two (dual-polarity and same-polarity/CSE) through `n = 7`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires Python 3.10+. The only external dependency is [python-sat](https://pysathq.github.io/) (used by the data generation script; the verify scripts need only the standard library).

## Verification scripts

All scripts should be run from the repository root.

### 1. Unit Gap Theorem

```bash
python scripts/verify_unit_gap.py
```

Verifies `gap in {0, 1}` for all 3-input (248) and 4-input (20,660) functions. Prints the gap distribution by optimal cost level:

```
--- n=3 (248 non-trivial functions) ---
  gap    count   fraction
    0      222      89.5%
    1       26      10.5%

--- n=4 (20660 non-trivial functions) ---
  gap    count   fraction
    0    17564      85.0%
    1     3096      15.0%
```

### 2. Threshold Law

```bash
python scripts/verify_threshold.py
```

Verifies that every gap=1 function satisfies `opt(f) >= n_essential(f)`. Tests 3,122 gap=1 functions across n=3 and n=4 with 0 violations.

### 3. Tree Theorem

```bash
python scripts/verify_tree_theorem.py
```

Verifies that `opt <= 3` implies `gap = 0` (optimal tree circuit exists). Tests 1,362 functions. Shows the phase transition: gap=1 first appears at `opt = 4`.

### 4. Sharing mechanisms

```bash
python scripts/verify_mechanisms.py
```

Classifies all gap=1 circuits from n=5, n=6, and n=7 by sharing mechanism. Finds exactly two mechanisms with no new type through n=7:

```
  n  circuits  dual-pol       CSE   new?
  5        31       52%       48%     NO
  6       165       67%       33%     NO
  7        60       92%        8%     NO
```

## Data files

See [`data/README.md`](data/README.md) for field descriptions.

| File | Description |
|------|-------------|
| `n3_complete.json` | All 248 non-trivial 3-input functions with opt, tree_UB, gap |
| `n4_complete.json` | All 20,660 4-input functions (opt <= 6) with opt, tree_UB, gap |
| `n5_gap1_circuits.json` | 31 gap=1 circuits at n=5 with full structural analysis |
| `n6_gap1_circuits.json` | 6 constructed gap=1 circuits at n=6 |
| `n6_gap1_random.json` | 159 randomly generated gap=1 circuits at n=6 |
| `n7_gap1_circuits.json` | 60 gap=1 circuits at n=7 |
| `npn4_classes.json` | NPN equivalence class sizes for 4-input functions (222 classes) |

## Source modules

| Module | Description |
|--------|-------------|
| `src/boolean_function.py` | Truth table representation of Boolean functions |
| `src/aig.py` | And-Inverter Graph data structure and standard constructions |
| `src/fast_synthesis.py` | Exact synthesis by gate-level enumeration (n <= 4) |
| `src/tropical.py` | Tropical Bellman equation: tree upper bounds, gap analysis, fixed-point convergence |
| `src/npn.py` | NPN equivalence classification |

## License

MIT. See [LICENSE](LICENSE).
