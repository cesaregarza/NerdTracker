import pytesseract, cv2, re, pathlib
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

base_path = pathlib.Path(__file__).parent

def construct_path(path):
    return str( (base_path / path).resolve())

class Function_Dictionary_Class:
    config_value                = r"--psm 6 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#0123456789[]_-"
    regex_string                = r"[a-zA-Z0-9][a-zA-Z0-9_-]+(#\d+)?"

    mouse_template_path         = construct_path(r"..\patterns\mouse_mono.png")
    controller_template_path    = construct_path(r"..\patterns\controller_mono.png")
    horizontal_offset           = 142
    negative_horizontal_offset  = 66
    template_threshold          = 0.9
    row_width                   = 40
    blur_kernel                 = (8,8)
    weighted_value              = 2
    weighted_gamma              = 110
    alpha_primary               = 1.5
    beta_primary                = -120
    second_blur_kernel          = (2,2)
    alpha_secondary             = 1.9
    beta_secondary              = -130

    def update(self, **kwargs):
        """Updates the attributes in this function based on key word input
        """
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

def read_each_entry_modern_warfare(image, **kwargs):

    #Override existing default values based on input kwargs
    func_dict.update(**kwargs)

    #Load the two templates we'll use first to locate each row
    mouse_template      = [cv2.imread(func_dict.mouse_template_path, cv2.IMREAD_GRAYSCALE), "mouse"]
    controller_template = [cv2.imread(func_dict.controller_template_path, cv2.IMREAD_GRAYSCALE), "controller"]

    #Create a gray image copy to be used for locating the image
    gray_image          = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Initialize a list that will be used to store the full locations of each row
    full_locations = []

    for template, controller_type in [mouse_template, controller_template]:
        template_height, template_width = template.shape
        
        #Use matchTemplate to identify where the template is located in the image
        result          = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)

        #Identify the points where the templates are located on the image portion based on the threshold
        template_locations  = np.where(result > func_dict.template_threshold)

        #Identify the amount of templates located, and move onto the next one if none were located
        amount_located      = len(template_locations[0])

        if amount_located == 0:
            continue
        
        #Create an array that is going to be passed on with each row when we use tesseract
        shape_array                     = [
            [template_height] * amount_located,
            [template_width]  * amount_located,
            [controller_type] * amount_located
        ]

        #Add it to the list we initialized earlier
        full_locations     += [[*template_locations, *shape_array]]
    
    #Concatenate them to create a numpy array
    try:
        full_locations = np.concatenate(full_locations, axis=1)
    except ValueError:
        return [[]]
    
    #Sort the locations by the y value
    full_locations = full_locations[:, full_locations[0].astype(int).argsort()]
    
    #Subtract the average color through blurring, convert to gray, then increase contrast while decreasing brightness.
    #Finally, add slight blur to reduce noise caused by the weird square tiles of the background and invert to make it easier
    #for tesseract to read
    blurred_image   = cv2.blur(image, ksize=func_dict.blur_kernel)
    modified_image  = cv2.addWeighted(image, func_dict.weighted_value, blurred_image, -func_dict.weighted_value, func_dict.weighted_gamma)
    modified_image  = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)
    modified_image  = cv2.convertScaleAbs(modified_image, alpha=func_dict.alpha_primary, beta=func_dict.beta_primary)
    modified_image  = cv2.blur(modified_image, ksize=func_dict.second_blur_kernel)
    modified_image  = 255 - modified_image
    modified_image  = cv2.convertScaleAbs(modified_image, alpha=func_dict.alpha_secondary, beta=func_dict.beta_secondary)
    read_values = []
    
    for located_tuple in zip(*full_locations):
        #Because np.concat will infer the dtype and controller_type is a string, we must convert all of the values to integers
        y_value, x_value, template_width, template_height = [int(val) for val in located_tuple[:-1]]

        #Calculate both the y value of the start of the row and the y value of the end of it
        start_y_value   = y_value + template_height // 2 - func_dict.row_width // 2
        end_y_value     = start_y_value + func_dict.row_width

        #Bound the upper and lower values of the y values
        start_y_value   = max(start_y_value, 0)
        end_y_value     = min(end_y_value, image.shape[0])
        
        #Calculate both the start of the section that will contain the text and the end
        start_x_value   =  func_dict.horizontal_offset
        end_x_value     = -func_dict.negative_horizontal_offset

        #Create a cropped copy of the modified image to be fed into tesseract
        name_box    = modified_image[start_y_value:end_y_value, start_x_value:end_x_value].copy()

        #Read the string using tesseract
        read_string = pytesseract.image_to_string(name_box, config=func_dict.config_value)

        #The string will be read with additional characters before or after the string on occasion, this will fix it
        try:
            parsed_string = re.search(func_dict.regex_string, read_string).group()
        except AttributeError:
            parsed_string = ""

        #Add the parsed string as well as the last value of "located_tuple", which is the controller type
        read_values += [[parsed_string, located_tuple[-1]]]
    
    return read_values