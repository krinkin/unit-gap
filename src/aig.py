"""And-Inverter Graph (AIG) representation.

An AIG is a DAG where each internal node computes AND of two inputs,
and edges may be complemented (inverted). Every Boolean function can be
represented as an AIG.

Reference: Mishchenko et al., "DAG-Aware AIG Rewriting: A Fresh Look at
Combinational Logic Synthesis", DAC 2006.

Node indexing:
  - 0: constant FALSE
  - 1..n_inputs: primary inputs (PI)
  - n_inputs+1..: AND gates

A literal is (node_id, complemented). We encode literals as integers:
  lit = node_id * 2 + (1 if complemented else 0)
  So literal 0 = const 0, literal 1 = const 1,
     literal 2 = PI_0 normal, literal 3 = PI_0 inverted, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from src.boolean_function import BooleanFunction


@dataclass
class AIG:
    """An And-Inverter Graph.

    Attributes:
        n_inputs: number of primary inputs
        gates: list of (left_literal, right_literal) for each AND gate
        outputs: list of output literals
    """

    n_inputs: int
    gates: list[tuple[int, int]] = field(default_factory=list)
    outputs: list[int] = field(default_factory=list)

    @property
    def n_gates(self) -> int:
        return len(self.gates)

    def gate_node_id(self, gate_index: int) -> int:
        return self.n_inputs + 1 + gate_index

    def add_gate(self, left_lit: int, right_lit: int) -> int:
        """Add an AND gate. Returns the node_id of the new gate."""
        node_id = self.gate_node_id(len(self.gates))
        self.gates.append((left_lit, right_lit))
        return node_id

    def set_output(self, literal: int):
        """Set an output literal."""
        self.outputs.append(literal)

    def evaluate(self, inputs: tuple[int, ...]) -> tuple[int, ...]:
        """Evaluate the AIG on given inputs. Returns output values."""
        if len(inputs) != self.n_inputs:
            raise ValueError(f"Expected {self.n_inputs} inputs, got {len(inputs)}")

        # node_values[i] = value of node i
        node_values = [0] * (self.n_inputs + 1 + self.n_gates)
        node_values[0] = 0  # constant FALSE
        for i, v in enumerate(inputs):
            node_values[i + 1] = v

        for gi, (left, right) in enumerate(self.gates):
            left_val = node_values[left >> 1] ^ (left & 1)
            right_val = node_values[right >> 1] ^ (right & 1)
            node_values[self.n_inputs + 1 + gi] = left_val & right_val

        results = []
        for out_lit in self.outputs:
            val = node_values[out_lit >> 1] ^ (out_lit & 1)
            results.append(val)
        return tuple(results)

    def to_function(self) -> BooleanFunction:
        """Convert single-output AIG to BooleanFunction."""
        if len(self.outputs) != 1:
            raise ValueError("to_function requires exactly 1 output")
        tt = 0
        for i in range(1 << self.n_inputs):
            inputs = tuple((i >> k) & 1 for k in range(self.n_inputs))
            vals = self.evaluate(inputs)
            if vals[0]:
                tt |= 1 << i
        return BooleanFunction(self.n_inputs, tt)

    def is_redundant_gate(self, gate_index: int) -> bool:
        """Check if a gate's output is never used."""
        node_id = self.gate_node_id(gate_index)
        pos_lit = node_id * 2
        neg_lit = node_id * 2 + 1
        # Check if used by any other gate
        for left, right in self.gates:
            if left in (pos_lit, neg_lit) or right in (pos_lit, neg_lit):
                return False
        # Check if used by any output
        for out in self.outputs:
            if out in (pos_lit, neg_lit):
                return False
        return True

    def count_used_gates(self) -> int:
        """Count gates that contribute to outputs (non-redundant)."""
        return sum(1 for i in range(self.n_gates) if not self.is_redundant_gate(i))

    def structural_hash(self) -> tuple:
        """Return a canonical structural hash for isomorphism detection.

        Two AIGs with the same structural hash compute the same function
        with the same gate structure (up to gate renumbering).
        """
        # Topological order is already guaranteed by construction
        return (self.n_inputs, tuple(self.gates), tuple(self.outputs))

    def __repr__(self) -> str:
        return f"AIG(inputs={self.n_inputs}, gates={self.n_gates}, outputs={len(self.outputs)})"


