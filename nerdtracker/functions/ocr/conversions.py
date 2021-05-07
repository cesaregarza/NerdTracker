from cv2 import cvtColor
from numpy import array

def pil_to_cv2(pil_image, color_space_conversion_code, **kwargs):
    """Converts PIL image to CV2

    Args:
        pil_image (Image): PIL Image object
        color_space_conversion_code (cv2.COLOR_SPACE_CONVERSION): a color space conversion code to use

    Returns:
        np.ndarray: numpy array of the converted PIL image
    """

    image_array = array(pil_image)
    return cvtColor(image_array[:, :, ::-1], color_space_conversion_code, **kwargs)