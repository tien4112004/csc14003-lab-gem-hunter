from utils.solver_utils import get_neighbors, flatten
import consts
from itertools import combinations
from utils.io import load_map

class MapToCNF:
    def __init__(self, map: tuple):
        """
        Initialize the converter with a grid representing the map
        
        Args:
            map: A tuple containing (grid, width, height) where:
                - grid is a 2D list where each cell contains an integer 1-8 or consts.EMPTY_CELL
                - width is the number of columns
                - height is the number of rows
        """
        self.grid, width, height = map
        self.n = width
        self.clauses = []
        
    def convert_to_cnf(self):
        """Convert the map to CNF clauses with all necessary constraints"""
        unique_clauses_set = set()
        
        for row in range(self.n):
            for col in range(self.n):
                cell = self.grid[row][col]
                
                if cell == consts.EMPTY_CELL:
                    continue
                    
                # assigned cell -> a number -> not a trap
                cell_var = flatten(self.n, row, col)
                unique_clauses_set.add(frozenset([-cell_var]))
                
                cell_int = int(cell)
                neighbors = get_neighbors(row, col, self.n, self.n)            
                unassigned_neighbors = [(r, c) for r, c in neighbors if self.grid[r][c] == consts.EMPTY_CELL]
                neighbor_vars = [flatten(self.n, r, c) for r, c in unassigned_neighbors]
                
                if cell_int == consts.ZERO_VALUE: 
                    for neighbor in neighbor_vars:
                        unique_clauses_set.add(frozenset([-neighbor]))
                elif len(unassigned_neighbors) == consts.ZERO_LENGTH: 
                    continue
                elif len(unassigned_neighbors) == cell_int: # all neighbors are traps
                    for neighbor in neighbor_vars:
                        unique_clauses_set.add(frozenset([neighbor]))
                elif len(unassigned_neighbors) > cell_int:
                    # There is a trap around - at least one neighbor must be a trap
                    unique_clauses_set.add(frozenset(neighbor_vars))

                    # Explain: exactlt k <=> at least k AND at most k

                    # 1. At most cell_int traps: 
                    # For every (cell_int+1) combination, at least one must be safe
                    for comb in combinations(neighbor_vars, cell_int + 1):
                        unique_clauses_set.add(frozenset(-var for var in comb))
                    
                    # 2. At least cell_int traps:
                    # For every (len-cell_int+1) combination, at least one must be a trap
                    for comb in combinations(neighbor_vars, len(neighbor_vars) - cell_int + 1):
                        unique_clauses_set.add(frozenset(var for var in comb))
        
        self.clauses = [list(clause) for clause in unique_clauses_set]
        self.clauses.sort(key=lambda x: (len(x), x)) 

        self.print_report()
        return self.clauses
    
    def to_dimacs(self, output_file=None):
        """
        Convert the CNF clauses to DIMACS format
        
        Args:
            output_file: (Optional) file path to write the DIMACS output.
            
        Returns:
            A string in DIMACS format
        """
        max_var = self.n * self.n
        
        lines = []
        lines.append(f"p cnf {max_var} {len(self.clauses)}")
        for clause in self.clauses:
            lines.append(" ".join(map(str, clause)) + " 0")
        dimacs_str = "\n".join(lines)
        
        if output_file:
            with open(output_file, consts.FILE_WRITE_MODE) as f:
                f.write(dimacs_str)

        return dimacs_str
    
    def print_report(self):
        """Print a report about the CNF conversion process"""
        # assigned_cells = 0
        # neighbor_count = 0
        # unreachable_cells = 0
        
        # for row in range(self.n):
        #     for col in range(self.n):
        #         cell = self.grid[row][col]
                
        #         # Count assigned cells (cells with numbers)
        #         if cell != consts.EMPTY_CELL:
        #             assigned_cells += 1
                
        #         # Count neighbor relationships
        #         cell_neighbors = get_neighbors(row, col, self.n, self.n)
        #         neighbor_count += len(cell_neighbors)
                
        #         # Check for unreachable empty cells
        #         if cell == consts.EMPTY_CELL:
        #             has_assigned_neighbor = False
        #             for nr, nc in cell_neighbors:
        #                 if self.grid[nr][nc] != consts.EMPTY_CELL:
        #                     has_assigned_neighbor = True
        #                     break
        #             if not has_assigned_neighbor:
        #                 unreachable_cells += 1
        
        grid_size = f"{self.n}x{self.n}"
        total_vars = self.n * self.n
        total_clauses = len(self.clauses)
        
        print(f"Grid size: {grid_size}")
        print(f"Total variables: {total_vars}")
        print(f"Total unique clauses: {total_clauses}")
        

if __name__ == "__main__":
    import os
    import sys
    
    os.makedirs("cnf", exist_ok=True)
    
    if len(sys.argv) > 1:
        map_files = sys.argv[1:]
    else:
        map_dir = "maps"
        map_files = [os.path.join(map_dir, f) for f in os.listdir(map_dir) 
                    if f.endswith(".txt") and os.path.isfile(os.path.join(map_dir, f))]
        
    for map_file in map_files:
        try:
            map_name = os.path.splitext(os.path.basename(map_file))[0]
            output_file = f"cnf/{map_name}.cnf"
            
            print(f"\nProcessing map: {map_name}")
            grid = load_map(map_file)
            print(f"Loaded map: {map_file}")
            
            converter = MapToCNF(grid)
            cnf_clauses = converter.convert_to_cnf()
            converter.print_report()
            
            dimacs_output = converter.to_dimacs(output_file=f"cnf/{output_file}")
            print(f"CNF output written to: cnf/{output_file}")
            
        except Exception as e:
            print(f"Error processing {map_file}: {e}")