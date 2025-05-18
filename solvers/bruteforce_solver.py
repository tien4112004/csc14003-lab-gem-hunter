import time
import consts
from pysat.formula import CNF

class BruteForceSolver:
    def __init__(self, puzzle, dimacs_file=None):
        """
        Initialize a brute force solver for the Gem Hunter puzzle.
        
        Args:
            puzzle (list): 2D grid representing the puzzle map
            dimacs_file (str, optional): Path to DIMACS file containing the CNF formula
        """
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.empty_cells = []
        self.dimacs_file = dimacs_file
        self.cnf = None
        
        for i in range(self.height):
            for j in range(self.width):
                if puzzle[i][j] == consts.EMPTY_CELL:
                    self.empty_cells.append((i, j))
        
        if dimacs_file:
            self.load_dimacs(dimacs_file)
    
    def load_dimacs(self, dimacs_file):
        """
        Load CNF formula from a DIMACS file.
        
        Args:
            dimacs_file (str): Path to DIMACS file
            
        Returns:
            bool: True if file was loaded successfully, False otherwise
        """
        try:
            self.cnf = CNF(from_file=dimacs_file)
            self.dimacs_file = dimacs_file
            self.clauses = self.cnf.clauses
            return True
        except Exception as e:
            print(f"Error loading DIMACS file: {e}")
            return False
    
    def check_solution(self, assignment):
        """Check if an assignment satisfies all clauses."""
        for clause in self.clauses:
            satisfied = False
            for literal in clause:
                var = abs(literal)
                if (literal > 0 and assignment[var]) or (literal < 0 and not assignment[var]):
                    satisfied = True
                    break
            
            if not satisfied:
                return False
        return True
    
    def solve(self):
        """Try all possible trap configurations until a solution is found."""
        if not self.cnf:
            print("No CNF formula loaded.")
            return None, 0, False
            
        start_time = time.time()
        solution_grid = [row[:] for row in self.puzzle]
        
        num_empty = len(self.empty_cells)
        total_combinations = 2 ** num_empty
        
        if total_combinations > consts.WARNING_COMBINATION_COUNT:
            print(f"Warning: Limited to {consts.MAX_COMBINATION_COUNT} out of {total_combinations} combinations")

        combinations_count = 0

        for mask in range(total_combinations):
            assignment = {}
            for i in range(1, self.width * self.height + 1):
                assignment[i] = False  
            
            for idx, (row, col) in enumerate(self.empty_cells):
                var = row * self.width + col + 1
                assignment[var] = ((mask >> idx) & 1) == 1  # True = trap, False = gem
            
            if self.check_solution(assignment):
                for row, col in self.empty_cells:
                    var = row * self.width + col + 1
                    cell_type = consts.TRAP_CELL if assignment[var] else consts.GEM_CELL
                    solution_grid[row][col] = cell_type
                
                solving_time = time.time() - start_time
                return solution_grid, solving_time, True
            
            combinations_count += 1
            if combinations_count % consts.PROGRESS_UPDATE_INTERVAL == 0:
                print(f"\rProcessed {combinations_count} combinations...", end='', flush=True)
            if combinations_count >= consts.MAX_COMBINATION_COUNT:
                print(f"Processed {combinations_count} combinations, stopping to avoid long computation.")
                break
        
        solving_time = time.time() - start_time
        return solution_grid, solving_time, False