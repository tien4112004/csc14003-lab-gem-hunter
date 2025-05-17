import time
import consts
from pysat.formula import CNF
from utils.solver_utils import unflatten

class BacktrackingSolver:
    def __init__(self, puzzle, dimacs_file=None):
        """
        Initialize a backtracking solver for the Gem Hunter puzzle.
        
        Args:
            puzzle (list): 2D grid representing the puzzle map
            dimacs_file (str): Path to DIMACS file containing the CNF formula
        """
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.solution_grid = [row[:] for row in puzzle]
        self.cnf = None
        
        # Find empty cells to assign
        self.empty_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if puzzle[i][j] == consts.EMPTY_CELL:
                    self.empty_cells.append((i, j))
        
        # Load CNF formula
        if dimacs_file:
            self.load_dimacs(dimacs_file)
    
    def load_dimacs(self, dimacs_file):
        """Load CNF formula from a DIMACS file."""
        try:
            self.cnf = CNF(from_file=dimacs_file)
            self.clauses = self.cnf.clauses
            return True
        except Exception as e:
            print(f"Error loading DIMACS file: {e}")
            return False
    
    def is_consistent(self, assignment, var, value):
        """
        Check if assigning value to var is consistent with current assignment.
        
        Args:
            assignment: Current partial assignment
            var: Variable to assign
            value: Value to assign (True or False)
            
        Returns:
            bool: True if assignment is consistent with all clauses
        """
        # Make a temporary assignment
        temp_assignment = assignment.copy()
        temp_assignment[var] = value
        
        # Check all clauses that contain this variable
        for clause in self.clauses:
            # Check if clause contains this variable
            if var in [abs(lit) for lit in clause]:
                # Check if clause is satisfied
                satisfied = False
                unassigned = False
                
                for literal in clause:
                    lit_var = abs(literal)
                    is_positive = literal > 0
                    
                    if lit_var in temp_assignment:
                        var_value = temp_assignment[lit_var]
                        if var_value is None:
                            unassigned = True
                            continue
                        if (is_positive and var_value) or (not is_positive and not var_value):
                            satisfied = True
                            break
                
                # If clause is not satisfied and has no unassigned variables, it's inconsistent
                if not satisfied and not unassigned:
                    return False
        
        return True
    
    def backtrack_search(self, assignment, index):
        """
        Recursive backtracking search.
        
        Args:
            assignment: Current partial assignment
            index: Current index in the empty_cells list
            
        Returns:
            bool: True if a valid solution is found
        """
        # If all variables are assigned, we're done
        if index >= len(self.empty_cells):
            return True
        
        # Get the next unassigned variable
        row, col = self.empty_cells[index]
        var = row * self.width + col + 1
        
        # Try assigning False (gem) first
        if self.is_consistent(assignment, var, False):
            assignment[var] = False
            self.solution_grid[row][col] = consts.GEM_CELL
            
            if self.backtrack_search(assignment, index + 1):
                return True
        
        # If False didn't work, try True (trap)
        if self.is_consistent(assignment, var, True):
            assignment[var] = True
            self.solution_grid[row][col] = consts.TRAP_CELL
            
            if self.backtrack_search(assignment, index + 1):
                return True
        
        # If neither works, undo this assignment and backtrack
        assignment[var] = None
        self.solution_grid[row][col] = consts.EMPTY_CELL
        return False
    
    def solve(self):
        """
        Solve the puzzle using backtracking.
        
        Returns:
            tuple: (solution grid, solving time in seconds, was solution found)
        """
        if not self.cnf:
            print("No CNF formula loaded.")
            return self.solution_grid, 0, False
        
        start_time = time.time()
        
        # Initialize empty assignment
        assignment = {}
        for i in range(1, self.height * self.width + 1):
            assignment[i] = None
        
        # Start with original puzzle
        self.solution_grid = [row[:] for row in self.puzzle]
        
        # Run backtracking search
        found_solution = self.backtrack_search(assignment, 0)
        
        solving_time = time.time() - start_time
        
        if found_solution:
            # Mark any remaining empty cells as gems
            for i in range(self.height):
                for j in range(self.width):
                    if self.solution_grid[i][j] == consts.EMPTY_CELL and self.puzzle[i][j] == consts.EMPTY_CELL:
                        self.solution_grid[i][j] = consts.GEM_CELL
            
            return self.solution_grid, solving_time, True
        else:
            return self.solution_grid, solving_time, False