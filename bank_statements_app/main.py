import os
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
st.set_page_config(page_title="Pintar - Bank Statement Parser")
st.title(f"{os.getenv('TITLE')}")

from datetime import datetime
from dateutil.parser import parse
import json
from PIL import Image
import pandas as pd
import numpy as np

from process import get_raw_text_from_pages, get_processed_text_from_pages
from utils import convert_pdf_to_image, get_img, save_csv_file, delete_file, filter_color
from llm import llm
from google_genai import gemini

def get_pages(uploaded_file):
    filename = uploaded_file.name.split(".")[0]
    if uploaded_file.name.split(".")[1].lower() == "pdf":
        pdf_pages = convert_pdf_to_image(uploaded_file.read())
    else:
        pdf_pages = [get_img(uploaded_file.read())]
    
    return pdf_pages[:5], filename

def ocr(pdf_pages, filename, progress_bar, filter:bool = False):
    num_pages = len(pdf_pages)
    ## ---------------------------------
    #* Extract raw text from Document
    raw_text = {}
    results = []
    for page_num, page in enumerate(pdf_pages, start=1):
        result, page_text = get_raw_text_from_pages(page, filename, page_num=page_num, save_images=False, filter=True)
        results.append((page, result))
        raw_text[page_num] = page_text
        progress_bar.progress(
            page_num / num_pages, "Extracting info from document"
        )
    progress_bar.progress(100, "Extracting info from document")
    ## ---------------------------------
    ## ---------------------------------
    #* Text Processing
    progress_bar.progress(0, "Processing Text")
    pages_processed_text = {}
    for page_num, (img, result) in enumerate(results, start=1):
        processed_text = get_processed_text_from_pages(img, result)
        pages_processed_text[page_num] = processed_text
        progress_bar.progress(
            page_num / num_pages, "Processing Text"
        )
    progress_bar.progress(100, "Processing Text")
    # st.write(pages_processed_text)
    ## ----------------------------------

    return pages_processed_text

def invoke_llm(pages_processed_text, progress_bar):
    progress_bar.progress(0, "Creating CSV data")
    json_output = {}
    num_pages = len(pages_processed_text)
    context = '\n\n'.join([text for _, text in pages_processed_text.items()])
    st.write(context)
    # for page_num, text in pages_processed_text.items():
    response = llm(context)
        # json_output[page_num] = response
        # progress_bar.progress(
        #     page_num / num_pages, "Creating CSV data"
        # )
    progress_bar.progress(100, "Done")
    # return json_output
    return response

def gemini_invoke(pages, progress_bar):
    progress_bar.progress(0, "Creating CSV data")
    # json_output = {}
    # num_pages = len(pages)
    # for page_num, page in enumerate(pages):
        # response = gemini([Image.fromarray(page.astype("uint8"), "RGB")])
        # json_output[page_num] = json.loads(response.text)
        # progress_bar.progress(
        #     page_num / num_pages, "Creating CSV data"
        # )
    response = gemini([Image.fromarray(page.astype("uint8"), "RGB") for page in pages])
    progress_bar.progress(100, "Done")
    return response.text

def main(uploaded_file):
    start = datetime.now()
    progress_bar = st.progress(0, "Extracting info from document")
    pdf_pages, filename = get_pages(uploaded_file)
    pages_processed_text = ocr(pdf_pages, filename, progress_bar)
    st.json(pages_processed_text)
    json_output = invoke_llm(pages_processed_text, progress_bar)
    # json_output = gemini_invoke(pdf_pages, progress_bar)
    st.json(json_output)
    # df_list = create_dataframe(json_output)
    end = datetime.now()
    st.text(
        f"Time taken: {(str(round((end - start).seconds/60, 2)) + ' minutes') if (end - start).seconds > 60 else (str((end - start).seconds) + ' seconds')}"
    )
    # if os.path.exists(filename):
    #     with open(f"{filename}", "rb") as fp:
    #         st.download_button(
    #             label="Download CSV file",
    #             data=fp,
    #             file_name=filename,
    #             mime="text/csv",
    #         )
    #     delete_file(filename)
    # else:
    #     st.warning("No results found")
document = st.file_uploader("Upload Document")

if document:
    success = st.button("Extract", on_click=main, args=[document])