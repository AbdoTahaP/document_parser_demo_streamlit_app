import streamlit as st
from paddleocr import PaddleOCR

@st.cache_resource
def get_ocr(use_angle_cls: bool = True, lang: str = "ch"):
    """loads ocr model

    Returns:
        _type_: PaddleOCR
        OCR model
    """
    ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)
    return ocr


get_ocr()