def make_literal(node_id: int, complemented: bool = False) -> int:
    return node_id * 2 + (1 if complemented else 0)


def literal_node(lit: int) -> int:
    return lit >> 1


def literal_is_complemented(lit: int) -> bool:
    return bool(lit & 1)


def literal_complement(lit: int) -> int:
    return lit ^ 1


# --- Standard AIG constructions ---

def aig_and(aig: AIG, a: int, b: int) -> int:
    """AND of two literals. Returns result literal."""
    node = aig.add_gate(a, b)
    return make_literal(node)


def aig_or(aig: AIG, a: int, b: int) -> int:
    """OR of two literals (via De Morgan: a OR b = NOT(NOT a AND NOT b))."""
    node = aig.add_gate(a ^ 1, b ^ 1)
    return make_literal(node, complemented=True)


def aig_xor(aig: AIG, a: int, b: int) -> int:
    """XOR of two literals. Costs 3 AND gates in AIG.

    XOR(a,b) = OR(AND(a, NOT b), AND(NOT a, b))
             = NOT(AND(NOT(AND(a, NOT b)), NOT(AND(NOT a, b))))
    """
    n1 = aig.add_gate(a, b ^ 1)       # a AND (NOT b)
    n2 = aig.add_gate(a ^ 1, b)       # (NOT a) AND b
    lit1 = make_literal(n1, complemented=True)
    lit2 = make_literal(n2, complemented=True)
    n3 = aig.add_gate(lit1, lit2)      # NOT(n1) AND NOT(n2)
    return make_literal(n3, complemented=True)  # NOT of that = n1 OR n2


def aig_mux(aig: AIG, sel: int, a: int, b: int) -> int:
    """MUX: if sel then a else b. Costs 3 AND gates."""
    n1 = aig.add_gate(sel, a)          # sel AND a
    n2 = aig.add_gate(sel ^ 1, b)     # (NOT sel) AND b
    lit1 = make_literal(n1, complemented=True)
    lit2 = make_literal(n2, complemented=True)
    n3 = aig.add_gate(lit1, lit2)
    return make_literal(n3, complemented=True)


def build_from_function(func: BooleanFunction) -> AIG:
    """Build an AIG for a Boolean function using Shannon decomposition.

    This is NOT optimal — it's a straightforward recursive construction
    that gives a working circuit as a starting point.
    """
    aig = AIG(n_inputs=func.n_inputs)
    if func.n_inputs == 0:
        aig.set_output(1 if func.truth_table else 0)
        return aig

    out_lit = _build_recursive(aig, func, list(range(func.n_inputs)))
    aig.set_output(out_lit)
    return aig


def _build_recursive(aig: AIG, func: BooleanFunction, vars_remaining: list[int]) -> int:
    """Recursively build AIG via Shannon decomposition on the first variable."""
    if func.is_constant():
        return 1 if func.truth_table != 0 else 0

    if func.n_inputs == 1:
        pi_lit = make_literal(vars_remaining[0] + 1)
        if func.truth_table == 0b10:  # identity
            return pi_lit
        else:  # func.truth_table == 0b01, complement
            return pi_lit ^ 1

    # Shannon decomposition on variable 0 of current function
    var = vars_remaining[0]
    rest = vars_remaining[1:]
    f0 = func.cofactor(0, 0)
    f1 = func.cofactor(0, 1)

    if f0.truth_table == f1.truth_table:
        # Variable is don't-care
        return _build_recursive(aig, f0, rest)

    lit0 = _build_recursive(aig, f0, rest)
    lit1 = _build_recursive(aig, f1, rest)

    # f = x * f1 + x' * f0 = MUX(x, f1, f0)
    sel = make_literal(var + 1)
    return aig_mux(aig, sel, lit1, lit0)
