import os
from dotenv import load_dotenv

load_dotenv()
import streamlit as st
st.set_page_config(page_title="Pintar - Document Parser")
st.title(f"{os.getenv('TITLE')}")

from datetime import datetime
from dateutil.parser import parse
import json
from PIL import Image
import pandas as pd

from process import get_raw_text_from_pages, get_processed_text_from_pages
from utils import convert_pdf_to_image, get_img, save_csv_file, delete_file
from llm import llm
# from google_genai import gemini
from GCP import upload

def get_pages(uploaded_file):
    filename = uploaded_file.name.split(".")[0]
    if uploaded_file.name.split(".")[1].lower() == "pdf":
        pdf_pages = convert_pdf_to_image(uploaded_file.read())
    else:
        pdf_pages = [get_img(uploaded_file.read())]
    
    return pdf_pages, filename

def ocr(pdf_pages, filename, progress_bar):
    num_pages = len(pdf_pages)
    ## ---------------------------------
    #* Extract raw text from Document
    raw_text = {}
    results = []
    for page_num, page in enumerate(pdf_pages, start=1):
        result, page_text = get_raw_text_from_pages(page, filename, page_num=page_num, save_images=False)
        results.append((page, result))
        raw_text[page_num] = page_text
        progress_bar.progress(
            page_num / num_pages, "Extracting info from document"
        )
    progress_bar.progress(100, "Extracting info from document")
    # st.write(raw_text)
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
    for page_num, text in pages_processed_text.items():
        response = llm(text)
        json_output[page_num] = response
        progress_bar.progress(
            page_num / num_pages, "Creating CSV data"
        )
    progress_bar.progress(100, "Done")
    return json_output

# def gemini_invoke(pages, progress_bar):
#     progress_bar.progress(0, "Creating CSV data")
#     json_output = {}
#     num_pages = len(pages)
#     for page_num, page in enumerate(pages):
#         response = gemini([Image.fromarray(page.astype("uint8"), "RGB")])
#         json_output[page_num] = json.loads(response.text)
#         progress_bar.progress(
#             page_num / num_pages, "Creating CSV data"
#         )
#     progress_bar.progress(100, "Done")
#     return json_output

