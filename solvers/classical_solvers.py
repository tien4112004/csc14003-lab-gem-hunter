"""
1. Brute Force: tries all possible combinations of trap and gem placements
2. Backtracking: uses backtracking with constraint propagation for faster solving
"""

import itertools
import time
import numpy as np
import consts
import utils.solver_utils as solver_utils

class BruteForceSolver:
    def __init__(self, puzzle):
        """
        Initialize a brute force solver for the Gem Hunter puzzle.
        
        Args:
            puzzle (list): 2D grid representing the puzzle map
        """
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.empty_cells = []
        
        # Find all empty cells
        for i in range(self.height):
            for j in range(self.width):
                if puzzle[i][j] == consts.EMPTY_CELL:
                    self.empty_cells.append((i, j))
    
    def is_valid_solution(self, solution_grid):
        """Check if a solution grid is valid according to the game rules."""
        # Check number cell constraints
        for i in range(self.height):
            for j in range(self.width):
                cell_value = self.puzzle[i][j]
                
                if cell_value.isdigit():
                    trap_count = 0
                    neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
                    
                    for ni, nj in neighbors:
                        if solution_grid[ni][nj] == consts.TRAP_CELL:
                            trap_count += 1
                    
                    if trap_count != int(cell_value):
                        return False
        
        # Check gem cell constraints
        for i in range(self.height):
            for j in range(self.width):
                if solution_grid[i][j] == consts.GEM_CELL:
                    neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
                    
                    # Gems cannot have trap neighbors
                    if any(solution_grid[ni][nj] == consts.TRAP_CELL for ni, nj in neighbors):
                        return False
                    
                    # Gems must have at least one non-empty neighbor
                    has_non_empty_neighbor = False
                    for ni, nj in neighbors:
                        if solution_grid[ni][nj] != consts.EMPTY_CELL:
                            has_non_empty_neighbor = True
                            break
                    
                    if not has_non_empty_neighbor:
                        return False
        
        # Check unreachable cell constraints
        for i in range(self.height):
            for j in range(self.width):
                neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
                all_neighbors_empty = all(solution_grid[ni][nj] == consts.EMPTY_CELL for ni, nj in neighbors)
                
                if all_neighbors_empty and solution_grid[i][j] != consts.EMPTY_CELL:
                    return False
        
        return True
    
    def solve(self):
        """
        Solve the puzzle using brute force.
        
        Returns:
            tuple: (solution grid, solving time in seconds, was solution found)
        """
        start_time = time.time()
        
        # Initialize solution grid with the given number cells
        solution_grid = [row[:] for row in self.puzzle]
        
        # Try all possible combinations of trap and gem for empty cells
        num_empty_cells = len(self.empty_cells)
        max_combinations = 3 ** num_empty_cells  # Each cell can be EMPTY, TRAP, or GEM
        
        # Limit the maximum number of combinations to avoid excessive computation
        MAX_COMBINATIONS = 1_000_000
        if max_combinations > MAX_COMBINATIONS:
            print(f"Warning: Too many combinations ({max_combinations}). This might take a very long time.")
            print(f"Limiting to {MAX_COMBINATIONS} combinations.")
            max_combinations = MAX_COMBINATIONS
        
        for trap_mask in range(2 ** num_empty_cells):
            # Skip if we've gone over the maximum combinations
            if trap_mask > max_combinations:
                break
                
            # Reset solution grid
            for i, j in self.empty_cells:
                solution_grid[i][j] = consts.EMPTY_CELL
            
            # Place traps according to the current mask
            for idx, (i, j) in enumerate(self.empty_cells):
                if (trap_mask >> idx) & 1:
                    solution_grid[i][j] = consts.TRAP_CELL
                    
            # Infer gems according to game rules
            updated = True
            while updated:
                updated = False
                for i in range(self.height):
                    for j in range(self.width):
                        if solution_grid[i][j] != consts.EMPTY_CELL:
                            continue
                        
                        neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
                        has_number = False
                        has_trap = False
                        
                        for next_i, next_j in neighbors:
                            if solution_grid[next_i][next_j] == consts.TRAP_CELL:
                                has_trap = True
                                break
                            elif solution_grid[next_i][next_j] not in [consts.EMPTY_CELL, consts.GEM_CELL]:  # It's a number
                                has_number = True
                        
                        # If current cell has a number neighbor but no trap neighbors, it's a gem
                        if has_number and not has_trap:
                            solution_grid[i][j] = consts.GEM_CELL
                            updated = True
            
            # Check if the solution is valid
            if self.is_valid_solution(solution_grid):
                solving_time = time.time() - start_time
                return solution_grid, solving_time, True
        
        solving_time = time.time() - start_time
        return None, solving_time, False


