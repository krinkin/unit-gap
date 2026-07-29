# The Threshold Law: a proof by incidence counting

`scripts/verify_threshold.py` checks the Threshold Law empirically on 3,122 functions.
This note gives the argument behind it.

## Statement

> **Claim.** If `f` has `n` essential variables and `gap(f) = 1`, then `opt(f) = m >= n`.

The proof below establishes something slightly stronger, which is worth stating separately
because it does not mention the gap at all:

> **Claim'.** If `C` is a size-optimal single-output AIG for `f`, `f` has `n` essential
> variables, and `C` is not a tree, then `|C| >= n`.

The Threshold Law follows: `gap(f) = 1` forces any optimal circuit to be a non-tree, since
a tree optimum would give `tree_UB(f) <= |C| = opt(f)` and hence `gap(f) = 0`.

## Proof

Let `C` be a size-optimal single-output AIG for `f`, with `m = opt(f)` AND gates, and
suppose `C` is not a tree. Then some non-output gate of `C` has fan-out `>= 2`.

Count *input incidences* — the slots where something is read. Every AND gate has exactly
two inputs, so there are `2m` slots in total. Partition them by what they read:

```
2m = I_var + I_gate
```

where `I_var` counts slots reading a primary input or the constant, and `I_gate` counts
slots reading another gate.

**Lower bound on `I_var`.** Each of the `n` essential variables must feed at least one
slot — otherwise `f` would not depend on it. So `I_var >= n`.

**Lower bound on `I_gate`.** In a normalised circuit no gate is unused, so each of the
`m - 1` non-output gates feeds at least one later slot, contributing `>= m - 1`. The gate
with fan-out `>= 2` contributes at least one further incidence. So `I_gate >= m`.

Combining:

```
2m = I_var + I_gate >= n + m,  hence  m >= n.   ∎
```

## Where the published proof was short

The published argument went through a gate-elimination step asserting `|S| >= k - 1`,
applied to the cone `S` **excluding** the shared gate `g`. When `g` sits at input level,
the `k` essential variables of `S ∪ {g}` are not all covered by `S`, and the count falls
short by exactly one. The incidence argument above avoids the case split: it never needs
to reason about the position of the shared gate, only that one exists.

## Scope

The argument is purely combinatorial. It assumes only that the circuit is a single-output
AIG in normalised form (two inputs per gate, no unused gate) and that inversions are free,
which is the cost model used throughout this repository. It says nothing about how `opt`
is computed and does not depend on any other result in the paper.

## Provenance

Contributed via pull request. The argument was produced with AI assistance under my
direction, in an adversarial review pipeline in which the published proof was checked by
independent model families; the gap at the input-level case was found there and the
incidence argument replaced it. I selected the target, set the verification standard and
am responsible for the claim. The proof is short enough to check by hand, which is the
point: nothing here rests on how it was found.

— L. A. Busnello