def create_dataframe(data):
    df_list = []
    # tax_categories = {
    #     "Sales Tax": "01",
    #     "Service Tax": "02",
    #     "Tourism Tax": "03",
    #     "High-Value Goods Tax": "04",
    #     "Sales Tax on Low Value Goods": "05",
    #     "Not Applicable": "06",
    #     "Tax exemption": "E",
    # }
    tax_categories = {
        "salestax": "01",
        "servicetax": "02",
        "tourismtax": "03",
        "high-valuegoodstax": "04",
        "salestaxonlowvaluegoods": "05",
        "notapplicable": "06",
        "taxexemption": "E",
    }
    city_codes = {
        "All States": "00",
        "Johor": "01",
        "Kedah": "02",
        "Kelantan":"03",	
        "Melaka":"04",
        "Negeri Sembilan":"05",	
        "Pahang":"06",	
        "Pulau Pinang":"07",
        "Perak":"08",
        "Perlis":"09",
        "Selangor":"10",
        "Terengganu":"11",
        "Sabah":"12",
        "Sarawak":"13",
        "Wilayah Persekutuan Kuala Lumpur":"14",
        "Wilayah Persekutuan Labuan":"15",
        "Wilayah Persekutuan Putrajaya":"16",
        "Not Applicable":"17",
    }
    for page_num, json_object in data.items():
        df = pd.DataFrame(json_object)

        #spread the Invoice Lines array
        df[list(df["Invoice Lines"][0].keys())] = [list(item.values()) for item in df["Invoice Lines"]]
        df.drop("Invoice Lines", axis=1, inplace=True)
        
        #Change the date format
        df["Invoice Date"] = df["Invoice Date"].apply(lambda x: parse(x).strftime("%d/%m/%Y"))

        df["Invoice Type"] = df["Invoice Type"].apply(lambda x: "11" if "Invoice" in x or not x else "12" if "Credit" in x else "") if df["Invoice Type"].any() else pd.Series(["11" for _ in range(df.shape[0])])
        
        df["Tax Category Code"] = df["Tax Type"].apply(lambda x: tax_categories.get(x.replace(" ", "").lower()) if x else x)
        df.drop('Tax Type', axis=1, inplace=True)
        
        df["Supplier State Code"] = df["Supplier City"].apply(lambda x: city_codes.get(x) if x else "")


        df["Supplier Country Code"] = df["Supplier Country Code"].apply(lambda x: "MYS")

        df['Currency Code']='MYR'
        df['Currency Rate']='1'
        df['Discount']='0'

        df['Total with Tax Per Tax Type'] = df["Total Excluding Tax"]
        df['Total Excluding Tax'] = df["Invoice Line SubTotal"]

        df['Total with Tax Per Tax Type'] = df['Total with Tax Per Tax Type'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Total Tax Amount Per Tax Type'] = df['Total Tax Amount Per Tax Type'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Total Excluding Tax'] = df['Total Excluding Tax'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Total Tax Amount'] = df['Total Tax Amount'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Total Payable Amount'] = df['Total Payable Amount'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Total Including Tax'] = df['Total Including Tax'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Unit Price'] = df['Unit Price'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Invoice Line SubTotal'] = df['Invoice Line SubTotal'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Invoice Line Tax Amount'] = df['Invoice Line Tax Amount'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))
        df['Invoice Line Total with Tax'] = df['Invoice Line Total with Tax'].apply(lambda x: str(x).replace('MYR', '').replace(',', ''))

        df['Total Taxable Amount Per Tax Type'] = df['Total Excluding Tax']

        df['Supplier BRN No'] = '199801017202'

        df['Invoice Line Total Excluding Tax'] = df["Invoice Line SubTotal"]


        df['Total with Tax Per Tax Type'] = '37808.82'
        df['Total Excluding Tax'] = '36008.4'


        df = df.reindex(["Supplier Name","Supplier Address","Supplier City","Supplier State Code","Supplier Country Code","Supplier Telephone","Supplier TIN No","Supplier BRN No","Supplier SST No","Supplier MSIC Name","Supplier MSIC Code","Invoice Type","Invoice No","Invoice Date","Classification Code","Line No","Part No","Qty Inv","Unit Price","Discount", "Invoice Line SubTotal", "Invoice Line Total Excluding Tax", "Invoice Line Tax Amount", "Invoice Line Total with Tax","Total with Tax Per Tax Type", "Total Taxable Amount Per Tax Type","Tax Rate", "Total Tax Amount Per Tax Type", "Total Excluding Tax", "Total Tax Amount","Total Payable Amount","Total Including Tax","Tax Category Code", "Currency Code","Currency Rate"], axis=1)
        st.dataframe(df)
        df_list.append(df)
    return df_list
        

def main(uploaded_file):
    start = datetime.now()
    progress_bar = st.progress(0, "Extracting info from document")
    pdf_pages, filename = get_pages(uploaded_file)
    pages_processed_text = ocr(pdf_pages, filename, progress_bar)
    json_output = invoke_llm(pages_processed_text, progress_bar)
    # json_output = gemini_invoke(pdf_pages, progress_bar)
    # st.json(json_output)
    df_list = create_dataframe(json_output)
    filename = save_csv_file(df_list, filename=uploaded_file.name.split(".")[0])
    end = datetime.now()
    st.text(
        f"Time taken: {(str(round((end - start).seconds/60, 2)) + ' minutes') if (end - start).seconds > 60 else (str((end - start).seconds) + ' seconds')}"
    )
    if os.path.exists(filename):
        with open(f"{filename}", "rb") as fp:
            upload(fp, f"/{os.getenv('COMPANY_ID')}/{filename}", "text/csv")
            st.download_button(
                label="Download CSV file",
                data=fp,
                file_name=filename,
                mime="text/csv",
            )
        delete_file(filename)
    else:
        st.warning("No results found")
document = st.file_uploader("Upload Document")

if document:
    success = st.button("Extract", on_click=main, args=[document])