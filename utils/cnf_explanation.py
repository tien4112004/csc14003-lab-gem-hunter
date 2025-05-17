"""
Module for generating and explaining CNF constraints for the Gem Hunter problem.
Also provides visualization utilities for puzzles and solutions.
"""

import textwrap
from colorama import Fore, Back, Style, init
import consts
from solvers.sat_solver import SATSolver
from solvers.classical_solvers import solver_utils
import utils.solver_utils as solver_utils

# Initialize colorama for cross-platform colored output
init()

def cell_variable_name(i, j, state):
    """Get a human-readable variable name for a cell state."""
    return f"{state}({i},{j})"

def generate_cnf_explanation():
    """Generate a human-readable explanation of CNF constraints for Gem Hunter."""
    explanation = """
# CNF Constraints for Gem Hunter

We need to encode the Gem Hunter rules into CNF (Conjunctive Normal Form) constraints for the SAT solver.
For each cell (i, j) in the grid, we create three boolean variables:
- T(i,j): Cell (i,j) contains a trap
- G(i,j): Cell (i,j) contains a gem
- E(i,j): Cell (i,j) is empty

## Basic Cell State Constraints

1. Each cell must have exactly one state:
   - (T(i,j) ∨ G(i,j) ∨ E(i,j)) for each cell (i,j)
   
2. No cell can have more than one state:
   - (¬T(i,j) ∨ ¬G(i,j)) for each cell (i,j)
   - (¬T(i,j) ∨ ¬E(i,j)) for each cell (i,j)
   - (¬G(i,j) ∨ ¬E(i,j)) for each cell (i,j)

## Number Cell Constraints

For a cell (i,j) with number n, we need to enforce that exactly n neighboring cells contain traps.
Let's say the neighboring cells are {(n1_i, n1_j), (n2_i, n2_j), ..., (nk_i, nk_j)}.

1. At most n neighboring cells can be traps:
   - For every subset S of n+1 neighboring cells, add the constraint:
     (¬T(n1_i,n1_j) ∨ ¬T(n2_i,n2_j) ∨ ... ∨ ¬T(nx_i,nx_j)) 
     where x varies over the n+1 cells in subset S

2. At least n neighboring cells can be traps:
   - For every subset S of (k-n+1) neighboring cells, add the constraint:
     (T(n1_i,n1_j) ∨ T(n2_i,n2_j) ∨ ... ∨ T(nx_i,nx_j))
     where x varies over the (k-n+1) cells in subset S

## Gem Cell Constraints

For a cell (i,j) to be a gem:

1. None of its neighboring cells can be traps:
   - For each neighboring cell (ni,nj):
     (¬G(i,j) ∨ ¬T(ni,nj))

2. At least one of its neighboring cells must be a non-empty cell:
   - (¬G(i,j) ∨ ¬E(n1_i,n1_j) ∨ ¬E(n2_i,n2_j) ∨ ... ∨ ¬E(nk_i,nk_j))
     where (n1_i,n1_j), (n2_i,n2_j), ..., (nk_i,nk_j) are all neighboring cells

## Unreachable Cell Constraints

A cell is unreachable if all its neighbors are empty cells. An unreachable cell must remain empty.

For a cell (i,j) with neighbors {(n1_i, n1_j), (n2_i, n2_j), ..., (nk_i, nk_j)}:
- (¬E(n1_i,n1_j) ∨ ¬E(n2_i,n2_j) ∨ ... ∨ ¬E(nk_i,nk_j) ∨ E(i,j))

This says "if all neighbors are empty, then this cell must be empty."

## Example

For a 3x3 grid with cell (1,1) having a number 2, some of the CNF clauses would be:

- Basic state for cell (1,1):
  - (T(1,1) ∨ G(1,1) ∨ E(1,1))  # Cell has a state
  - (¬T(1,1) ∨ ¬G(1,1))  # Not both trap and gem
  - (¬T(1,1) ∨ ¬E(1,1))  # Not both trap and empty
  - (¬G(1,1) ∨ ¬E(1,1))  # Not both gem and empty

- Number 2 constraints for cell (1,1) with 8 neighbors:
  - Various clauses ensuring exactly 2 neighbors are traps

- For neighboring cell (0,0):
  - (¬G(0,0) ∨ ¬T(0,1))  # If (0,0) is a gem, (0,1) can't be a trap
  - (¬G(0,0) ∨ ¬T(1,0))  # If (0,0) is a gem, (1,0) can't be a trap
  - ... # Similar for other neighbors

- Unreachable constraints:
  - For each cell, clauses ensuring it's empty if all neighbors are empty
"""
    return explanation

