"""Tropical algebra analysis of the Bellman equation for circuit complexity.

The Bellman equation opt(f) = min_{a,b: f=AND(a,b)}[1 + opt(a) + opt(b)]
is naturally an equation over the tropical semiring (Z, min, +).

This module:
1. Computes tropical polynomials for each Boolean function
2. Analyzes the gap between tropical (tree) and exact solutions
3. Studies the fixed-point structure of the tropical Bellman operator
4. Formulates the transition matrix for tropical iteration
"""

from __future__ import annotations

from src.fast_synthesis import FastSynthesisResult, base_truth_tables, fast_exact_synthesis


def all_and_decompositions(f_tt: int, n_inputs: int, opt_data: dict[int, int]) -> list[dict]:
    """Find all AND/NAND decompositions of f into known functions.

    For f = AND(a, b) or f = NAND(a, b), enumerate all (a, b) pairs
    where both a and b have known optimal cost.

    Returns list of dicts with keys: a_tt, b_tt, opt_a, opt_b, tree_cost, is_nand.
    """
    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1

    decomps = []

    for is_nand in [False, True]:
        target = f_tt if not is_nand else (f_tt ^ mask)

        for a_tt, opt_a in opt_data.items():
            # a & b = target means target must be a subset of a (bitwise)
            if (a_tt & target) != target:
                continue

            # b can have target's 1-bits plus any bits where a is 0
            free_mask = (~a_tt) & mask
            subset = 0
            while True:
                b_tt = target | subset
                if b_tt in opt_data:
                    opt_b = opt_data[b_tt]
                    tree_cost = 1 + opt_a + opt_b
                    decomps.append({
                        'a_tt': a_tt,
                        'b_tt': b_tt,
                        'opt_a': opt_a,
                        'opt_b': opt_b,
                        'tree_cost': tree_cost,
                        'is_nand': is_nand,
                    })

                if subset == free_mask:
                    break
                subset = (subset - free_mask) & free_mask

    return decomps


def tropical_polynomial(f_tt: int, n_inputs: int, opt_data: dict[int, int]) -> dict:
    """Compute the tropical polynomial T(f) = min_{decomps}[1 + opt(a) + opt(b)].

    Returns dict with:
      - value: the tropical minimum (tree upper bound)
      - n_terms: number of decomposition terms
      - n_minimizers: number of terms achieving the minimum
      - all_costs: sorted list of all tree costs
      - gap: T(f) - opt(f) (tropical gap, >= 0)
      - minimizer_examples: list of (a_tt, b_tt) achieving the minimum
    """
    decomps = all_and_decompositions(f_tt, n_inputs, opt_data)

    if not decomps:
        return {
            'value': float('inf'),
            'n_terms': 0,
            'n_minimizers': 0,
            'all_costs': [],
            'gap': None,
            'minimizer_examples': [],
        }

    costs = [d['tree_cost'] for d in decomps]
    min_cost = min(costs)
    minimizers = [d for d in decomps if d['tree_cost'] == min_cost]

    opt_f = opt_data.get(f_tt)
    gap = (min_cost - opt_f) if opt_f is not None else None

    return {
        'value': min_cost,
        'n_terms': len(decomps),
        'n_minimizers': len(minimizers),
        'all_costs': sorted(set(costs)),
        'gap': gap,
        'minimizer_examples': [(m['a_tt'], m['b_tt'], m['is_nand']) for m in minimizers[:5]],
    }


def tropical_bellman_operator(opt_current: dict[int, int], n_inputs: int) -> dict[int, int]:
    """Apply one step of the tropical Bellman operator.

    F(v)(f) = min_{a,b: f=AND(a,b) or NAND}[1 + v(a) + v(b)]

    Starting from any upper bound v, repeated application converges
    to the tree upper bound (without sharing).
    """
    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1
    total = 1 << n_rows

    result = dict(opt_current)

    for f_tt in range(total):
        if f_tt not in opt_current:
            continue

        for is_nand in [False, True]:
            target = f_tt if not is_nand else (f_tt ^ mask)

            for a_tt, v_a in opt_current.items():
                if (a_tt & target) != target:
                    continue

                free_mask = (~a_tt) & mask
                subset = 0
                while True:
                    b_tt = target | subset
                    if b_tt in opt_current:
                        v_b = opt_current[b_tt]
                        new_cost = 1 + v_a + v_b
                        if new_cost < result.get(f_tt, float('inf')):
                            result[f_tt] = new_cost

                    if subset == free_mask:
                        break
                    subset = (subset - free_mask) & free_mask

    return result


def tropical_transition_matrix(n_inputs: int, opt_data: dict[int, int]) -> dict[int, list[tuple[int, int, int]]]:
    """Build the tropical transition structure.

    For each function f, list all (a, b, cost) triples where
    f = AND(a, b) or NAND(a, b) and cost = 1 + opt(a) + opt(b).

    This is the adjacency structure of the tropical "Bellman graph".
    """
    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1
    transitions: dict[int, list[tuple[int, int, int]]] = {}

    for f_tt in opt_data:
        decomps = all_and_decompositions(f_tt, n_inputs, opt_data)
        transitions[f_tt] = [(d['a_tt'], d['b_tt'], d['tree_cost']) for d in decomps]

    return transitions


