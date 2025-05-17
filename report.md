# Gem Hunter Report

## 1. Student Information

## 2. Project Structure

## 3. Logical principles

### 3.1. Propositional Logic

## 3. Algorithms

### 3.0. DIMACS Format

- We use DIMACS format to represent our boolean formulas. The syntax is:
  - The first line contains `p cnf n m`, with `n` is the number of variables, `m` is the number of clauses.
  - The next `m` lines contain the clauses, each clause is a list of integers that:
    - Positive integers represent the variable.
    - Negative integers represent the negation of the variable.
    - Each clause ends with a `0`.
  - Multiple literals in a clause represent a logical OR (∨)
  - Multiple clauses represent a logical AND (∧)
- For example:

  $$
  (\neg{x_1}\vee x_2)\wedge(\neg{x_2}\vee x_3)
  $$

- The above formula can be represented in DIMACS format as follows:

```
p cnf 3 2
-1 2 0
-2 3 0
```

- Explanation:
  - `p cnf 3 2` means 3 variables and 2 clauses
  - `-1 2 0` represents the clause $(\neg{x_1}\vee x_2)$
  - `-2 3 0` represents the clause $(\neg{x_2}\vee x_3)$

### 3.1. Problem Formulation

- The grid of size `n x n` with the following symbols:

  - `_`: empty cell.
  - `G`: cell with a gem.
  - `T`: cell with a trap.
  - `X` is a positive integer: the number of traps surrounding the current cell. This cell is neither a gem cell nor a trap cell.

#### Assumptions

- If current cell contains a Trap (`T`), the proposition is true. In other cases, the proposition is false. After this assumption, we can say that the cell is either a trap (TRUE) or not a trap (FALSE).
- A cell containing a number `X` indicates that there are **exactly** `X` traps in the surrounding cells. The surrounding cells are the 8 adjacent cells (up, down, left, right, and the 4 diagonals).

#### Proof

- Now, we are going to examine a case. For simplicity but enough complexity, we will examine a case that have 2 traps.

|       |       |     |
| ----- | ----- | --- |
| **T** | **T** | ?   |
| ?     | **2** | ?   |
| ?     | ?     | ?   |

- Note: `?` is a unknown cell. It can be any type of cell (`_`, `G`, or `X`). We will not care about the exact type of the cell, for simplicity.

- Look at the center cell. It contains `2`, which means that there are exactly $2$ traps in the surrounding cells.
- Expressing this in CNF, we can say that the center cell is `2` if and only if the following conditions are satisfied:

  - There are no more than $2$ traps in the surrounding cells.
  - There are no less than $2$ traps in the surrounding cells.

---

# REWRITE THIS PART

Let the cells around the center be numbered as variables $x_1, x_2, ..., x_8$ (if all 8 surrounding cells exist). When $x_i = TRUE$, the cell is a trap; when $x_i = FALSE$, the cell is not a trap.

In our example, we already know that $x_1 = 1$ and $x_2 = 1$ (the two traps in the top row). The other cells (marked with "?") are represented by variables $x_3$ through $x_8$.

To express "exactly 2 traps" in CNF:

1. At most 2 traps: For any combination of 3 cells, at least one must NOT be a trap.
   - For every subset of 3 variables {$x_i, x_j, x_k$}, we add the clause: $(\neg x_i \lor \neg x_j \lor \neg x_k)$
   - This prevents having 3 or more traps.
2. At least 2 traps: Since we already know $x_1 = 1$ and $x_2 = 1$, this constraint is satisfied.

- Without this knowledge, we would need clauses to ensure that for any subset of $(n-1)$ variables (where $n$ is the total number of surrounding cells), at least one must be a trap.
  In our specific example with the known traps, we only need the "at most 2 traps" constraints.

Since we already have two traps ($x_1$ and $x_2$), the CNF clauses would enforce that none of the other surrounding cells can be traps: $(\neg x_3), (\neg x_4), (\neg x_5), (\neg x_6), (\neg x_7), (\neg x_8)$

## This is how the algorithm ensures that the exact number of traps matches the number in the cell, by combining "at most k" and "at least k" constraints through CNF clauses.

### 3.2. Brute-force algorithm

For this algorithm, we will try all set of value for the CNF formula. If result is `TRUE`, that means that the current set of value is a solution. If result is `FALSE`, we will try another set of value.

### 3.3. Backtracking algorithm

### 3.4. PySAT

## 4. Results

### 4.1. Results

### 4.2. Benchmark

## 5. Conclusion

## 6. References

[1] Antonio Morgado Alexey Ignatiev Joao Marques-Silva. Boolean formula manipulation (pysat.formula). Accessed: 12 May 2025. url: https://pysathq.github.io/docs/html/api/formula.html
