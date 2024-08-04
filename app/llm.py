from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

# class InvoiceLines(BaseModel):
#     Classification_Code: str = Field()
#     Line_No: int = Field()
#     Part_No: str = Field()
#     Qty_Inv: int = Field()
#     Unit_Price: float = Field()
#     Discount: float = Field()
#     Invoice_Line_SubTotal: float = Field()
#     Tax_Rate: float = Field()
#     Invoice_Line_Tax_Amount: float = Field()
#     Invoice_Line_Total_With_Tax: float = Field()
    
#     model_config = ConfigDict(json_schema_serialization_defaults_required=True)

# class Invoice(BaseModel):
#     Supplier_Name: str = Field()
#     Supplier_Address: str = Field()
#     Supplier_City: str = Field()
#     Supplier_State_Code: str = Field()
#     Supplier_Country_Code: str = Field()
#     Supplier_Telephone: str = Field()
#     Supplier_TIN: str = Field()
#     Supplier_BRN: str = Field()
#     Supplier_SST: str = Field()
#     Supplier_MSIC_Code: str = Field()
#     Supplier_MSIC_Name: str = Field()
    
#     Invoice_Type: str = Field()
#     Invoice_No: str = Field()
#     Invoice_Date: str = Field()
#     Invoice_Lines: List[InvoiceLines] = Field(default=[])
    
#     Total_with_Tax_per_Tax_Type: float = Field()
#     Tax_Category: str = Field()
#     Tax_Rate: float = Field()
#     Total_Tax_Amount_per_Tax_Type: float = Field()
    
#     Total_Net_Amount: float = Field()
#     Total_Excluding_Tax: float = Field()
#     Tota_Tax_Amount: float = Field()
#     Total_Payable_Amount: float = Field()
#     Total_Including_Tax: float = Field()
    
#     model_config = ConfigDict(json_schema_serialization_defaults_required=True)
    
response_schema = [
    ResponseSchema(name="Supplier Name", description="Supplier Name", type="string"),
    ResponseSchema(name="Supplier Address", description="Supplier Address", type="string"),
    ResponseSchema(name="Supplier City", description="Supplier City", type="string"),
    ResponseSchema(name="Supplier State Code", description="Supplier State Code", type="string"),
    ResponseSchema(name="Supplier Country Code", description="Supplier Country Code", type="string"),
    ResponseSchema(name="Supplier Telephone", description="Supplier Telephone", type="string"),
    ResponseSchema(name="Supplier TIN No", description="Supplier TIN", type="string"),
    ResponseSchema(name="Supplier BRN No", description="Supplier BRN", type="string"),
    ResponseSchema(name="Supplier SST No", description="Supplier SST", type="string"),
    ResponseSchema(name="Supplier MSIC Name", description="Supplier Business", type="string"),
    ResponseSchema(name="Supplier MSIC Code", description="Supplier MSIC Code", type="string"),
    ResponseSchema(name="Invoice Type", description="invoice type code", type="string"),
    ResponseSchema(name="Invoice No", description="Invoice No", type="string"),
    ResponseSchema(name="Invoice Date", description="Invoice Date", type="string"),
    ResponseSchema(name="Invoice Lines",
                   description=f"""{
                        [
                            ResponseSchema(name="Classification Code", description="Classification Code",  type="string"),
                            ResponseSchema(name="Line No", description="Line No",  type="number"),
                            ResponseSchema(name="Part No", description="the description of the invoice line",  type="string"),
                            ResponseSchema(name="Qty Inv", description="Qty Inv",  type="number"),
                            ResponseSchema(name="Unit Price", description="Unit Price",  type="number"),
                            ResponseSchema(name="Discount", description="Discount",  type="number"),
                            ResponseSchema(name="Invoice Line SubTotal", description="Invoice Line SubTotal",  type="number"),
                            ResponseSchema(name="Tax Rate", description="Tax Rate",  type="number"),
                            ResponseSchema(name="Invoice Line Tax Amount", description="Invoice Line Tax Amount",  type="number"),
                            ResponseSchema(name="Invoice Line Total with Tax", description="Invoice Line Total With Tax",  type="number"),
                        ]
                       }""", 
                   type="array"),
    ResponseSchema(name="Total with Tax Per Tax Type", description="Invoice Total Including Tax", type="number"),
    ResponseSchema(name="Tax Type", description="Tax Type", type="string"),
    ResponseSchema(name="Tax Rate", description="Tax Rate", type="number"),
    ResponseSchema(name="Total Tax Amount Per Tax Type", description="Total Tax Amount", type="number"),
    # ResponseSchema(name="Total Net Amount", description="Total Net Amount", type="number"),
    ResponseSchema(name="Total Excluding Tax", description="Total Excluding Tax", type="number"),
    ResponseSchema(name="Total Tax Amount", description="Total Tax Amount", type="number"),
    ResponseSchema(name="Total Payable Amount", description="Total Payable Amount", type="number"),
    ResponseSchema(name="Total Including Tax", description="Total Including Tax", type="number"),   
]

PROMPT_TEMPLATE ="""
You are an assistant that recognize the given context and extract the following required fields in a valid json format

Instructions:
```
{format_instructions}
```

context:
```    
{context}
```

"""

def llm(context_text):
    output_parser = StructuredOutputParser.from_response_schemas(response_schema)
    instructions = output_parser.get_format_instructions()
    
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context"],
        partial_variables={"format_instructions": instructions},
    )

    model = ChatOllama(model="llama3.1", temperature=0.1, format="json")
    chain = prompt | model | output_parser
    
    response_text = chain.invoke({"context": context_text})
    
    return response_text