def analyze_tropical_landscape(n_inputs: int, max_gates: int = 10) -> dict:
    """Full tropical analysis for all n-input functions.

    Returns comprehensive analysis of the tropical Bellman equation
    including polynomial structure, gap distribution, and fixed-point
    convergence.
    """
    synth = fast_exact_synthesis(n_inputs, max_gates)
    opt_data = synth.min_gates

    # Compute tropical polynomials for all functions
    polynomials = {}
    for f_tt in opt_data:
        if opt_data[f_tt] == 0:
            continue  # Skip base functions (constants, inputs)
        polynomials[f_tt] = tropical_polynomial(f_tt, n_inputs, opt_data)

    # Gap distribution
    gap_counts: dict[int, int] = {}
    gap_by_opt: dict[int, dict[int, int]] = {}
    for f_tt, poly in polynomials.items():
        gap = poly['gap']
        if gap is None:
            continue
        gap_counts[gap] = gap_counts.get(gap, 0) + 1
        opt_f = opt_data[f_tt]
        if opt_f not in gap_by_opt:
            gap_by_opt[opt_f] = {}
        gap_by_opt[opt_f][gap] = gap_by_opt[opt_f].get(gap, 0) + 1

    # Tropical polynomial complexity (number of terms)
    terms_by_opt: dict[int, list[int]] = {}
    for f_tt, poly in polynomials.items():
        opt_f = opt_data[f_tt]
        if opt_f not in terms_by_opt:
            terms_by_opt[opt_f] = []
        terms_by_opt[opt_f].append(poly['n_terms'])

    # Number of minimizers
    minimizers_by_opt: dict[int, list[int]] = {}
    for f_tt, poly in polynomials.items():
        opt_f = opt_data[f_tt]
        if opt_f not in minimizers_by_opt:
            minimizers_by_opt[opt_f] = []
        minimizers_by_opt[opt_f].append(poly['n_minimizers'])

    # Cost spectrum: how many distinct costs appear
    spectrum_by_opt: dict[int, list[int]] = {}
    for f_tt, poly in polynomials.items():
        opt_f = opt_data[f_tt]
        if opt_f not in spectrum_by_opt:
            spectrum_by_opt[opt_f] = []
        spectrum_by_opt[opt_f].append(len(poly['all_costs']))

    return {
        'n_inputs': n_inputs,
        'n_functions': len(opt_data),
        'n_analyzed': len(polynomials),
        'gap_counts': gap_counts,
        'gap_by_opt': gap_by_opt,
        'terms_by_opt': {k: (min(v), sum(v)/len(v), max(v)) for k, v in terms_by_opt.items()},
        'minimizers_by_opt': {k: (min(v), sum(v)/len(v), max(v)) for k, v in minimizers_by_opt.items()},
        'spectrum_by_opt': {k: (min(v), sum(v)/len(v), max(v)) for k, v in spectrum_by_opt.items()},
        'polynomials': polynomials,
        'opt_data': opt_data,
    }


def tropical_fixed_point_convergence(n_inputs: int, max_gates: int = 10, max_iters: int = 20) -> list[dict]:
    """Study convergence of the tropical Bellman operator.

    Start from upper bounds (e.g., n_inputs * some constant) and
    iterate the Bellman operator, tracking how many functions reach
    their optimal value at each iteration.
    """
    synth = fast_exact_synthesis(n_inputs, max_gates)
    opt_exact = synth.min_gates

    n_rows = 1 << n_inputs
    mask = (1 << n_rows) - 1

    # Initialize: base functions exact, everything else at infinity
    current = {}
    base = base_truth_tables(n_inputs)
    for tt in base:
        current[tt] = 0

    convergence_log = []

    for iteration in range(max_iters):
        # Count how many match exact
        n_exact = sum(1 for tt in opt_exact if current.get(tt) == opt_exact[tt])
        n_finite = sum(1 for tt in opt_exact if tt in current and current[tt] < float('inf'))

        convergence_log.append({
            'iteration': iteration,
            'n_exact': n_exact,
            'n_finite': n_finite,
            'n_total': len(opt_exact),
        })

        if n_exact == len(opt_exact):
            break

        # Apply Bellman operator: try to improve every function
        new_current = dict(current)
        total = 1 << n_rows

        for f_tt in range(total):
            for is_nand in [False, True]:
                target = f_tt if not is_nand else (f_tt ^ mask)

                for a_tt in current:
                    if (a_tt & target) != target:
                        continue
                    v_a = current[a_tt]
                    if v_a >= 100:  # Skip unreachable
                        continue

                    free_mask = (~a_tt) & mask
                    subset = 0
                    while True:
                        b_tt = target | subset
                        if b_tt in current:
                            v_b = current[b_tt]
                            if v_b < 100:
                                new_cost = 1 + v_a + v_b
                                old_cost = new_current.get(f_tt, 100)
                                if new_cost < old_cost:
                                    new_current[f_tt] = new_cost

                        if subset == free_mask:
                            break
                        subset = (subset - free_mask) & free_mask

        current = new_current

    return convergence_log
