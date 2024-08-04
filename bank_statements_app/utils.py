from typing import Tuple
import os
import cv2
import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from pdf2image import convert_from_bytes, convert_from_path

def get_img(uploaded_file):
    # convert file bytes into cv2 image
    file_bytes = np.asarray(bytearray(uploaded_file), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    return img


def convert_pdf_to_image(filename: str | Path | bytes, size: Tuple[int, int] | int = None):
    # * returns back a list of images according to the pdf pages
    if type(filename) in (str, Path):
        pdf_pages = convert_from_path(filename, 300, size=size, thread_count=os.cpu_count())
    elif type(filename) is bytes:
        pdf_pages = convert_from_bytes(filename, 300, size=size, thread_count=os.cpu_count())
    else:
        return []
    return [np.asarray(page) for page in pdf_pages]

def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized Base64 string
    """

    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def filter_color(img, lower_val, upper_val):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # define range of black color in HSV

    lower_val = lower_val

    upper_val = upper_val

    # Threshold the HSV image to get only black colors

    mask = cv2.inRange(hsv, lower_val, upper_val)

    # Bitwise-AND mask and original image

    res = cv2.bitwise_not(mask)
    return res

if __name__ == "__main__":
    filename = "app/docs/DOUYIN GROUP(HK) LIMITED-NR1.pdf"
    pdf_pages = convert_pdf_to_image(filename)
    print(pdf_pages)
    
    
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


def save_csv_file(
    dfs: list[pd.DataFrame],
    filename: str,
):
    df = pd.concat(dfs, ignore_index=True)
    filename = f"{int(datetime.now().timestamp())}_{filename}.csv"
    df.to_csv(filename, index=False)
    
    return filename