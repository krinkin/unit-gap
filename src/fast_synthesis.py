"""Exact synthesis using truth table simulation with correct gate counting.

For small functions (n <= 3), we enumerate circuits gate-by-gate in
topological order. Each gate is an AND of two available literals (possibly
complemented). We track intermediate results as truth tables for deduplication.

Approach: enumerate all k-gate circuits for k = 0, 1, 2, ... At each level,
record which truth tables become achievable for the first time.

Key optimization: two circuits that produce the same sorted tuple of
intermediate truth tables are functionally equivalent. We memoize on
this to prune the search tree.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FastSynthesisResult:
    """Result of fast exact synthesis."""
    n_inputs: int
    min_gates: dict[int, int]  # truth_table -> minimum gate count
    functions_by_gates: dict[int, list[int]]  # gate_count -> list of truth tables


def base_truth_tables(n_inputs: int) -> list[int]:
    """Truth tables available with 0 gates: constants and PIs with complements."""
    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1
    result = [0, mask]
    for i in range(n_inputs):
        tt = 0
        for j in range(n_rows):
            if (j >> i) & 1:
                tt |= 1 << j
        result.append(tt)
        result.append(tt ^ mask)
    return sorted(set(result))


def fast_exact_synthesis(n_inputs: int, max_gates: int = 10) -> FastSynthesisResult:
    """Find minimum AIG size for all n-input Boolean functions.

    Enumerates circuits gate-by-gate with memoization on the set of
    available truth tables. Correct gate counting: each AND gate counts
    as 1 regardless of input sharing.
    """
    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1
    total_functions = 1 << n_rows

    base = tuple(base_truth_tables(n_inputs))
    min_gates: dict[int, int] = {}
    functions_by_gates: dict[int, list[int]] = {}

    # Level 0: base functions
    fns_0 = []
    for tt in base:
        if tt not in min_gates:
            min_gates[tt] = 0
            fns_0.append(tt)
    functions_by_gates[0] = fns_0

    if len(min_gates) >= total_functions:
        return FastSynthesisResult(n_inputs, min_gates, functions_by_gates)

    # For each level k, find new functions by adding one gate
    # available_states_prev = set of frozensets of TTs reachable at level k-1
    # We track all distinct "available TT sets" to avoid redundant exploration

    prev_states: set[tuple[int, ...]] = {base}

    for k in range(1, max_gates + 1):
        if len(min_gates) >= total_functions:
            break

        new_fns = []
        next_states: set[tuple[int, ...]] = set()

        for state in prev_states:
            state_set = set(state)
            n = len(state)
            for i in range(n):
                for j in range(i, n):
                    and_tt = state[i] & state[j]
                    comp_tt = and_tt ^ mask
                    # Skip if gate produces nothing new
                    if and_tt in state_set and comp_tt in state_set:
                        continue

                    # New state with this gate added
                    new_tts = set(state_set)
                    new_tts.add(and_tt)
                    new_tts.add(comp_tt)
                    new_state = tuple(sorted(new_tts))

                    if new_state in next_states or new_state in prev_states:
                        continue
                    next_states.add(new_state)

                    # Record newly found functions
                    for tt in (and_tt, comp_tt):
                        if tt not in min_gates:
                            min_gates[tt] = k
                            new_fns.append(tt)

        functions_by_gates[k] = new_fns
        # For next level, explore from both previous and new states
        prev_states = next_states
        if not next_states:
            break

    return FastSynthesisResult(n_inputs, min_gates, functions_by_gates)


def print_synthesis_summary(result: FastSynthesisResult):
    """Print a summary of synthesis results."""
    total = 1 << (1 << result.n_inputs)
    found = len(result.min_gates)
    print(f"Exact synthesis for {result.n_inputs}-input functions:")
    print(f"  Total functions: {total}")
    print(f"  Functions found: {found} ({100*found/total:.1f}%)")
    print()
    print("  Distribution of minimum gate counts:")
    for k in sorted(result.functions_by_gates):
        count = len(result.functions_by_gates[k])
        if count > 0:
            print(f"    {k} gates: {count} functions")
    if found < total:
        print(f"    Not found: {total - found} functions")