def explain_cnf_for_example_grid():
    """Generate a concrete example of CNF constraints for a small Gem Hunter grid."""
    # Create a small example grid
    example_grid = [
        ["_", "2", "_"],
        ["3", "_", "1"],
        ["_", "2", "_"]
    ]
    
    # Explain the variables
    explanation = "# CNF Example for a 3x3 Gem Hunter Grid\n\n"
    explanation += "Let's examine a 3x3 grid with the following cells:\n"
    explanation += "```\n"
    explanation += "  _ 2 _\n"
    explanation += "  3 _ 1\n"
    explanation += "  _ 2 _\n"
    explanation += "```\n\n"
    
    explanation += "## Variable Encoding\n\n"
    explanation += "For each cell (i,j), we create three boolean variables:\n"
    explanation += "- T(i,j): Cell contains a Trap\n"
    explanation += "- G(i,j): Cell contains a Gem\n"
    explanation += "- E(i,j): Cell is Empty\n\n"
    
    # Explain the constraints for the center cell
    explanation += "## Constraints for Cell (1,1) - Empty Cell\n\n"
    
    explanation += "1. Cell state constraints:\n"
    explanation += "   - (T(1,1) ∨ G(1,1) ∨ E(1,1))  # Cell has exactly one state\n"
    explanation += "   - (¬T(1,1) ∨ ¬G(1,1))         # Not both trap and gem\n"
    explanation += "   - (¬T(1,1) ∨ ¬E(1,1))         # Not both trap and empty\n"
    explanation += "   - (¬G(1,1) ∨ ¬E(1,1))         # Not both gem and empty\n\n"
    
    explanation += "2. Gem constraints (applicable if the cell is a gem):\n"
    explanation += "   - (¬G(1,1) ∨ ¬T(0,0))  # If (1,1) is a gem, (0,0) can't be a trap\n"
    explanation += "   - (¬G(1,1) ∨ ¬T(0,1))  # If (1,1) is a gem, (0,1) can't be a trap\n"
    explanation += "   - ... (similar for all 8 neighbors)\n\n"
    explanation += "   - (¬G(1,1) ∨ ¬E(0,0) ∨ ¬E(0,1) ∨ ... ∨ ¬E(2,2))  # At least one neighbor non-empty\n\n"
    
    explanation += "## Constraints for Cell (0,1) - Number 2\n\n"
    
    explanation += "1. Cell state constraints (same as above)\n\n"
    
    explanation += "2. Number 2 constraints:\n"
    explanation += "   For cell (0,1) with 5 neighbors (on the top edge), we need exactly 2 traps.\n\n"
    explanation += "   - At most 2 traps: For every 3 neighbors, at least one must not be a trap\n"
    explanation += "     - (¬T(0,0) ∨ ¬T(0,2) ∨ ¬T(1,0))  # Not all three can be traps\n"
    explanation += "     - (¬T(0,0) ∨ ¬T(0,2) ∨ ¬T(1,1))  # Not all three can be traps\n"
    explanation += "     - ... (all combinations of 3 neighbors)\n\n"
    explanation += "   - At least 2 traps: For every 4 neighbors, at least one must be a trap\n"
    explanation += "     - (T(0,0) ∨ T(0,2) ∨ T(1,0) ∨ T(1,1))  # At least one must be a trap\n"
    explanation += "     - ... (all combinations of 4 neighbors)\n\n"
    
    explanation += "## Unreachable Cell Constraints\n\n"
    explanation += "For each cell, if all its neighbors are empty, the cell must be empty:\n"
    explanation += "- (¬E(0,0) ∨ ¬E(0,1) ∨ ... ∨ ¬E(2,2) ∨ E(1,1))  # If all neighbors of (1,1) are empty, (1,1) must be empty\n\n"
    
    explanation += "## SAT Solving\n\n"
    explanation += "The SAT solver finds an assignment to all variables that satisfies all these constraints.\n"
    explanation += "The solution corresponds to a valid placement of traps and gems in the grid.\n"
    
    return explanation

