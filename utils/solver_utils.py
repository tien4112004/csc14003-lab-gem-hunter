from typing import List, Tuple

import consts

def get_neighbors(i, j, height, width) -> List[Tuple[int, int]]:
    """Get valid neighboring cells for cell (i, j)."""
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

def print_grid(grid: List[List[str]]) -> None:
    """Print a 2D grid."""
    for row in grid:
        print(" ".join(row))
    print()  # Add an extra newline for better readability

def flatten(n, row, col) -> int:
    """
    Convert a cell position to a variable number
    """
    return row * n + col + consts.CNF_STARTING_VAR

def unflatten(n, var) -> tuple[int, int]:
    """
    Convert a variable number back to a cell position (row, col)
    """
    var -= consts.CNF_STARTING_VAR
    row = var // n
    col = var % n
    return row, col