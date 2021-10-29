import cv2, pathlib
from numpy import amax, uint8
from PIL import Image

base_path = pathlib.Path(__file__).parent

def construct_path(path):
    return str( (base_path / path).resolve())

class Function_Dictionary_Class:

    logo_path               = construct_path("..\patterns\modern_warfare.png")
    hue_threshold           = 60
    saturation_threshold    = 40
    value_threshold         = 100
    match_threshold         = 0.7

    def update(self, **kwargs):
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

def check_if_lobby_screen(image, **kwargs):

    #Update based on 
    func_dict.update(**kwargs)

    #Read the black and white logo template
    logo_template                   = cv2.imread(func_dict.logo_path, cv2.IMREAD_GRAYSCALE)

    #Create a copy of the input frame that's in HSV form
    hsv_frame                       = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #Create a binarized version of the frame by applying multiple masks simultaneously
    thresholds                      = [func_dict.hue_threshold, 
                                       func_dict.saturation_threshold,
                                       func_dict.value_threshold]
    accumulated_mask                = None

    #Iterate through the thresholds, applying each mask
    for i, threshold in enumerate(thresholds):
        mask = hsv_frame[:, :, i] > threshold
        if accumulated_mask is None:
            accumulated_mask = mask
        else:
            accumulated_mask &= mask

    binary_frame                    = accumulated_mask.astype(uint8)
    
    #Match the template with the binary frame
    result                          = cv2.matchTemplate(binary_frame, logo_template, cv2.TM_CCOEFF_NORMED)

    #Return whether the maximum of the result is greater than our threshold, which means it was indeed matched
    return amax(result) > func_dict.match_threshold