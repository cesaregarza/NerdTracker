import numpy as np
from .transform_class import TransformClass

def map_autoscaler(map_coordinates, image_coordinates):

    #Reshape image coordinates into the appropriate form, and find the dimensionality
    target_vector   = image_coordinates.reshape((-1, 1))
    dimensions      = map_coordinates.shape[1] + 1

    #Transform the points in the map space into the appropriate form
    matrix_list     = []
    for coordinate in map_coordinates:
        base_vector                 = np.zeros(2 * dimensions)
        base_vector[:dimensions]    = [*coordinate, 1]
        matrix_list                += [base_vector.copy()]
        matrix_list                += [np.roll(base_vector, dimensions)]
    
    matrix                      = np.array(matrix_list)
    
    #Computer affine transformation using least squares
    solution_vector, _, _, _    = np.linalg.lstsq(matrix, target_vector, rcond=None)

    #Attach a [0, 0, ..., 0, 1] row at the bottom of the solution vector, then reshape correctly
    final_vector                = np.zeros(dimensions)
    final_vector[-1]            = 1
    solution_matrix             = np.vstack([solution_vector.reshape(dimensions - 1, -1), final_vector])

    return TransformClass(solution_matrix)