from typing import List, Tuple

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
