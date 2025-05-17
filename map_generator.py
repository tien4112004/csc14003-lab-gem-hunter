import random
import numpy as np
import os
import consts
import utils.solver_utils as solver_utils

def generate_map(height, width, trap_probability=0.25):
    """
    Generate a Gem Hunter map with the specified dimensions.
    
    Parameters:
    - height: Height of the map
    - width: Width of the map
    - trap_probability: Probability of a cell being a trap (0.0-1.0)
    
    Returns:
    - Dictionary containing puzzle and solution maps
    """
    solution = np.full((height, width), consts.EMPTY_CELL, dtype=object)
    
    trap_layout = np.zeros((height, width), dtype=bool)
    for i in range(height):
        for j in range(width):
            trap_layout[i, j] = random.random() < trap_probability
            if trap_layout[i, j]:
                solution[i, j] = consts.TRAP_CELL
    
    for i in range(height):
        for j in range(width):
            is_trap_cell = trap_layout[i, j]
            if not is_trap_cell:
                neighbors = solver_utils.get_neighbors(i, j, height, width)
                trap_count = sum(trap_layout[ni, nj] for ni, nj in neighbors)
                
                if trap_count > consts.ZERO_COUNT:
                    solution[i, j] = str(trap_count)
    
    # Find all gems cell in the map
    # A cell is a gem when all surrounding cells are number cells, gem cells, or empty
    # (i.e., no surrounding traps)
    updated = True
    while updated:
        updated = False
        for i in range(height):
            for j in range(width):
                if solution[i, j] != consts.EMPTY_CELL:
                    continue
                
                neighbors = solver_utils.get_neighbors(i, j, height, width)
                has_number = False
                has_trap = False
                
                for next_i, next_j in neighbors:
                    if solution[next_i, next_j] == consts.TRAP_CELL:
                        has_trap = True
                        break
                    elif solution[next_i, next_j] not in [consts.EMPTY_CELL, consts.GEM_CELL]:  # It's a number
                        has_number = True
                
                # If current cell has a number neighbor but no trap neighbors, it's a gem
                if has_number and not has_trap:
                    solution[i, j] = consts.GEM_CELL
                    updated = True
    
    # Create map from generated solution    
    puzzle = np.full((height, width), consts.EMPTY_CELL, dtype=object)
    for i in range(height):
        for j in range(width):
            if solution[i, j] not in [consts.EMPTY_CELL, consts.TRAP_CELL, consts.GEM_CELL]:
                puzzle[i, j] = solution[i, j]
    
    puzzle_map = [list(row) for row in puzzle]
    solution_map = [list(row) for row in solution]
    
    return {
        'puzzle': puzzle_map,
        'solution': solution_map,
        'height': height,
        'width': width
    }

def save_map(map_data, size=None, probability=None, map_dir="maps", name_suffix=None):
    """
    Save a map using a standardized naming convention and avoiding overwriting.
    
    Parameters:
    - map_data: Map data dictionary from generate_map
    - size: Map size (optional, for filename)
    - probability: Trap probability (optional, for filename)
    - map_dir: Directory to save the map in
    - name_suffix: Optional suffix for the filename
    
    Returns:
    - Path to the saved map file
    """
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
        
    solution_dir = os.path.join(map_dir, 'solution_from_generator')
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)
    

    height = map_data.get('height', size)
    width = map_data.get('width', size)
    
    size_part = f"map_{size}x{size}" if size else f"map_{height}x{width}"
    prob_part = f"_{int(probability*100)}p" if probability else ""
    suffix_part = f"_{name_suffix}" if name_suffix else ""
    
    base_name = f"{size_part}{prob_part}{suffix_part}.txt"
    filename = os.path.join(map_dir, base_name)
    
    counter = 1
    while os.path.exists(filename):
        filename = os.path.join(map_dir, f"{base_name[:-4]}_{counter}.txt")
        counter += 1
    
    with open(filename, consts.FILE_WRITE_MODE) as f:
        f.write(f"{height} {width}\n")
        for row in map_data['puzzle']:
            f.write(','.join(row) + '\n')
    
    solution_filename = os.path.join(solution_dir, os.path.basename(filename))
    with open(solution_filename, consts.FILE_WRITE_MODE) as f:
        f.write(f"{height} {width}\n")
        for row in map_data['solution']:
            f.write(','.join(row) + '\n')
    
    return filename

def generate_and_save_map(height, width, trap_probability=0.25, 
                         map_dir="maps", name_suffix=None, show_solution=False):
    """
    Generate a map and save it in one operation.
    
    Parameters:
    - height: Height of the map
    - width: Width of the map
    - trap_probability: Probability of a cell being a trap (0.0-1.0)
    - map_dir: Directory to save the map in
    - name_suffix: Optional suffix for the filename
    - show_solution: Whether to print the solution to the console
    
    Returns:
    - Dictionary with saved_file path and the generated map_data
    """
    print(f"Generating {height}x{width} map with trap probability {trap_probability}...")
    map_data = generate_map(height, width, trap_probability)
    
    saved_file = save_map(
        map_data, 
        size=height if height == width else None,
        probability=trap_probability,
        map_dir=map_dir,
        name_suffix=name_suffix
    )
    
    print(f"Map saved to {saved_file}")
    
    return {
        'saved_file': saved_file,
        'map_data': map_data
    }

def main():
    """Main function for standalone map generation."""
    try:
        num_maps = int(input("Number of maps to be generated [default: 1] ") or "1")
        min_size = int(input("Minimum map size? [default: 8] ") or "8")
        max_size = int(input("Maximum map size? [default: 8] ") or "8")
        trap_probability = float(input("Trap probability (0.0-1.0)? [default: 0.25] ") or "0.25")
        output_dir = input("Output directory? [default: maps] ") or "maps"
        
        for i in range(num_maps):
            map_size = random.randint(min_size, max_size)
            
            result = generate_and_save_map(
                map_size, map_size, 
                trap_probability, 
                map_dir=output_dir,
                name_suffix=f"{i+1}"
            )
                        
    except KeyboardInterrupt:
        print("\nMap generation interrupted.")
    except Exception as e:
        print(f"\nError during map generation: {e}")
    finally:
        print("\nMap generation complete.")

if __name__ == "__main__":
    main()
