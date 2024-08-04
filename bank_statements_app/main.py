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
from utils import convert_pdf_to_image, get_img, save_csv_file, delete_file, filter_color, convert_to_base64
from llm import llm, evaluate
from google_genai import gemini
from parsers.HSBC_bank_statement import hsbc_parser
from parsers.InHouse_FS import inhouse_parser

def get_pages(uploaded_file):
    filename = uploaded_file.name.split(".")[0]
    if uploaded_file.name.split(".")[1].lower() == "pdf":
        pdf_pages = convert_pdf_to_image(uploaded_file.read())
    else:
        pdf_pages = [get_img(uploaded_file.read())]
    
    return pdf_pages, filename

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

def invoke_llm(pages_processed_text, progress_bar, parser):
    progress_bar.progress(0, "Creating CSV data")
    # json_output = {}
    # num_pages = len(pages_processed_text)
    context = '\n\n'.join([text for _, text in pages_processed_text.items()])
    # st.write(context)
    # for page_num, img in enumerate(pdf_pages):
    #     response = llm_ocr(image=[{
    #             "type": "image_url",
    #             "image_url": {"url": f"data:image/jpeg;base64,{convert_to_base64(img)}"},
    #         }])
    #     context += response["response"] + "\n\n"
    #         # json_output[page_num] = response
    #         # progress_bar.progress(
    #         #     page_num / num_pages, "Creating CSV data"
    #         # )
    response = llm(context_text=context, parser=parser)
    accuracy = evaluate(context, response)
    progress_bar.progress(100, "Done")
    # return json_output
    return response, accuracy["accuracy"]

def gemini_invoke(pages_processed_text, progress_bar):
    progress_bar.progress(0, "Creating CSV data")
    # json_output = {}
    # num_pages = len(pages_processed_text)
    # response = None
    # for page_num, text in pages_processed_text.items():
    #     response = gemini([text, f"{response.text if response else None}"])
    #     # json_output[page_num] = json.loads(response.text)
    #     progress_bar.progress(
    #         page_num / num_pages, "Creating CSV data"
    #     )
    context = '\n\n'.join([text for _, text in pages_processed_text.items()])
    # response = gemini([Image.fromarray(page.astype("uint8"), "RGB") for page in pages])
    response = gemini([context])
    progress_bar.progress(100, "Done")
    return response.text

def main(uploaded_file):
    filename = uploaded_file.name.split(".")[0]
    match filename:
        case "HSBC bank statement":
            start = datetime.now()
            progress_bar = st.progress(0, "Extracting info from document")
            pdf_pages, filename = get_pages(uploaded_file)
            pages = pdf_pages[:5]
            pages_processed_text = ocr(pages, filename, progress_bar)
            json_output, accuracy = invoke_llm(pages_processed_text, progress_bar, hsbc_parser)
            end = datetime.now()
            st.text(f"processed {len(pages)} pages")
            st.text(
                f"Time taken: {(str(round((end - start).seconds/60, 2)) + ' minutes') if (end - start).seconds > 60 else (str((end - start).seconds) + ' seconds')}"
            )
            st.text(f"Accuracy: {accuracy}")
            st.json(json_output)
        
        case "Inhouse FS":
            start = datetime.now()
            progress_bar = st.progress(0, "Extracting info from document")
            pdf_pages, filename = get_pages(uploaded_file)
            pages_processed_text = ocr(pdf_pages, filename, progress_bar)
            json_output, accuracy = invoke_llm(pages_processed_text, progress_bar, inhouse_parser)
            end = datetime.now()
            st.text(f"processed {len(pdf_pages)} pages")
            st.text(
                f"Time taken: {(str(round((end - start).seconds/60, 2)) + ' minutes') if (end - start).seconds > 60 else (str((end - start).seconds) + ' seconds')}"
            )
            st.text(f"Accuracy: {accuracy}")
            st.json(json_output)
        
        case "eStatement1 - mask":
            start = datetime.now()
            progress_bar = st.progress(0, "Extracting info from document")
            pdf_pages, filename = get_pages(uploaded_file)
            pages_processed_text = ocr(pdf_pages, filename, progress_bar)
            json_output, accuracy = invoke_llm(pages_processed_text, progress_bar, hsbc_parser)
            end = datetime.now()
            st.text(f"processed {len(pdf_pages)} pages")
            st.text(
                f"Time taken: {(str(round((end - start).seconds/60, 2)) + ' minutes') if (end - start).seconds > 60 else (str((end - start).seconds) + ' seconds')}"
            )
            st.text(f"Accuracy: {accuracy}")
            st.json(json_output)
    
document = st.file_uploader("Upload Document")

if document:
    success = st.button("Extract", on_click=main, args=[document])