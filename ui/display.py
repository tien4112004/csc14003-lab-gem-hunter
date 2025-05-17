from utils.io import load_map, save_solution
from utils.cnf_explanation import print_grid, explain_solution
from solvers.sat_solver import SATSolver
from solvers.classical_solvers import BruteForceSolver, BacktrackingSolver

def solve_map(filename, solver_type='sat'):
    """
    Solve a map using the specified solver.
    
    Args:
        filename (str): Path to the map file
        solver_type (str): Type of solver to use ('sat', 'bf', or 'bt')
        
    Returns:
        tuple: (solution, solving_time, found_solution)
    """
    puzzle, height, width = load_map(filename)
    
    print(f"Loaded map from {filename} ({height}x{width})")
    print("\nPuzzle:")
    print_grid(puzzle)
    
    if solver_type == 'sat':
        print("\nSolving using SAT solver...")
        solver = SATSolver(puzzle)
    elif solver_type == 'bf':
        print("\nSolving using Brute Force solver...")
        solver = BruteForceSolver(puzzle)
    elif solver_type == 'bt':
        print("\nSolving using Backtracking solver...")
        solver = BacktrackingSolver(puzzle)
    else:
        print(f"Unknown solver type: {solver_type}")
        return None, 0, False
    
    solution, solving_time, found_solution = solver.solve()
    
    if found_solution:
        print(f"\nSolution found in {solving_time:.6f} seconds:")
        print_grid(solution)
        
        solution_file = save_solution(filename, solution, height, width)
        print(f"\nSolution saved to {solution_file}")
        
        # Print explanation
        print("\nExplanation of why the solution is valid:")
        explanations = explain_solution(puzzle, solution)
        for explanation in explanations:
            print(f"- {explanation}")
    else:
        print(f"\nNo solution found after {solving_time:.6f} seconds.")
    
    return solution, solving_time, found_solution