from PIL import Image, ImageDraw, ImageFont
import numpy as np

class Function_Dictionary_Class:
    
    bins = 50
    color_percentile_list = [
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        95,
        99,
        99.9
    ]
    start_hue           = 150
    end_hue             = 0
    rect_width          = 60
    start_legend_x      = -60
    start_legend_y      = 50
    font_path           = r"/System/Library/Fonts/Supplemental/Rockwell.ttc"
    font_encoding       = None
    text_stroke_width   = 2
    text_size           = 20
    
    def update(self, **kwargs):
        """Updates the attributes in this function based on key word input
        """
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

def generate_color_list(num_colors, start_hue, end_hue):
    step_height = (end_hue - start_hue) / (num_colors + 1)
    return [f"hsv({int(start_hue + step_height * i)}, 100%, 100%)" for i in range(num_colors)]

def generate_histogram(xy_values, image_path, **kwargs):
    """Generate a histogram image

    Args:
        xy_values (float[:,:]): List of pixel xy values to generate the histogram. Must already be transformed!
        image_path (str): String pointing at the map image to use

    Returns:
        PIL.Image: Generated PIL Image
    """
    
    func_dict.update(**kwargs)

    #Open the image and create a draw object
    image   = Image.open(image_path)
    draw    = ImageDraw.Draw(image)

    #Generate the histogram
    z, x_bins, y_bins = np.histogram2d(xy_values[:, 0], xy_values[:, 1], bins=func_dict.bins)

    #Generate a linear version of z and filter out zeroes. This will be used to calculate colors used
    z_linear = z.reshape(1, -1)
    z_linear = z_linear[z_linear > 0]

    #Calculate the percentile
    percentile_list = np.percentile(z_linear, func_dict.color_percentile_list)

    #Generate color list
    color_list = generate_color_list(len(percentile_list), func_dict.start_hue, func_dict.end_hue)

    def return_first_matching_index(input_value):
        for i in range(len(percentile_list)):
            try:
                if percentile_list[i + 1] > input_value:
                    return i
            except IndexError:
                return -1
        
        return -1
    
    for ix in range(len(x_bins) - 1):
        start_x = x_bins[ix]
        end_x   = x_bins[ix + 1]

        for iy in range(len(y_bins) - 1):
            start_y = y_bins[iy]
            end_y   = y_bins[iy + 1]

            #If z is zero, we don't want to actually draw anything
            if (z_value := z[ix][iy]) == 0:
                continue
            
            fill_color = color_list[return_first_matching_index(z_value)]
            draw.rectangle([start_x, start_y, end_x, end_y], fill=fill_color)
    
    #Create a copy and blend the two images
    image_copy = Image.open(image_path)

    return_image = Image.blend(image, image_copy, alpha=0.6)
    return_draw  = ImageDraw.Draw(return_image)

    #Generate a unique percentile list, a unique color list, and the lowest percentile associated with each color
    unique_percentile_list = np.unique(percentile_list)
    unique_color_list       = [color_list[return_first_matching_index(x)] for x in unique_percentile_list[::-1]]
    low_percentile_list     = [percentile_list[return_first_matching_index(x)] for x in unique_percentile_list[::-1]]

    #Generate the font
    font = ImageFont.truetype(func_dict.font_path, size=func_dict.text_size, encoding=func_dict.font_encoding)

    #Generate the legend, starting from the last value and moving backwards
    for color, percent_value, i in zip(unique_color_list, low_percentile_list, range(len(low_percentile_list))):

        #Dictate legend rectangle positions
        start_x = return_image.width + func_dict.start_legend_x - ((i+1) * func_dict.rect_width)
        start_y = func_dict.start_legend_y
        end_x   = start_x + func_dict.rect_width
        end_y   = start_y + func_dict.rect_width

        #Fix text, appending a "+" for the last value that represents the 99.9th percentile or above
        fixed_percent_value = f"{np.format_float_positional(percent_value, precision=0)[:-1]}{'+' if i == 0 else ''}"
        
        #Generate the text and center it.
        text_width, text_height = return_draw.textsize(fixed_percent_value, font=font, stroke_width=func_dict.text_stroke_width)
        text_x = int((start_x + end_x - text_width) / 2)
        text_y = int((start_y + end_y - text_height) / 2)

        #Draw the rectangle in the appropriate color, as well as the text that goes with it
        return_draw.rectangle([start_x, start_y, end_x, end_y], fill=color)
        return_draw.text([text_x, text_y], fixed_percent_value, font=font, fill="white", stroke_width=func_dict.text_stroke_width, stroke_fill="black")

    return return_image