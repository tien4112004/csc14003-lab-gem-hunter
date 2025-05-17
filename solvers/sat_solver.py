"""
SAT Solver implementation for the Gem Hunter game using pysat.

This module implements a SAT solver for the Gem Hunter game rules:
1. Number cells must have exactly that many trap cells surrounding them
2. Unreachable cells (surrounded by all empty cells) remain empty
3. Gem cells have no trap neighbors, and at least one non-empty neighbor
"""

import itertools
import time
from pysat.formula import CNF
from pysat.solvers import Solver

import consts

class SATSolver:
    def __init__(self, puzzle):
        """
        Initialize a SAT solver for the Gem Hunter puzzle.
        
        Args:
            puzzle (list): 2D grid representing the puzzle map
        """
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.cnf = CNF()
        
        # Variable mapping
        # Each cell can be:
        # - Trap (T) -> variable with index 3*cell_idx + 0
        # - Gem (G)  -> variable with index 3*cell_idx + 1
        # - Empty (_) -> variable with index 3*cell_idx + 2
        self.var_mapping = {}
        self.inverse_mapping = {}
        
        self._initialize_variable_mapping()
        
    def _initialize_variable_mapping(self):
        """Initialize variable mapping for cells in the puzzle."""
        var_idx = 1  # SAT variables are 1-indexed
        
        for i in range(self.height):
            for j in range(self.width):
                # Variables for each cell state (trap, gem, empty)
                self.var_mapping[(i, j, 'T')] = var_idx
                self.inverse_mapping[var_idx] = (i, j, 'T')
                var_idx += 1
                
                self.var_mapping[(i, j, 'G')] = var_idx
                self.inverse_mapping[var_idx] = (i, j, 'G')
                var_idx += 1
                
                self.var_mapping[(i, j, '_')] = var_idx
                self.inverse_mapping[var_idx] = (i, j, '_')
                var_idx += 1
                
    def _get_neighbors(self, i, j):
        """Get valid neighboring cells for cell (i, j)."""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                # Skip the cell itself
                if di == 0 and dj == 0:
                    continue
                
                ni, nj = i + di, j + dj
                # Check if neighbor is within bounds
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.append((ni, nj))
        
        return neighbors
    
    def _add_cell_has_one_state(self, i, j):
        """Add clauses to ensure cell (i, j) has exactly one state (T, G, or _)."""
        # At least one state
        self.cnf.append([
            self.var_mapping[(i, j, 'T')],
            self.var_mapping[(i, j, 'G')],
            self.var_mapping[(i, j, '_')]
        ])
        
        # At most one state (no two states can be true simultaneously)
        self.cnf.append([-self.var_mapping[(i, j, 'T')], -self.var_mapping[(i, j, 'G')]])
        self.cnf.append([-self.var_mapping[(i, j, 'T')], -self.var_mapping[(i, j, '_')]])
        self.cnf.append([-self.var_mapping[(i, j, 'G')], -self.var_mapping[(i, j, '_')]])
    
    def _add_fixed_cell_constraints(self, i, j, cell_value):
        """Add constraints for cells with fixed values in the puzzle."""
        if cell_value.isdigit():
            # Number cells remain number cells (not T, G, or _)
            self.cnf.append([-self.var_mapping[(i, j, 'T')]])
            self.cnf.append([-self.var_mapping[(i, j, 'G')]])
            self.cnf.append([-self.var_mapping[(i, j, '_')]])
            
            # Add constraint for the exact number of surrounding traps
            trap_count = int(cell_value)
            neighbors = self._get_neighbors(i, j)
            
            # Generate all combinations of neighbor cells that could be traps
            trap_vars = [self.var_mapping[(ni, nj, 'T')] for ni, nj in neighbors]
            
            # Add constraints for exactly trap_count traps among neighbors
            self._add_cardinality_constraint(trap_vars, trap_count)
    
    def _add_cardinality_constraint(self, variables, k):
        """
        Add clauses to ensure exactly k variables out of the given list are true.
        This implements the cardinality constraint using the binomial encoding approach.
        """
        n = len(variables)
        
        # No more than k
        for combo in itertools.combinations(variables, k + 1):
            self.cnf.append([-v for v in combo])
        
        # At least k
        for combo in itertools.combinations(variables, n - k + 1):
            self.cnf.append([v for v in combo])
    
    def _add_gem_constraints(self, i, j):
        """
        Add constraints for a gem cell:
        - No trap neighbors
        - At least one non-empty neighbor
        """
        neighbors = self._get_neighbors(i, j)
        
        # If cell is gem, none of its neighbors can be traps
        for ni, nj in neighbors:
            self.cnf.append([
                -self.var_mapping[(i, j, 'G')], 
                -self.var_mapping[(ni, nj, 'T')]
            ])
        
        # A gem cell must have at least one non-empty neighbor
        non_empty_neighbor_vars = []
        for ni, nj in neighbors:
            # A non-empty neighbor is a neighbor that's not empty
            non_empty_var = -self.var_mapping[(ni, nj, '_')]
            non_empty_neighbor_vars.append(non_empty_var)
        
        # At least one neighbor must be non-empty
        if non_empty_neighbor_vars:
            self.cnf.append([-self.var_mapping[(i, j, 'G')]] + non_empty_neighbor_vars)
    
    def _add_unreachable_cell_constraints(self, i, j):
        """Add constraints for unreachable cells."""
        neighbors = self._get_neighbors(i, j)
        
        # Check if all neighbors are empty; if so, this cell must be empty
        empty_neighbor_vars = [self.var_mapping[(ni, nj, '_')] for ni, nj in neighbors]
        
        # Add constraint: if all neighbors are empty, this cell must be empty
        if empty_neighbor_vars:
            # Convert ~(A ∧ B ∧ C ∧ ...) ∨ E into clauses: (~A ∨ E) ∧ (~B ∨ E) ∧ ...
            for var in empty_neighbor_vars:
                self.cnf.append([-var, self.var_mapping[(i, j, '_')]])
                
    def generate_cnf(self):
        """Generate the CNF formula for the puzzle."""
        # Add basic constraints for all cells
        for i in range(self.height):
            for j in range(self.width):
                # Each cell has exactly one state
                self._add_cell_has_one_state(i, j)
                
                # Add constraints for fixed cells (numbers)
                if self.puzzle[i][j] != consts.EMPTY_CELL:
                    self._add_fixed_cell_constraints(i, j, self.puzzle[i][j])
                    
                # Add gem cell constraints
                self._add_gem_constraints(i, j)
                
                # Add unreachable cell constraints
                self._add_unreachable_cell_constraints(i, j)
        
        # Remove duplicate clauses
        clauses_set = set(tuple(clause) for clause in self.cnf.clauses)
        self.cnf.clauses = [list(clause) for clause in clauses_set]
        
        return self.cnf
    
    def solve(self):
        """
        Solve the puzzle using the SAT solver.
        
        Returns:
            tuple: (solution grid, solving time in seconds, was solution found)
        """
        # Generate the CNF formula if not already generated
        if not self.cnf.clauses:
            self.generate_cnf()
        
        start_time = time.time()
        solution_grid = [[consts.EMPTY_CELL for _ in range(self.width)] for _ in range(self.height)]
        
        # Create a SAT solver and add the CNF formula
        solver = Solver(name='g4')
        solver.append_formula(self.cnf)
        
        # Solve the formula
        is_satisfiable = solver.solve()
        
        if is_satisfiable:
            # Extract solution from the model
            model = solver.get_model()
            
            for var in model:
                if var > 0:  # Only consider positive literals (true variables)
                    i, j, state = self.inverse_mapping[var]
                    solution_grid[i][j] = state
            
            # Preserve the original number cells
            for i in range(self.height):
                for j in range(self.width):
                    if self.puzzle[i][j] not in [consts.EMPTY_CELL, consts.TRAP_CELL, consts.GEM_CELL]:
                        solution_grid[i][j] = self.puzzle[i][j]
        
        # Calculate solving time
        solving_time = time.time() - start_time
        
        return solution_grid, solving_time, is_satisfiable

    def get_cnf_stats(self):
        """Get statistics about the CNF formula."""
        if not self.cnf.clauses:
            self.generate_cnf()
            
        return {
            'variables': self.cnf.nv,
            'clauses': len(self.cnf.clauses)
        }
        
    def export_cnf(self, filename):
        """Export the CNF formula to a DIMACS file."""
        if not self.cnf.clauses:
            self.generate_cnf()
            
        self.cnf.to_file(filename)
        
    def get_cnf_clauses_string(self):
        """Get a readable string representation of the CNF clauses."""
        if not self.cnf.clauses:
            self.generate_cnf()
            
        result = []
        
        for clause in self.cnf.clauses:
            clause_str = " ∨ ".join([
                f"{'¬' if lit < 0 else ''}{self.inverse_mapping[abs(lit)]}" 
                for lit in clause
            ])
            result.append(f"({clause_str})")
            
        return " ∧ ".join(result)
