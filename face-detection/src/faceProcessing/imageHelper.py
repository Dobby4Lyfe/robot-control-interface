import datetime
import io

from PIL import Image

DATETIME_STR_FORMAT = "%Y-%m-%d_%H:%M:%S.%f"


def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()


def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))
