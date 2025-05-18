import time
import consts
from pysat.formula import CNF
from utils.solver_utils import unflatten, get_neighbors

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
        
        self.empty_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if puzzle[i][j] == consts.EMPTY_CELL:
                    self.empty_cells.append((i, j))
        
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
        temp_assignment = assignment.copy()
        temp_assignment[var] = value
        
        # Check all clauses that contain this variable
        for clause in self.clauses:
            # Check if clause contains this variable
            if var not in [abs(lit) for lit in clause]:
                continue

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
        if index >= len(self.empty_cells):
            return True
        
        row, col = self.empty_cells[index]
        var = row * self.width + col + 1
        
        if self.is_consistent(assignment, var, False):
            assignment[var] = False
            self.solution_grid[row][col] = consts.GEM_CELL
            
            if self.backtrack_search(assignment, index + 1):
                return True
        
        if self.is_consistent(assignment, var, True):
            assignment[var] = True
            self.solution_grid[row][col] = consts.TRAP_CELL
            
            if self.backtrack_search(assignment, index + 1):
                return True
        
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
        
        assignment = {}
        for i in range(1, self.height * self.width + 1):
            assignment[i] = None
        
        self.solution_grid = [row[:] for row in self.puzzle]
        
        found_solution = self.backtrack_search(assignment, 0)
        
        solving_time = time.time() - start_time
        
        if not found_solution:
            return self.solution_grid, solving_time, False

        for i in range(self.height):
            for j in range(self.width):
                if self.solution_grid[i][j] == consts.EMPTY_CELL and self.puzzle[i][j] == consts.EMPTY_CELL:
                    has_adjacent_trap_or_num = False
                    neighbors = get_neighbors(i, j, self.height, self.width)
                    for ni, nj in neighbors:
                        print(self.solution_grid[ni][nj])
                        if (self.solution_grid[ni][nj] == consts.TRAP_CELL or 
                            isinstance(self.puzzle[ni][nj], int)):
                            has_adjacent_trap_or_num = True
                            break
            
                    if has_adjacent_trap_or_num:
                        self.solution_grid[i][j] = consts.GEM_CELL
        
        return self.solution_grid, solving_time, True