def generate_specific_cnf_example(grid_size=3):
    """Generate a specific small example with actual CNF clauses."""
    # Create a small example grid
    puzzle = [["_" for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Add some numbers
    puzzle[0][1] = "2"  # Top middle
    puzzle[1][0] = "1"  # Middle left
    
    # Create the SAT solver
    solver = SATSolver(puzzle)
    
    # Generate CNF
    solver.generate_cnf()
    
    # Get statistics
    stats = solver.get_cnf_stats()
    
    # Format a human-readable explanation with actual clauses
    explanation = f"# Example CNF for a {grid_size}x{grid_size} Grid\n\n"
    explanation += "Grid:\n```\n"
    for row in puzzle:
        explanation += "  " + " ".join(row) + "\n"
    explanation += "```\n\n"
    
    explanation += f"This grid generates {stats['variables']} variables and {stats['clauses']} clauses.\n\n"
    
    explanation += "## Variable Encoding\n\n"
    explanation += "Variables are encoded as follows:\n"
    for i in range(grid_size):
        for j in range(grid_size):
            for state in ['T', 'G', '_']:
                var_id = solver.var_mapping[(i, j, state)]
                explanation += f"- Variable {var_id}: {cell_variable_name(i, j, state)}\n"
    
    explanation += "\n## Selected Clauses\n\n"
    
    # Display first 10 clauses as examples
    for idx, clause in enumerate(solver.cnf.clauses[:10]):
        clause_str = " ∨ ".join([
            f"{'¬' if lit < 0 else ''}{cell_variable_name(*solver.inverse_mapping[abs(lit)])}" 
            for lit in clause
        ])
        explanation += f"{idx+1}. ({clause_str})\n"
    
    explanation += f"... and {len(solver.cnf.clauses) - 10} more clauses.\n"
    
    return explanation

def print_grid(grid, colorized=True):
    """
    Print a grid (puzzle or solution) with colorized output.
    
    Args:
        grid (list): 2D grid to print
        colorized (bool): Whether to use colorized output
    """
    if not grid:
        print("Empty grid")
        return
    
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    # Print column indices
    if colorized:
        print("  ", end="")
        for j in range(width):
            print(f"{Fore.CYAN}{j}{Style.RESET_ALL} ", end="")
        print()
    else:
        print("  " + " ".join(str(j) for j in range(width)))
    
    # Print rows
    for i in range(height):
        if colorized:
            print(f"{Fore.CYAN}{i}{Style.RESET_ALL} ", end="")
        else:
            print(f"{i} ", end="")
            
        for j in range(width):
            cell = grid[i][j]
            
            if not colorized:
                print(f"{cell} ", end="")
            else:
                if cell.isdigit():
                    print(f"{Fore.BLUE}{cell}{Style.RESET_ALL} ", end="")
                elif cell == consts.TRAP_CELL:
                    print(f"{Fore.RED}{cell}{Style.RESET_ALL} ", end="")
                elif cell == consts.GEM_CELL:
                    print(f"{Fore.GREEN}{cell}{Style.RESET_ALL} ", end="")
                else:  # Empty cell
                    print(f"{cell} ", end="")
        
        print()

def explain_solution(puzzle, solution):
    """
    Explain why a solution is valid by checking all constraints.
    
    Args:
        puzzle (list): 2D puzzle grid
        solution (list): 2D solution grid
    """
    height = len(puzzle)
    width = len(puzzle[0]) if height > 0 else 0
    
    explanation = []
    
    # Check number cell constraints
    for i in range(height):
        for j in range(width):
            if puzzle[i][j].isdigit():
                neighbors = solver_utils.get_neighbors(i, j, height, width)
                trap_count = sum(1 for ni, nj in neighbors if solution[ni][nj] == consts.TRAP_CELL)
                
                explanation.append(f"Number cell ({i}, {j}) with value {puzzle[i][j]}: "
                                  f"Has {trap_count} trap neighbors "
                                  f"{'✓' if trap_count == int(puzzle[i][j]) else '✗'}")
    
    # Check gem cell constraints
    for i in range(height):
        for j in range(width):
            if solution[i][j] == consts.GEM_CELL:
                neighbors = solver_utils.get_neighbors(i, j, height, width)
                
                trap_neighbors = [
                    (ni, nj) for ni, nj in neighbors 
                    if solution[ni][nj] == consts.TRAP_CELL
                ]
                
                non_empty_neighbors = [
                    (ni, nj) for ni, nj in neighbors 
                    if solution[ni][nj] != consts.EMPTY_CELL
                ]
                
                if trap_neighbors:
                    explanation.append(f"Gem cell ({i}, {j}): Has trap neighbors at {trap_neighbors} ✗")
                else:
                    explanation.append(f"Gem cell ({i}, {j}): Has no trap neighbors ✓")
                
                if non_empty_neighbors:
                    explanation.append(f"Gem cell ({i}, {j}): Has non-empty neighbors ✓")
                else:
                    explanation.append(f"Gem cell ({i}, {j}): Has no non-empty neighbors ✗")
    
    # Check unreachable cell constraints
    for i in range(height):
        for j in range(width):
            neighbors = solver_utils.get_neighbors(i, j, height, width)
            all_neighbors_empty = all(solution[ni][nj] == consts.EMPTY_CELL for ni, nj in neighbors)
            
            if all_neighbors_empty:
                explanation.append(f"Cell ({i}, {j}): All neighbors empty, should be empty "
                                  f"{'✓' if solution[i][j] == consts.EMPTY_CELL else '✗'}")
    
    return explanation

def main():
    """Main function to demonstrate CNF constraints."""
    print("Gem Hunter CNF Constraint Explanation")
    print("====================================")
    print("1. General CNF constraints explanation")
    print("2. Concrete example for a small grid")
    print("3. Generate specific CNF example")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == '1':
        explanation = generate_cnf_explanation()
        print(explanation)
        
    elif choice == '2':
        explanation = explain_cnf_for_example_grid()
        print(explanation)
        
    elif choice == '3':
        size = int(input("Enter grid size (2-5 recommended): ") or "3")
        explanation = generate_specific_cnf_example(size)
        print(explanation)
        
    elif choice == '4':
        return
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
