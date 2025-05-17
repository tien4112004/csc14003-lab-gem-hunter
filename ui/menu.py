import os
import sys
from colorama import Fore, Style

from utils.io import clear_screen, get_map_files, load_map, save_solution
from utils.cnf_explanation import print_grid, explain_solution, generate_cnf_explanation
import map_generator
from solvers.sat_solver import SATSolver

def main_menu():
    """Display the main menu and return the selected option."""
    clear_screen()
    options = [
        "Generate New Map",
        "Select Map to Solve",
        "Run Benchmarks",
        "View CNF Explanation",
        "Exit"
    ]
    
    print("\n" + "="*50)
    print("               GEM HUNTER")
    print("="*50)
    print("\nSelect an option:")
    
    for i, option in enumerate(options):
        print(f"  {i+1}. {option}")
    
    print("\nEnter your choice (1-5):")
    
    while True:
        try:
            choice = input("> ")
            if choice.lower() in ('q', 'quit', 'exit'):
                return 4  # Exit option
            
            choice = int(choice) - 1
            if 0 <= choice < len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

def map_selection_menu():
    """Display a menu to select a map and return the selected map file."""
    map_files = get_map_files()
    if not map_files:
        print("No maps found in the maps/ directory!")
        input("Press Enter to continue...")
        return None
    
    clear_screen()
    print("\n" + "="*50)
    print("               MAP SELECTION")
    print("="*50)
    print("\nSelect a map:")
    
    for i, map_file in enumerate(map_files):
        print(f"  {i+1}. {map_file}")
    
    print("\n  0. Return to main menu")
    print("\nEnter your choice:")
    
    while True:
        try:
            choice = input("> ")
            if choice.lower() in ('q', 'quit', 'exit', '0'):
                return None
            
            choice = int(choice) - 1
            if 0 <= choice < len(map_files):
                return os.path.join("maps", map_files[choice])
            else:
                print(f"Please enter a number between 0 and {len(map_files)}.")
        except ValueError:
            print("Please enter a valid number.")

def generate_map_menu():
    """Display the map generation menu and handle the generation process."""
    clear_screen()
    print("\n" + "="*50)
    print("               GENERATE NEW MAP")
    print("="*50)
    
    try:
        map_generator.main()
    except Exception as e:
        print(f"\nError during map generation: {e}")
    finally:
        print("\nReturning to main menu...")
        input("Press Enter to continue...")

def solver_selection_menu():
    """Display a menu to select a solver and return the selected solver type."""
    clear_screen()
    print("\n" + "="*50)
    print("               SELECT SOLVER")
    print("="*50)
    print("\nChoose solver:")
    
    solvers = [
        "SAT Solver",
        "Brute Force",
        "Backtracking"
    ]
    
    for i, solver in enumerate(solvers):
        print(f"  {i+1}. {solver}")
    
    print("\n  0. Return to main menu")
    print("\nEnter your choice:")
    
    while True:
        try:
            choice = input("> ")
            if choice.lower() in ('q', 'quit', 'exit', '0'):
                return None
            
            choice = int(choice) - 1
            if choice == 0:
                return "sat"
            elif choice == 1:
                return "bf"
            elif choice == 2:
                return "bt"
            else:
                print("Please enter a number between 0 and 3.")
        except ValueError:
            print("Please enter a valid number.")

def benchmark_menu():
    """Display the benchmark menu and handle benchmarking."""
    from utils.benchmark import run_benchmark, benchmark_multiple_maps, print_benchmark_table, plot_benchmark_results
    
    clear_screen()
    print("\n" + "="*50)
    print("               BENCHMARKING")
    print("="*50)
    
    print("1. Benchmark a single map")
    print("2. Benchmark all maps in directory")
    print("0. Return to main menu")
    
    choice = input("\nEnter your choice (0-2): ")
    
    if choice == '1':
        map_file = map_selection_menu()
        
        if map_file:
            clear_screen()
            print("\n" + "="*50)
            print("               BENCHMARKING")
            print("="*50)
            print(f"\nBenchmarking {os.path.basename(map_file)}...")
            
            results = run_benchmark(map_file, verbose=True)
            print("\nBenchmark complete. Press Enter to continue...")
            input()
    
    elif choice == '2':
        clear_screen()
        print("\n" + "="*50)
        print("               BENCHMARK ALL MAPS")
        print("="*50)
        
        map_dir = input("\nEnter directory containing maps [default: maps]: ") or "maps"
        if not os.path.exists(map_dir):
            print(f"Directory '{map_dir}' does not exist!")
            input("\nPress Enter to continue...")
            return
        
        map_files = [os.path.join(map_dir, f) for f in get_map_files(map_dir)]
        
        if not map_files:
            print(f"No map files found in '{map_dir}'!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nFound {len(map_files)} map files.")
        verbose = input("Show detailed results? (y/n) [default: n]: ").lower() == 'y'
        
        results = benchmark_multiple_maps(
            map_files, 
            output_file=os.path.join(map_dir, "benchmark_results.csv"),
            verbose=verbose
        )
        
        print("\nBenchmark Results Summary:")
        print_benchmark_table(results)
        
        plot = input("\nGenerate performance plot? (y/n) [default: y]: ")
        if plot.lower() != 'n':
            plot_benchmark_results(
                results, 
                output_file=os.path.join(map_dir, "benchmark_results.png")
            )
            print(f"\nPlot saved to {os.path.join(map_dir, 'benchmark_results.png')}")
        
        input("\nPress Enter to continue...")

# TODO: Fix this function
def cnf_explanation_menu():
    """Display the CNF explanation menu and handle CNF explanations."""
    clear_screen()
    print("\n" + "="*50)
    print("               CNF EXPLANATIONS")
    print("="*50)
    
    print("1. General explanation of CNF constraints")
    print("2. Example for a small grid")
    print("0. Return to main menu")
    
    choice = input("\nEnter your choice (0-2): ")
    
    if choice == '1':
        clear_screen()
        print("\n" + "="*50)
        print("               CNF CONSTRAINTS")
        print("="*50)
        
        explanation = generate_cnf_explanation()
        print(explanation)
        
        input("\nPress Enter to continue...")
    
    elif choice == '2':
        clear_screen()
        print("\n" + "="*50)
        print("               CNF EXAMPLE")
        print("="*50)
        
        size = input("\nEnter grid size (2-5 recommended) [default: 3]: ")
        size = int(size) if size.strip() else 3
        
        # Create a small example grid
        puzzle = [["_" for _ in range(size)] for _ in range(size)]
        
        # Add some numbers
        puzzle[0][1] = "2"  # Top middle
        puzzle[1][0] = "1"  # Middle left
        
        print("\nExample Grid:")
        print_grid(puzzle)
        
        # Solve the grid
        solver = SATSolver(puzzle)
        solver.generate_cnf()
        
        # Display statistics
        stats = solver.get_cnf_stats()
        print(f"\nCNF Statistics:")
        print(f"- Variables: {stats['variables']}")
        print(f"- Clauses: {stats['clauses']}")
        
        # Show sample clauses
        print("\nSample CNF Clauses:")
        for idx, clause in enumerate(solver.cnf.clauses[:10]):
            clause_str = " ∨ ".join([
                f"{'¬' if lit < 0 else ''}{solver.inverse_mapping[abs(lit)]}" 
                for lit in clause
            ])
            print(f"{idx+1}. ({clause_str})")
        
        if len(solver.cnf.clauses) > 10:
            print(f"... and {len(solver.cnf.clauses) - 10} more clauses.")
        
        input("\nPress Enter to continue...")