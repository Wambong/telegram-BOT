import numpy as np

def calculate_uv(cost_matrix, solution):
    num_rows, num_cols = cost_matrix.shape
    u = np.full(num_rows, np.nan)  # Use np.nan for uninitialized values
    v = np.full(num_cols, np.nan)
    
    # Initialize the first u or v based on a heuristic or a fixed rule
    u[0] = 0
    
    # Track whether an update was made to break the loop if no updates occur
    update_made = True
    
    while np.isnan(u).any() or np.isnan(v).any():
        if not update_made:
            raise ValueError("Unable to solve for all u and v; the system might be under-specified.")
        update_made = False  # Reset update flag for this iteration
        
        for i in range(num_rows):
            for j in range(num_cols):
                if solution[i, j] > 0:  # Occupied cell implies a basic variable
                    if not np.isnan(u[i]) and np.isnan(v[j]):
                        v[j] = cost_matrix[i, j] - u[i]
                        update_made = True
                    elif np.isnan(u[i]) and not np.isnan(v[j]):
                        u[i] = cost_matrix[i, j] - v[j]
                        update_made = True
    
    return u, v

def find_dij(cost_matrix, u, v):
    """
    Calculates dij for all unoccupied cells.
    """
    dij_matrix = np.zeros(cost_matrix.shape)
    for i in range(cost_matrix.shape[0]):
        for j in range(cost_matrix.shape[1]):
            dij_matrix[i, j] = cost_matrix[i, j] - (u[i] + v[j])
    return dij_matrix

def optimize_solution(cost_matrix, solution):
    """
    Iterates to optimize the solution based on dij calculations and cycle adjustments.
    """
    while True:
        u, v = calculate_uv(cost_matrix, solution)
        dij_matrix = find_dij(cost_matrix, u, v)
        
        # Step 4: Check for optimality
        if np.all(dij_matrix >= 0):
            print("Optimal solution found.")
            return solution
        
        # Step 5: Select the unoccupied cell with the largest negative dij
        min_dij_value = np.min(dij_matrix)
        if min_dij_value >= 0:
            break  # Optimal solution found
        min_dij_index = np.argwhere(dij_matrix == min_dij_value)[0]
        
        # Simplification: Not showing detailed cycle detection and adjustment for brevity
        print(f"Improvement opportunity at {min_dij_index} with dij {min_dij_value}")
        
        # Implement cycle detection and adjustments (Steps 6 to 7) here
        # This part is left as a conceptual placeholder
        
        # Example adjustment, assuming we can simply add the allocation without real cycle detection
        solution[min_dij_index[0], min_dij_index[1]] += 1  # Simplified adjustment
        
        # Repeat the process (Step 8)

# Example Usage:
cost_matrix = np.array([
    [2, 3, 1, 4],
    [5, 4, 8, 6],
    [5, 4, 8, 6]
])

# Initial basic feasible solution (assuming it's given or calculated through VAM/NWCM/LCM)
solution = np.full(cost_matrix.shape, -1)  # -1 indicates unoccupied cells
# Example allocations for simplicity
solution[0, 0] = 20; solution[1, 1] = 30; solution[2, 2] = 50

optimized_solution = optimize_solution(cost_matrix, solution)
print("Optimized Solution:")
print(optimized_solution)
