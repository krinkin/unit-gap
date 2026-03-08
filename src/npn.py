"""NPN equivalence classification of Boolean functions.

Two Boolean functions are NPN-equivalent if one can be obtained from the
other by:
  N: negating (complementing) any subset of inputs
  P: permuting inputs
  N: negating the output

NPN equivalence preserves circuit complexity: if f and g are NPN-equivalent,
they have the same minimum AIG size (because input/output complementation
is free in AIG, and input permutation just relabels wires).

For n inputs, there are:
  n=2: 4 NPN classes (out of 16 functions)
  n=3: 14 NPN classes (out of 256 functions)
  n=4: 222 NPN classes (out of 65536 functions)

Reference: Harrison, "The number of equivalence classes of Boolean functions
under groups containing negation", IEEE Trans. EC, 1963.
"""

from __future__ import annotations

from itertools import permutations, product
from src.boolean_function import BooleanFunction


def npn_canonical(func: BooleanFunction) -> int:
    """Compute the NPN canonical form of a Boolean function.

    Returns the minimum truth table value among all NPN-equivalent functions.
    This serves as the representative of the NPN equivalence class.
    """
    n = func.n_inputs
    n_rows = 1 << n
    mask = (1 << n_rows) - 1
    min_tt = func.truth_table

    # Try all input permutations
    for perm in permutations(range(n)):
        # Try all input negation patterns (2^n combinations)
        for neg_pattern in range(1 << n):
            # Apply negation and permutation
            new_tt = 0
            for i in range(n_rows):
                # Map new input assignment to original
                orig = 0
                for new_var in range(n):
                    old_var = perm[new_var]
                    bit = (i >> new_var) & 1
                    if (neg_pattern >> new_var) & 1:
                        bit ^= 1
                    orig |= bit << old_var
                if (func.truth_table >> orig) & 1:
                    new_tt |= 1 << i

            # Try both output polarities
            min_tt = min(min_tt, new_tt, new_tt ^ mask)

    return min_tt


def classify_npn(n_inputs: int) -> dict[int, list[int]]:
    """Classify all n-input Boolean functions into NPN equivalence classes.

    Returns dict mapping canonical_tt -> list of truth tables in the class.
    """
    classes: dict[int, list[int]] = {}
    for tt in range(1 << (1 << n_inputs)):
        f = BooleanFunction(n_inputs, tt)
        canonical = npn_canonical(f)
        if canonical not in classes:
            classes[canonical] = []
        classes[canonical].append(tt)
    return classes


def npn_class_representatives(n_inputs: int) -> list[int]:
    """Return one representative truth table per NPN class."""
    classes = classify_npn(n_inputs)
    return sorted(classes.keys())
