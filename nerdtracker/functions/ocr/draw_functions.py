import numpy as np
from cv2 import rectangle

def draw_rectangle_percent(image, left, top, width, height, color, thickness = -1, percent_type = "relative"):

    #Obtain the base height and base width, to be used for the calculations
    image_height, image_width = image.shape
    top_pixel   = np.round(top * image_height).astype(int)
    left_pixel  = np.round(left * image_width).astype(int)

    if not percent_type in ["relative", "absolute"]:
        raise ValueError("percent_type will only accept 'relative' or 'absolute' values")
    
    base_width  = np.round(width * image_width)  .astype(int)
    base_height = np.round(height * image_height).astype(int)

    if percent_type == "relative":
        bottom_pixel    = top  + base_height
        right_pixel     = left + base_width
    else:
        bottom_pixel    = base_height
        right_pixel     = base_width
    
    args = [image.copy(), (left_pixel, top_pixel), (right_pixel, bottom_pixel), color, thickness]
    return rectangle(*args)