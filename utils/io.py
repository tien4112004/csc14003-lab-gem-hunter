import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_map_files(map_dir="maps"):
    """Get a list of all map files in the maps directory."""
    if not os.path.exists(map_dir):
        return []
    
    map_files = [f for f in os.listdir(map_dir) if os.path.isfile(os.path.join(map_dir, f)) and f.endswith('.txt')]
    return sorted(map_files)

def load_map(filename) -> tuple[list[list[str]], int, int]:
    """Load a map file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    height, width = map(int, lines[0].strip().split())
    puzzle = []
    
    for i in range(1, height + 1):
        row = lines[i].strip().split(',')
        puzzle.append(row)
    
    return puzzle, height, width

def save_solution(filename, solution, height, width, solver_name) -> str:
    """
    Save a solution to a file.
    
    Args:
        filename (str): The original map file name.
        solution (list): The solution to save.
        height (int): The height of the map.
        width (int): The width of the map.

    Returns:
        str: The path to the saved solution file.
    """
    filename = f"{filename}_{solver_name}.txt"
    solution_dir = os.path.join(os.path.dirname(filename), 'solution')
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)
    
    solution_file = os.path.join(solution_dir, os.path.basename(filename))
    
    with open(solution_file, 'w') as f:
        f.write(f"{height} {width}\n")
        for row in solution:
            f.write(','.join(row) + '\n')
    
    return solution_file