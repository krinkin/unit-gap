# Unit Gap Theorem for Boolean Circuit Complexity

> ## Correction, 2026-08-10: the Unit Gap Theorem is false
>
> `opt` = 6 and `tree` = 9 for 3-variable parity, a gap of 3. Counterexample, diagnosis and
> machine-checked certificates: **L. A. Busnello**,
> [doi:10.5281/zenodo.21630762](https://doi.org/10.5281/zenodo.21630762). The paper is withdrawn
> ([arXiv:2603.08033v4](https://arxiv.org/abs/2603.08033v4); notice in v3).
>
> The error was reproduced in this repository's data. The files carried `tree_ub`, the value of
> `min over f = AND(a, b) of [1 + opt(a) + opt(b)]` evaluated once against the exact `opt` table
> -- the DAG measure `opt` in the children where the formula measure needs `tree`. Iterating that
> recurrence to its fixed point gives `tree`; one step from `opt` gives neither, because once
> gates are shared an optimum for the whole does not restrict to optima on its parts. The values
> sat *below* the true formula size for 2296 of the 20660 records at n = 4 and 18 of the 248 at
> n = 3, so on those records it was not an upper bound at all, and the apparent verification of
> `gap <= 1` was an artefact of the field. The files now carry the exact `tree` from
> `scripts/tree_exact.py`:
>
> | | old `gap` | corrected `gap` |
> |---|---|---|
> | n = 3, 248 functions | 0: 222, 1: 26 | 0: 206, 1: 40, **3: 2** |
> | n = 4, the 20660 functions with opt <= 6 | 0: 17564, 1: 3096 | 0: 15772, 1: 4384, **2: 352, 3: 152** |
>
> The two n = 3 records at gap 3 are 3-variable parity and its complement -- the counterexample,
> mislabelled as gap 1 in this repository all along.
>
> The n = 4 file holds only the 20660 functions of opt <= 6, 31.5% of the 65536, and that is
> where the gaps are smallest. Over all four-variable functions the gap reaches 6: parity-4 has
> opt 9 and tree 15. The maximum of 3 below is an artefact of the truncation, not the truth.
>
> The Threshold Law and the Tree Theorem still verify against the corrected data. The n = 5, 6, 7
> mechanism catalogue does not; `data/README.md` marks those files.

This repository contains code and data on the relation between minimum circuit size `opt(f)` and
minimum formula size `tree(f)` in the AND-Inverter Graph basis (2-input AND gates, inversions
free on every edge and on the output; a formula is a circuit in which every gate has fan-out
exactly 1). `gap(f) = tree(f) - opt(f)`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires Python 3.10+. External dependencies: [python-sat](https://pysathq.github.io/) (used by
the data generation script) and numpy (used by `scripts/tree_exact.py`). The verify scripts need
only the standard library.

## Verification scripts

All scripts should be run from the repository root.

### 1. Gap distribution

```bash
python scripts/verify_unit_gap.py
```

Reports the gap distribution for the 248 three-variable functions and the 20,660 four-variable
functions of opt <= 6, and exhibits the counterexamples to `gap <= 1`:

```
--- n=3 (248 non-trivial functions) ---
  gap    count   fraction
    0      206      83.1%
    1       40      16.1%
    3        2       0.8%

--- n=4 (20660 functions, opt <= 6) ---
  gap    count   fraction
    0    15772      76.3%
    1     4384      21.2%
    2      352       1.7%
    3      152       0.7%

  gap > 1 for 504 of 20660 functions; max gap = 3
  smallest counterexample: tt=0x01fe opt=5 tree=7 gap=2
```

### 2. Threshold Law

```bash
python scripts/verify_threshold.py
```

Verifies that `gap(f) >= 1` implies `opt(f) >= n_essential(f)`: 4,930 functions across n = 3 and
n = 4, 0 violations. Checked for `gap >= 1` rather than `gap = 1`; the incidence argument in
[`docs/threshold_law_proof.md`](docs/threshold_law_proof.md) only needs some optimum to be a
non-tree, and `gap = 1` would skip the functions of gap 2 and 3.

### 3. Tree Theorem

```bash
python scripts/verify_tree_theorem.py
```

Verifies that `opt <= 3` implies `gap = 0`: 1,362 functions, 0 violations. A positive gap first
appears at `opt = 4`.

### 4. Sharing mechanisms

```bash
python scripts/verify_mechanisms.py
```

Classifies the n = 5, 6 and 7 circuits by sharing mechanism. **Read with the caveat above**: that
population was selected under the old recurrence.

### 5. Exact formula size

```bash
python scripts/tree_exact.py            # recompute and check the shipped data
python scripts/tree_exact.py --write    # recompute and rewrite the two data files
```

Recomputes `tree` at n = 3 and n = 4 from scratch, compares with the shipped values and exits
non-zero on any mismatch. Asserts the two Cox and Healy cross-checks. About 20 seconds.

## Data files

See [`data/README.md`](data/README.md) for field descriptions and for which files are corrected.

| File | Description |
|------|-------------|
| `n3_complete.json` | All 248 non-trivial 3-input functions with opt, tree, gap |
| `n4_complete.json` | All 20,660 4-input functions (opt <= 6) with opt, tree, gap |
| `n5_gap1_circuits.json` | 31 circuits at n=5 with full structural analysis (not corrected) |
| `n6_gap1_circuits.json` | 6 constructed circuits at n=6 (not corrected) |
| `n6_gap1_random.json` | 159 randomly generated circuits at n=6 (not corrected) |
| `n7_gap1_circuits.json` | 60 circuits at n=7 (not corrected) |
| `npn4_classes.json` | NPN equivalence class sizes for 4-input functions (222 classes) |

## Source modules

| Module | Description |
|--------|-------------|
| `src/boolean_function.py` | Truth table representation of Boolean functions |
| `src/aig.py` | And-Inverter Graph data structure and standard constructions |
| `src/fast_synthesis.py` | Exact synthesis by gate-level enumeration (n <= 4) |
| `src/tropical.py` | The Bellman recurrence over disjoint children. Correct for `tree`, not for `opt`; see the correction above |
| `src/npn.py` | NPN equivalence classification |

## License

MIT. See [LICENSE](LICENSE).
