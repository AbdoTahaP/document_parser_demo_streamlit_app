import os
import google.generativeai as genai

InvoiceLines = genai.protos.Schema(
    type = genai.protos.Type.OBJECT,
    properties = {
        "Classification Code": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Line No": genai.protos.Schema(type=genai.protos.Type.INTEGER),
        "Part No": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Qty Inv": genai.protos.Schema(type=genai.protos.Type.INTEGER),
        "Unit Price": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Discount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Invoice Line SubTotal": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Invoice Line Tax Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Invoice Line Total with Tax": genai.protos.Schema(type=genai.protos.Type.NUMBER),
    },
    required=["Classification Code","Line No","Part No","Qty Inv","Unit Price","Discount", "Invoice Line SubTotal", "Invoice Line Tax Amount", "Invoice Line Total with Tax"]
)

Invoice = genai.protos.Schema(
    type = genai.protos.Type.OBJECT,
    properties ={
        "Supplier Name": genai.protos.Schema(type=genai.protos.Type.STRING) ,
        "Supplier Address": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier City": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier State Code": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier Country Code": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier Telephone": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier TIN No": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier BRN No": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier SST No": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier MSIC Name": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Supplier MSIC Code": genai.protos.Schema(type=genai.protos.Type.STRING),
        
        "Invoice Type": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Invoice No": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Invoice Date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Invoice Lines": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=InvoiceLines
                        ),
        
        "Total with Tax Per Tax Type": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Tax Type": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Tax Rate": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Tax Amount Per Tax Type": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        
        "Total Excluding Tax": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Tax Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Payable Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Including Tax": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        
        "Currency Code": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Currency Rate": genai.protos.Schema(type=genai.protos.Type.INTEGER),
    },
    required=["Supplier Name","Supplier Address","Supplier City","Supplier State Code","Supplier Country Code","Supplier Telephone","Supplier TIN No","Supplier BRN No","Supplier SST No","Supplier MSIC Name","Supplier MSIC Code","Invoice Type","Invoice No","Invoice Date","Invoice Lines","Total with Tax Per Tax Type","Tax Rate", "Total Tax Amount Per Tax Type", "Total Excluding Tax", "Total Tax Amount","Total Payable Amount","Total Including Tax","Tax Type", "Currency Code","Currency Rate"]
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash',
                              # Set the `response mime type` to output JSON
                              generation_config={
                                  "response_mime_type": "application/json",
                                  "response_schema": Invoice,
                                  },
                              )

PROMPT = """
you are an assistant that takes an image and extract the required data in a json format following the provided schema
"""

def gemini(messages: list):
    messages.insert(0, PROMPT)
    return model.generate_content(messages)