class BacktrackingSolver:
    def __init__(self, puzzle):
        """
        Initialize a backtracking solver for the Gem Hunter puzzle.
        
        Args:
            puzzle (list): 2D grid representing the puzzle map
        """
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.solution_grid = [row[:] for row in puzzle]
        
        # Keep track of cells that need assignment
        self.unassigned_cells = []
        for i in range(self.height):
            for j in range(self.width):
                if puzzle[i][j] == consts.EMPTY_CELL:
                    self.unassigned_cells.append((i, j))
    
    def check_number_constraint(self, i, j):
        """Check if a number cell's constraint is satisfied."""
        if not self.puzzle[i][j].isdigit():
            return True
        
        target_trap_count = int(self.puzzle[i][j])
        current_trap_count = 0
        potential_trap_count = 0
        
        neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
        for ni, nj in neighbors:
            if self.solution_grid[ni][nj] == consts.TRAP_CELL:
                current_trap_count += 1
            elif self.solution_grid[ni][nj] == consts.EMPTY_CELL:
                potential_trap_count += 1
        
        # Check if constraint can still be satisfied
        return current_trap_count <= target_trap_count <= current_trap_count + potential_trap_count
    
    def check_gem_constraint(self, i, j):
        """Check if a gem cell's constraints are satisfied."""
        if self.solution_grid[i][j] != consts.GEM_CELL:
            return True
        
        neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
        
        # Check that gem has no trap neighbors
        for ni, nj in neighbors:
            if self.solution_grid[ni][nj] == consts.TRAP_CELL:
                return False
        
        # Check that gem has at least one non-empty neighbor
        has_non_empty_neighbor = False
        all_neighbors_assigned = True
        
        for ni, nj in neighbors:
            if self.solution_grid[ni][nj] != consts.EMPTY_CELL:
                has_non_empty_neighbor = True
            else:
                all_neighbors_assigned = False
        
        # If all neighbors are assigned and none are non-empty, constraint is violated
        if all_neighbors_assigned and not has_non_empty_neighbor:
            return False
        
        return True
    
    def check_unreachable_constraint(self, i, j):
        """Check if an unreachable cell's constraint is satisfied."""
        neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
        
        # If all neighbors are empty, this cell must be empty too
        all_neighbors_empty = True
        all_neighbors_assigned = True
        
        for ni, nj in neighbors:
            if self.solution_grid[ni][nj] != consts.EMPTY_CELL:
                all_neighbors_empty = False
            elif self.solution_grid[ni][nj] == consts.EMPTY_CELL:
                all_neighbors_assigned = False
        
        if all_neighbors_empty and all_neighbors_assigned:
            return self.solution_grid[i][j] == consts.EMPTY_CELL
        
        return True
    
    def is_consistent(self, i, j, value):
        """Check if assigning value to (i, j) is consistent with current assignments."""
        # Temporarily assign the value
        old_value = self.solution_grid[i][j]
        self.solution_grid[i][j] = value
        
        # Check constraints for this cell and its neighbors
        consistent = True
        
        # Check unreachable cell constraint for this cell
        if not self.check_unreachable_constraint(i, j):
            consistent = False
        
        # Check constraints for all number cells affected by this assignment
        if consistent:
            neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
            for ni, nj in neighbors:
                if self.puzzle[ni][nj].isdigit() and not self.check_number_constraint(ni, nj):
                    consistent = False
                    break
                
                # If neighbor is a gem, check its constraints
                if self.solution_grid[ni][nj] == consts.GEM_CELL and not self.check_gem_constraint(ni, nj):
                    consistent = False
                    break
                
                # Check unreachable cell constraint for neighbor
                if not self.check_unreachable_constraint(ni, nj):
                    consistent = False
                    break
        
        # Check gem constraint if this is a gem cell
        if consistent and value == consts.GEM_CELL and not self.check_gem_constraint(i, j):
            consistent = False
            
        # Restore the old value
        self.solution_grid[i][j] = old_value
        
        return consistent
    
    def infer_gems(self):
        """Infer gem cells based on the current assignment."""
        updated = True
        while updated:
            updated = False
            
            for i in range(self.height):
                for j in range(self.width):
                    if self.solution_grid[i][j] != consts.EMPTY_CELL:
                        continue
                        
                    neighbors = solver_utils.get_neighbors(i, j, self.height, self.width)
                    has_number = False
                    has_trap = False
                    
                    for next_i, next_j in neighbors:
                        if self.solution_grid[next_i][next_j] == consts.TRAP_CELL:
                            has_trap = True
                            break
                        elif self.solution_grid[next_i][next_j] not in [consts.EMPTY_CELL, consts.GEM_CELL]:  # It's a number
                            has_number = True
                    
                    # If current cell has a number neighbor but no trap neighbors, it's a gem
                    if has_number and not has_trap:
                        self.solution_grid[i][j] = consts.GEM_CELL
                        updated = True
                        
                        # Remove this cell from unassigned cells
                        if (i, j) in self.unassigned_cells:
                            self.unassigned_cells.remove((i, j))
    
    def backtrack(self, index):
        """
        Recursive backtracking function to find a solution.
        
        Args:
            index: Current index in the unassigned_cells list
            
        Returns:
            bool: True if a valid solution is found, False otherwise
        """
        # If all cells are assigned, check if solution is valid
        if index >= len(self.unassigned_cells):
            return True
        
        i, j = self.unassigned_cells[index]
        
        # Try each possible value (TRAP or EMPTY)
        for value in [consts.TRAP_CELL, consts.EMPTY_CELL]:
            if self.is_consistent(i, j, value):
                self.solution_grid[i][j] = value
                
                # Infer gems after assignment
                self.infer_gems()
                
                # Continue with next unassigned cell
                if self.backtrack(index + 1):
                    return True
                
                # If we reach here, this assignment didn't work
                # Reset this cell and any inferred gems
                self.solution_grid[i][j] = consts.EMPTY_CELL
                
                # Reset all cells to their initial state
                for reset_i, reset_j in self.unassigned_cells[index:]:
                    self.solution_grid[reset_i][reset_j] = consts.EMPTY_CELL
                
        return False
    
    def solve(self):
        """
        Solve the puzzle using backtracking.
        
        Returns:
            tuple: (solution grid, solving time in seconds, was solution found)
        """
        start_time = time.time()
        
        # Initialize solution grid with the original puzzle
        self.solution_grid = [row[:] for row in self.puzzle]
        
        # Infer gems at the start to reduce search space
        self.infer_gems()
        
        # Start backtracking
        found_solution = self.backtrack(0)
        
        solving_time = time.time() - start_time
        
        if found_solution:
            return self.solution_grid, solving_time, True
        else:
            return None, solving_time, False
