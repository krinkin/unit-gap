# Data file descriptions

## n3_complete.json / n4_complete.json

Complete gap analysis for all non-trivial Boolean functions at n=3 (248 functions) and n=4 (20,660 functions with opt <= 6).

**Top-level fields:**
- `n` (int): number of input variables
- `total_functions` (int): number of functions in the file
- `gap_distribution` (dict): mapping `"gap_value"` -> count
- `functions` (list): array of function records

**Function record fields:**
- `tt` (int): truth table as integer (bit i = f(i), LSB = x_0)
- `opt` (int): minimum number of AND gates in any AIG computing f
- `tree_ub` (int): tree upper bound = min over AND/NAND decompositions of [1 + opt(a) + opt(b)]
- `gap` (int): tree_ub - opt (always 0 or 1)
- `n_essential` (int): number of essential (non-redundant) input variables
- `npn_rep` (int): truth table of the NPN canonical representative

## n5_gap1_circuits.json

All 31 gap=1 functions at n=5 (opt=5) with optimal circuit structure.

**Top-level fields:**
- `n` (int): 5
- `opt` (int): 5
- `gap1_count` (int): 31
- `circuits` (list): array of circuit records

**Circuit record fields:**
- `tt` (int): truth table
- `tt_hex` (string): truth table in hexadecimal
- `gates` (list of [int, int]): each entry [la, lb] is an AND gate with literal inputs. Literal encoding: `node_id * 2 + is_complemented`. Node 0 = const 0, nodes 1..5 = primary inputs x0..x4, nodes 6+ = gate outputs.
- `out_lit` (int): output literal
- `mechanism` (string): `"dual-polarity"` or `"same-polarity"`
- `shared_gates` (list): details of shared (fan-out > 1) gates
  - `gate_idx` (int): index into gates array
  - `depth` (int): depth relative to PIs (-1 = leaf gate with only PI inputs, 0 = one level above PIs)
  - `pi_inputs` (list of int): which primary inputs the shared gate depends on
  - `polarity_type` (string): `"dual-polarity"` (used in both polarities) or `"same-polarity"` (reused with same polarity)
  - `ref_count` (int): number of times the gate output is referenced
- `template_details` (list): XOR/MUX template match details (if any)

## n6_gap1_circuits.json

6 constructed gap=1 circuits at n=6. Same circuit record format as n5.

**Top-level fields:**
- `n` (int): 6
- `total_candidates` (int): number of template candidates tested
- `total_solved` (int): number verified as opt=6
- `gap1_count` (int): 6
- `circuits` (list): array of circuit records (same format as n5)

## n6_gap1_random.json

159 randomly generated gap=1 circuits at n=6 with compact format.

**Top-level fields:**
- `n` (int): 6
- `gap1_count` (int): 159
- `gap0_count` (int): 0
- `circuits` (list): array of circuit records

**Circuit record fields (compact format):**
- `tt` (int): truth table
- `tt_hex` (string): truth table in hexadecimal
- `pattern` (string): generation pattern (`"cse"`, `"dual"`, `"mixed"`, `"deep"`, `"multi"`)
- `gates` (list of [int, int]): AND gate literals (same encoding as n5)
- `out_lit` (int): output literal
- `sharing` (list of [int, string, int]): each entry is [gate_idx, polarity_type, ref_count]

## n7_gap1_circuits.json

60 gap=1 circuits at n=7 (opt=7). Same circuit record format as n5/n6.

**Top-level fields:**
- `n` (int): 7
- `total_candidates` (int): 508
- `total_tested` (int): 60
- `total_opt7` (int): 60
- `gap0_count` (int): 0
- `gap1_count` (int): 60
- `skipped_opt_low` (int): 0 (all tested had opt=7)
- `skipped_opt_high` (int): 0
- `skipped_timeout` (int): 0
- `elapsed_seconds` (float): computation time
- `circuits` (list): array of circuit records (same format as n5)

## npn4_classes.json

NPN equivalence class sizes for all 222 classes of 4-input Boolean functions.

**Format:** dict mapping canonical truth table (string) -> class size (int).

Example: `"0": 2` means NPN class with representative tt=0 contains 2 functions (const 0 and const 1). The sum of all values equals 65,536.

## Literal encoding

All circuit data uses the AIG literal encoding:
- `literal = node_id * 2 + is_complemented`
- Node 0 = constant FALSE (literal 0 = FALSE, literal 1 = TRUE)
- Nodes 1..n = primary inputs x_0..x_{n-1}
- Nodes n+1, n+2, ... = AND gates in topological order
- Each AND gate computes `val(left_literal) AND val(right_literal)`
- A complemented literal (odd) inverts the value
