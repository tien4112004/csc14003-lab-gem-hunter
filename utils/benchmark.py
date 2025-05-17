"""
Benchmarking module for comparing different solver methods 
(SAT solver, brute force, and backtracking).
"""

import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

import consts
from solvers.sat_solver import SATSolver
from solvers.classical_solvers import BruteForceSolver, BacktrackingSolver
from map_generator import generate_map, save_map

def load_map_from_file(filename):
    """Load a puzzle map from a file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    height, width = map(int, lines[0].strip().split())
    puzzle = []
    
    for i in range(1, height + 1):
        row = lines[i].strip().split(',')
        puzzle.append(row)
    
    return puzzle, height, width

def save_solution_to_file(filename, solution_grid, height, width):
    """Save a solution grid to a file."""
    solution_dir = os.path.join(os.path.dirname(filename), 'solution')
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)
    
    solution_filename = os.path.join(solution_dir, os.path.basename(filename))
    
    with open(solution_filename, 'w') as f:
        f.write(f"{height} {width}\n")
        for row in solution_grid:
            f.write(','.join(row) + '\n')
    
    return solution_filename

def verify_solution(puzzle, solution):
    """Verify that a solution is valid according to game rules."""
    height = len(puzzle)
    width = len(puzzle[0]) if height > 0 else 0
    
    # Check number cell constraints
    for i in range(height):
        for j in range(width):
            cell_value = puzzle[i][j]
            
            if cell_value.isdigit():
                # Count traps around this number cell
                trap_count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        
                        ni, nj = i + di, j + dj
                        if 0 <= ni < height and 0 <= nj < width and solution[ni][nj] == consts.TRAP_CELL:
                            trap_count += 1
                
                if trap_count != int(cell_value):
                    return False, f"Number cell at ({i}, {j}) has {trap_count} traps, but should have {cell_value}"
    
    # Check gem cell constraints
    for i in range(height):
        for j in range(width):
            if solution[i][j] == consts.GEM_CELL:
                # Check no traps around gems
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        
                        ni, nj = i + di, j + dj
                        if 0 <= ni < height and 0 <= nj < width and solution[ni][nj] == consts.TRAP_CELL:
                            return False, f"Gem at ({i}, {j}) has a trap neighbor at ({ni}, {nj})"
                
                # Check at least one non-empty neighbor
                has_non_empty_neighbor = False
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        
                        ni, nj = i + di, j + dj
                        if 0 <= ni < height and 0 <= nj < width and solution[ni][nj] != consts.EMPTY_CELL:
                            has_non_empty_neighbor = True
                            break
                
                if not has_non_empty_neighbor:
                    return False, f"Gem at ({i}, {j}) has no non-empty neighbors"
    
    # Check unreachable cell constraints
    for i in range(height):
        for j in range(width):
            all_neighbors_empty = True
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    
                    ni, nj = i + di, j + dj
                    if 0 <= ni < height and 0 <= nj < width and solution[ni][nj] != consts.EMPTY_CELL:
                        all_neighbors_empty = False
                        break
            
            if all_neighbors_empty and solution[i][j] != consts.EMPTY_CELL:
                return False, f"Unreachable cell at ({i}, {j}) should be empty"
    
    return True, "Solution is valid"

def run_benchmark(map_file, verbose=True):
    """
    Run all solvers on a given map and compare their performance.
    
    Args:
        map_file (str): Path to the map file
        verbose (bool): Whether to print detailed results
        
    Returns:
        dict: Benchmark results
    """
    puzzle, height, width = load_map_from_file(map_file)
    
    results = {
        'map_file': map_file,
        'height': height,
        'width': width,
        'sat': {},
        'brute_force': {},
        'backtracking': {}
    }
    
    if verbose:
        print(f"Benchmarking map: {map_file} ({height}x{width})")
    
    # Run SAT solver
    sat_solver = SATSolver(puzzle)
    sat_solution, sat_time, sat_found = sat_solver.solve()
    
    results['sat']['time'] = sat_time
    results['sat']['solution_found'] = sat_found
    results['sat']['cnf_stats'] = sat_solver.get_cnf_stats()
    
    if verbose:
        print(f"SAT Solver: {'Solution found' if sat_found else 'No solution'} in {sat_time:.6f} seconds")
        print(f"  Variables: {results['sat']['cnf_stats']['variables']}")
        print(f"  Clauses: {results['sat']['cnf_stats']['clauses']}")
    
    # Run Brute Force solver (only for small maps)
    if height * width <= 36:  # Only run brute force on small maps
        bf_solver = BruteForceSolver(puzzle)
        bf_solution, bf_time, bf_found = bf_solver.solve()
        
        results['brute_force']['time'] = bf_time
        results['brute_force']['solution_found'] = bf_found
        
        if verbose:
            print(f"Brute Force: {'Solution found' if bf_found else 'No solution'} in {bf_time:.6f} seconds")
    else:
        results['brute_force']['time'] = None
        results['brute_force']['solution_found'] = None
        
        if verbose:
            print(f"Brute Force: Skipped (map too large)")
    
    # Run Backtracking solver
    bt_solver = BacktrackingSolver(puzzle)
    bt_solution, bt_time, bt_found = bt_solver.solve()
    
    results['backtracking']['time'] = bt_time
    results['backtracking']['solution_found'] = bt_found
    
    if verbose:
        print(f"Backtracking: {'Solution found' if bt_found else 'No solution'} in {bt_time:.6f} seconds")
    
    # Verify solution consistency
    if sat_found and bt_found:
        same_solution = all(sat_solution[i][j] == bt_solution[i][j] 
                            for i in range(height) for j in range(width))
        results['solutions_match'] = same_solution
        
        if verbose:
            print(f"Solutions match: {same_solution}")
    
    # Save solution
    if sat_found:
        solution_file = save_solution_to_file(map_file, sat_solution, height, width)
        results['solution_file'] = solution_file
        
        # Verify solution
        is_valid, message = verify_solution(puzzle, sat_solution)
        results['solution_valid'] = is_valid
        
        if verbose:
            print(f"Solution validity: {is_valid} - {message}")
            print(f"Solution saved to {solution_file}")
    
    return results

def benchmark_multiple_maps(map_files, output_file=None, verbose=True):
    """
    Run benchmarks on multiple maps and aggregate results.
    
    Args:
        map_files (list): List of map file paths
        output_file (str): Path to output file for results (CSV)
        verbose (bool): Whether to print detailed results
        
    Returns:
        pd.DataFrame: Aggregated benchmark results
    """
    all_results = []
    
    for map_file in map_files:
        try:
            results = run_benchmark(map_file, verbose)
            all_results.append(results)
            
            if verbose:
                print("-" * 80)
        except Exception as e:
            if verbose:
                print(f"Error benchmarking {map_file}: {e}")
            
            all_results.append({
                'map_file': map_file,
                'error': str(e)
            })
    
    # Convert to dataframe
    df_results = []
    
    for result in all_results:
        if 'error' in result:
            continue
            
        row = {
            'map_file': result['map_file'],
            'size': f"{result['height']}x{result['width']}",
            'sat_time': result['sat']['time'],
            'sat_found': result['sat']['solution_found'],
            'sat_variables': result['sat']['cnf_stats']['variables'],
            'sat_clauses': result['sat']['cnf_stats']['clauses'],
            'brute_force_time': result['brute_force']['time'],
            'brute_force_found': result['brute_force']['solution_found'],
            'backtracking_time': result['backtracking']['time'],
            'backtracking_found': result['backtracking']['solution_found'],
        }
        
        if 'solutions_match' in result:
            row['solutions_match'] = result['solutions_match']
            
        if 'solution_valid' in result:
            row['solution_valid'] = result['solution_valid']
            
        df_results.append(row)
    
    df = pd.DataFrame(df_results)
    
    if output_file:
        df.to_csv(output_file, index=False)
        
        if verbose:
            print(f"Benchmark results saved to {output_file}")
    
    return df

def plot_benchmark_results(results_df, output_file=None):
    """
    Plot benchmark results.
    
    Args:
        results_df (pd.DataFrame): Benchmark results
        output_file (str): Path to output file for plot
    """
    # Prepare data
    sizes = results_df['size'].tolist()
    sat_times = results_df['sat_time'].tolist()
    bf_times = results_df['brute_force_time'].tolist()
    bt_times = results_df['backtracking_time'].tolist()
    
    # Filter out None values
    valid_indices = [i for i, t in enumerate(bf_times) if t is not None]
    valid_sizes = [sizes[i] for i in valid_indices]
    valid_sat_times = [sat_times[i] for i in valid_indices]
    valid_bf_times = [bf_times[i] for i in valid_indices]
    valid_bt_times = [bt_times[i] for i in valid_indices]
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    if valid_sizes:
        plt.semilogy(valid_sizes, valid_sat_times, 'o-', label='SAT Solver')
        plt.semilogy(valid_sizes, valid_bf_times, 's-', label='Brute Force')
        plt.semilogy(valid_sizes, valid_bt_times, '^-', label='Backtracking')
    
    # Plot for all sizes (SAT and backtracking)
    plt.figure(figsize=(10, 6))
    plt.semilogy(sizes, sat_times, 'o-', label='SAT Solver')
    plt.semilogy(sizes, bt_times, '^-', label='Backtracking')
    
    plt.xlabel('Grid Size')
    plt.ylabel('Time (seconds, log scale)')
    plt.title('Solver Performance Comparison')
    plt.legend()
    plt.grid(True)
    
    if output_file:
        plt.savefig(output_file)
        print(f"Plot saved to {output_file}")
    else:
        plt.show()
        
def generate_benchmark_maps(base_dir="benchmark_maps", sizes=None, num_per_size=3):
    """
    Generate maps for benchmarking.
    
    Args:
        base_dir (str): Directory to save the generated maps
        sizes (list): List of map sizes to generate
        num_per_size (int): Number of maps to generate for each size
        
    Returns:
        list: List of generated map file paths
    """
    if sizes is None:
        sizes = [4, 6, 8, 10, 12, 16, 20]
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    map_files = []
    
    for size in sizes:
        for i in range(num_per_size):
            print(f"Generating {size}x{size} map {i+1}/{num_per_size}")
            
            map_data = generate_map(size, size)
            filename = os.path.join(base_dir, f"benchmark_map_{size}x{size}_{i+1}.txt")
            
            save_map(map_data, filename)
            map_files.append(filename)
    
    return map_files

def print_benchmark_table(results_df):
    """Print a formatted table of benchmark results."""
    # Extract relevant columns
    table = results_df[['size', 'sat_time', 'brute_force_time', 'backtracking_time']]
    
    # Fill NaN values
    table = table.fillna("N/A")
    
    # Format times
    for col in ['sat_time', 'brute_force_time', 'backtracking_time']:
        table[col] = table[col].apply(lambda x: f"{x:.6f}s" if isinstance(x, (int, float)) else x)
    
    # Rename columns
    table.columns = ['Grid Size', 'SAT Solver', 'Brute Force', 'Backtracking']
    
    # Print table
    print(tabulate(table, headers='keys', tablefmt='fancy_grid'))

def main():
    """Main function for running benchmarks."""
    # Map sizes to benchmark
    SIZES = [4, 6, 8, 10, 12, 16, 20]
    
    print("Gem Hunter Benchmark")
    print("===================")
    print("1. Generate benchmark maps")
    print("2. Run benchmarks on existing maps")
    print("3. Run benchmarks on a single map")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == '1':
        print("\nGenerating benchmark maps...")
        maps = generate_benchmark_maps(sizes=SIZES)
        print(f"Generated {len(maps)} benchmark maps.")
        
    elif choice == '2':
        map_dir = input("Enter directory containing maps: ")
        if not os.path.exists(map_dir):
            print(f"Directory '{map_dir}' does not exist!")
            return
        
        map_files = [os.path.join(map_dir, f) for f in os.listdir(map_dir) 
                    if os.path.isfile(os.path.join(map_dir, f)) and f.endswith('.txt')]
        
        if not map_files:
            print(f"No .txt files found in '{map_dir}'!")
            return
        
        print(f"Found {len(map_files)} map files.")
        verbose = input("Show detailed results? (y/n): ").lower() == 'y'
        
        results = benchmark_multiple_maps(map_files, 
                                         output_file=os.path.join(map_dir, "benchmark_results.csv"),
                                         verbose=verbose)
        
        print("\nBenchmark Results Summary:")
        print_benchmark_table(results)
        
        plot = input("Generate performance plot? (y/n): ").lower() == 'y'
        if plot:
            plot_benchmark_results(results, 
                                 output_file=os.path.join(map_dir, "benchmark_results.png"))
        
    elif choice == '3':
        map_file = input("Enter path to map file: ")
        if not os.path.exists(map_file):
            print(f"File '{map_file}' does not exist!")
            return
        
        results = run_benchmark(map_file, verbose=True)
        
    elif choice == '4':
        return
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
