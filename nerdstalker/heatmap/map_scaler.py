import numpy as np
from skimage import transform

def map_autoscaler(map_coordinates, image_coordinates):

    #Turn the coordinates into numpy arrays
    map_coordinates     = np.array(map_coordinates)
    image_coordinates   = np.array(image_coordinates)

    #Estimate the affine transform given the inputs (map coordinates) and the outputs (image coordinates)
    affine_transform = transform.estimate_transform("affine", map_coordinates, image_coordinates)

    #Return the rotation, scale, shear, and translation
    return affine_transform