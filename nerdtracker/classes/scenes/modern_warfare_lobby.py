from .scene import Scene
from .describer import SceneDescriber
from typing import Dict, Tuple
import numpy as np
import cv2

class ModernWarfareScene(Scene):
    def __init__(self, scene_description:SceneDescriber, **kwargs) -> None:
        """Scene for a Modern Warfare lobby

        Args:
            scene_description (SceneDescriber): Scene description
        """
        self.scene_description = scene_description
    
    def check_if_in_lobby(self, screenshot: np.ndarray) -> bool:
        """Checks if the player is in the lobby

        Args:
            screenshot (np.array): Screenshot of the game

        Returns:
            bool: True if the player is in the lobby, False otherwise
        """
        #Read the black and white logo template
        logo_template = self.scene_description.get_lobby_icon()

        #Crop the screenshot based on scene description
        y1, y2, x1, x2 = self.scene_description.get_lobby_limits()
        cropped_screenshot = screenshot.copy()[y1:y2, x1:x2, :]

        #Create a copy of the input frame in hSV form
        hsv_frame       = cv2.cvtColor(cropped_screenshot, cv2.COLOR_BGR2HSV)
        thresholds = (60, 40, 100) #(Hue, Saturation, Value)

        #Create a binarized version of the frame by applying multiple masks simultaneously
        accumulated_mask    = None

        #Iterate through each of the thresholds and apply each mask
        for i, thresh in enumerate(thresholds):
            mask = hsv_frame[:, :, i] > thresh
            if accumulated_mask is None:
                accumulated_mask = mask
            else:
                accumulated_mask &= mask
        
        binary_frame = accumulated_mask.astype(np.uint8)

        #Match the template with the binary frame
        result = cv2.matchTemplate(binary_frame, logo_template, cv2.TM_CCOEFF_NORMED)

        #return whether the maximum of the result is greater than our match threshold of 0.8
        return np.amax(result) > 0.8
    
    def read_each_line(self, screenshot: np.ndarray) -> list:
        
        #Crop the screenshot based on scene description
        y1, y2, x1, x2      = self.scene_description.get_player_list_limits()
        cropped_screenshot  = screenshot.copy()[y1:y2, x1:x2, :]

        #Create a gray image copy to be used for locating icons
        gray_frame = cv2.cvtColor(cropped_screenshot, cv2.COLOR_BGR2GRAY)

        controller_types = [
            ("mouse",       self.scene_description.get_mouse_icon()),
            ("controller",  self.scene_description.get_controller_icon()),
        ]

        full_locations = []
        for controller_type, icon in controller_types:
            
            template_height, template_width = icon.shape

            #Use matchTemplate to find the template in the frame
            result = cv2.matchTemplate(gray_frame, icon, cv2.TM_CCOEFF_NORMED)

            #Identify the points where the templates are located on the image portion based on the threshold
            threshold = 0.7
            template_locations = np.where(result > threshold)

            #Identify the amount of templates located, and move on if there are none
            amount_located = len(template_locations[0])
            if amount_located == 0:
                continue

            #Create an array that is going to be passed on with each row when we use tesseract
            shape_array = [
                [template_height] * amount_located,
                [template_width]  * amount_located,
                [controller_type] * amount_located,
            ]

            #Add it to the list we initialized earlier
            full_locations += [[*template_locations, *shape_array]]