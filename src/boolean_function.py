"""Boolean function representation via truth tables.

A Boolean function f: {0,1}^n -> {0,1} is represented by its truth table,
a bitvector of length 2^n. Entry i is f(x) where x is the binary encoding of i
(LSB = x_0).

For n inputs, there are 2^(2^n) distinct Boolean functions:
  n=2: 16 functions
  n=3: 256 functions
  n=4: 65536 functions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True, slots=True)
class BooleanFunction:
    """A Boolean function represented by its truth table.

    Attributes:
        n_inputs: number of input variables
        truth_table: integer whose binary representation is the truth table
            (bit i = f(i) where i is interpreted as input assignment, LSB = x_0)
    """

    n_inputs: int
    truth_table: int

    def __post_init__(self):
        max_val = 1 << (1 << self.n_inputs)
        if not (0 <= self.truth_table < max_val):
            raise ValueError(
                f"truth_table must be in [0, {max_val}) for {self.n_inputs} inputs"
            )

    @property
    def n_rows(self) -> int:
        return 1 << self.n_inputs

    def evaluate(self, inputs: tuple[int, ...]) -> int:
        """Evaluate the function on a specific input assignment."""
        if len(inputs) != self.n_inputs:
            raise ValueError(f"Expected {self.n_inputs} inputs, got {len(inputs)}")
        index = sum(b << i for i, b in enumerate(inputs))
        return (self.truth_table >> index) & 1

    def is_constant(self) -> bool:
        return self.truth_table == 0 or self.truth_table == (1 << self.n_rows) - 1

    def complement(self) -> BooleanFunction:
        """Return the complement (NOT) of this function."""
        mask = (1 << self.n_rows) - 1
        return BooleanFunction(self.n_inputs, self.truth_table ^ mask)

    def cofactor(self, var: int, value: int) -> BooleanFunction:
        """Shannon cofactor: fix variable var to value.

        Returns a function of n-1 inputs.
        Reference: Shannon decomposition, Shannon 1949.
        """
        if var < 0 or var >= self.n_inputs:
            raise ValueError(f"Variable index {var} out of range [0, {self.n_inputs})")
        new_n = self.n_inputs - 1
        new_tt = 0
        for i in range(1 << new_n):
            # Insert 'value' at position 'var' in the bit pattern
            low = i & ((1 << var) - 1)
            high = (i >> var) << (var + 1)
            orig_index = high | (value << var) | low
            if (self.truth_table >> orig_index) & 1:
                new_tt |= 1 << i
        return BooleanFunction(new_n, new_tt)

    def permute_inputs(self, perm: tuple[int, ...]) -> BooleanFunction:
        """Permute input variables. perm[i] = which original variable becomes new variable i."""
        if len(perm) != self.n_inputs or set(perm) != set(range(self.n_inputs)):
            raise ValueError(f"Invalid permutation: {perm}")
        new_tt = 0
        for i in range(self.n_rows):
            # Map new input assignment i to original assignment
            orig = 0
            for new_var, old_var in enumerate(perm):
                if (i >> new_var) & 1:
                    orig |= 1 << old_var
            if (self.truth_table >> orig) & 1:
                new_tt |= 1 << i
        return BooleanFunction(self.n_inputs, new_tt)

    def __repr__(self) -> str:
        tt_str = format(self.truth_table, f"0{self.n_rows}b")[::-1]
        return f"BooleanFunction(n={self.n_inputs}, tt={tt_str})"


def enumerate_all(n_inputs: int) -> Iterator[BooleanFunction]:
    """Enumerate all Boolean functions with n_inputs inputs."""
    for tt in range(1 << (1 << n_inputs)):
        yield BooleanFunction(n_inputs, tt)


def from_expression(n_inputs: int, expr) -> BooleanFunction:
    """Build a BooleanFunction from a callable expression.

    expr takes n_inputs integer arguments (0 or 1) and returns 0 or 1.
    """
    tt = 0
    for i in range(1 << n_inputs):
        inputs = tuple((i >> k) & 1 for k in range(n_inputs))
        if expr(*inputs):
            tt |= 1 << i
    return BooleanFunction(n_inputs, tt)
