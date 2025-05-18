import time
from utils.io import load_map, save_solution
from solvers.sat_solver import SATSolver
from solvers.backtracking_solvers import BacktrackingSolver
from solvers.bruteforce_solver import BruteForceSolver
from utils.solver_utils import print_grid
from cnf_generator import MapToCNF

def solve_map(filename, solver_type='all'):
    """
    Solve a map using the specified solver or all solvers.
    
    Args:
        filename (str): Path to the map file
        solver_type (str): Type of solver to use ('sat', 'bf', 'bt', or 'all')
        
    Returns:
        dict: Results from each solver that was run
    """
    puzzle, height, width = load_map(filename)
    
    print(f"Loaded map from {filename} ({height}x{width})")
    print("\nPuzzle:")
    print_grid(puzzle)
    
    results = {}
    solver_types = ['sat', 'bf', 'bt']
    
    print("Generating CNF formula...")
    cnf_start = time.time()
    cnf_path = f"cnf/{filename.split('/')[-1].replace('.txt', '.cnf')}"
    converter = MapToCNF((puzzle, width, height))
    converter.convert_to_cnf()
    converter.to_dimacs(cnf_path)
    cnf_time = time.time() - cnf_start
    print(f"CNF generation completed in {cnf_time:.6f} seconds")
    
    for solver in solver_types:
        if solver == 'sat':
            print("\n" + "="*50)
            print("Solving using SAT solver...")
            solver_obj = SATSolver(puzzle, dimacs_file=cnf_path)
            
        elif solver == 'bf':
            print("\n" + "="*50)
            print("Solving using Brute Force solver...")
            solver_obj = BruteForceSolver(puzzle, dimacs_file=cnf_path)
            
        elif solver == 'bt':
            print("\n" + "="*50)
            print("Solving using Backtracking solver...")
            solver_obj = BacktrackingSolver(puzzle, dimacs_file=cnf_path)
            
        else:
            print(f"Unknown solver type: {solver}")
            continue
        
        try:
            solution, solving_time, found_solution = solver_obj.solve()
            results[solver] = {
                'solution': solution,
                'time': solving_time,
                'success': found_solution
            }
            
            if found_solution:
                print(f"\nSolution found in {solving_time:.6f} seconds:")
                print_grid(solution)
                
                solution_file = save_solution(filename, solution, height, width, solver_name=solver.upper())
                print(f"Solution saved to {solution_file}")
            else:
                print(f"\nNo solution found after {solving_time:.6f} seconds.")
                
        except Exception as e:
            print(f"Error with {solver} solver: {e}")
            results[solver] = {
                'solution': None,
                'time': 0,
                'success': False,
                'error': str(e)
            }
    
    if len(results) > 1:
        print("\n" + "="*50)
        print("COMPARISON OF SOLVERS:")
        print("-"*50)
        print(f"{'Solver':<15} {'Success':<10} {'Time (seconds)':<15}")
        print("-"*50)
        
        for solver, data in results.items():
            success = "✓" if data['success'] else "✗"
            time_str = f"{data['time']:.6f}" if data['success'] else "N/A"
            print(f"{solver.upper():<15} {success:<10} {time_str:<15}")

        compare_solutions(results)

    return results

def compare_solutions(solutions):
    """
    Compare solutions from different solvers to check if they match.
    
    Args:
        solutions: Dictionary of solutions from different solvers
        
    Returns:
        bool: True if all solutions match, False otherwise
    """
    valid_solutions = {solver: data['solution'] 
                       for solver, data in solutions.items() 
                       if data['success'] and data['solution']}
    
    if len(valid_solutions) <= 1:
        return True
    
    reference_solver = list(valid_solutions.keys())[0]
    reference_solution = valid_solutions[reference_solver]
    
    differences = {}
    all_match = True
    
    for solver, solution in valid_solutions.items():
        if solver == reference_solver:
            continue
            
        is_same = True
        diff_cells = []
        
        for i in range(len(reference_solution)):
            for j in range(len(reference_solution[0])):
                if reference_solution[i][j] != solution[i][j]:
                    is_same = False
                    diff_cells.append((i, j, reference_solution[i][j], solution[i][j]))
        
        if not is_same:
            all_match = False
            differences[solver] = diff_cells
    
    if not all_match:
        print("\n" + "="*50)
        print("SOLUTION DIFFERENCES DETECTED:")
        print("-"*50)
        
        for solver, diffs in differences.items():
            print(f"\nDifferences between {reference_solver.upper()} and {solver.upper()}:")
            for i, j, ref_val, sol_val in diffs:
                print(f"  Position ({i},{j}): {ref_val} vs {sol_val}")
    else:
        print("\nAll solutions match! ✓")
    
    return all_match

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        solver_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        solve_map(filename, solver_type)
    else:
        print("Usage: python solve.py <map_file> [solver_type]")
        print("Solver types: sat, bf, bt, all (default)")