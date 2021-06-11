import numpy as np

class TransformClass:
    def __init__(self, matrix):
        self.matrix = matrix
    
    def __repr__(self):
        return_string = f"Transformation Matrix: \n"
        return return_string + np.array2string(self.matrix)
    
    def transform(self, map_coordinates):

        #Append a one vector to the end of the input coordinates in the map space
        ones_vector         = np.ones((map_coordinates.shape[0], 1))
        map_coordinates     = np.hstack([map_coordinates, ones_vector])

        #Multiply the transformation matrix with the transpose of the input map coordinates
        initial_solution    = self.matrix @ map_coordinates.T

        #Transpose back, and drop the column of 1s
        return initial_solution.T[:, :-1]