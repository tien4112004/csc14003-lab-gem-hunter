import random
import numpy as np
import os
import consts

def get_neighbors(i, j, height, width):
    neighbors = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            is_current_cell = (di == 0 and dj == 0)
            if is_current_cell:
                continue
            
            next_i, next_j = i + di, j + dj
            is_valid_cell = (0 <= next_i < height and 0 <= next_j < width)
            if is_valid_cell:
                neighbors.append((next_i, next_j))
    
    return neighbors

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
                neighbors = get_neighbors(i, j, height, width)
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
                
                neighbors = get_neighbors(i, j, height, width)
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

def save_map_to_file(map_data, filename):
    """
    Save a map and its solution.
    Ensures that existing files are not overwritten by creating unique filenames.
    """
    puzzle = map_data['puzzle']
    solution = map_data['solution']
    
    solution_dir = os.path.join(os.path.dirname(filename), 'solution_from_generator')
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)
    
    base_filename = os.path.basename(filename)
    base_name, ext = os.path.splitext(base_filename)
    counter = 1    
    while os.path.exists(filename):
        new_base_name = f"{base_name}_{counter}{ext}"
        filename = os.path.join(os.path.dirname(filename), new_base_name)
        counter += 1
    solution_filename = os.path.join(solution_dir, os.path.basename(filename))

    if os.path.exists(solution_filename):
        os.remove(solution_filename)
    
    with open(filename, 'w') as f:
        f.write(f"{map_data['height']} {map_data['width']}\n")
        for row in puzzle:
            f.write(','.join(row) + '\n')
    
    with open(solution_filename, 'w') as f:
        f.write(f"{map_data['height']} {map_data['width']}\n")
        for row in solution:
            f.write(','.join(row) + '\n')
    
    return filename

def main():
    """Generate maps."""
    print("Gem Hunter Map Generator")
    print("By Thanh-Tien Phan - 22120368")
    print("This program generates maps for the Gem Hunter game.")
    print("Note: Map size should be in range [3; 25] for readability.")
    print("=======================")
    
    try:
        num_maps = int(input("Number of maps to be generated [default: 3] ") or "3")
        min_size = int(input("Minimum map size? [default: 4] ") or "4")
        max_size = int(input("Maximum map size? [default: 8] ") or "8")
        trap_probability = float(input("Trap probability (0.0-1.0)? [default: 0.25] ") or "0.25")
        output_dir = input("Output directory? [default: maps] ") or "maps"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for i in range(num_maps):
            map_size = random.randint(min_size, max_size)
            
            print(f"Generating map {i+1}/{num_maps} - Size: {map_size}x{map_size}")

            map_data = generate_map(map_size, map_size, trap_probability)
            
            # Save map
            filename = os.path.join(output_dir, f"map_{map_size}x{map_size}_{i+1}.txt")
            save_map_to_file(map_data, filename)
            print(f"Map saved to {filename}")
        
    except KeyboardInterrupt:
        print("\nMap generation cancelled.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    # TODO: Add a command line argument to specify the number of maps to generate