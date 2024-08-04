import os
import google.generativeai as genai

Transactions = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Transaction Details": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Deposit": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Withdrawal": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Balance": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double")
    },
    required=["Date", "Transaction Details", "Deposit", "Withdrawal", "Balance"]
)

HSBCCurrent = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Transactions": genai.protos.Schema(
            type=genai.protos.Type.ARRAY,
            items=Transactions
        ),
        "Total No. of Deposits": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Deposit Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total No. of Withdrawals": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Withdrawal Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double")
    },
    required=["Transactions", "Total No. of Deposits", "Total Deposit Amount", "Total No. of Withdrawals", "Total Withdrawal Amount"]
)

HSBCSavings = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Transactions": genai.protos.Schema(
            type=genai.protos.Type.ARRAY,
            items=Transactions
        ),
        "Total No. of Deposits": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Deposit Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total No. of Withdrawals": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Withdrawal Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double")
    },
    required=["Transactions", "Total No. of Deposits", "Total Deposit Amount", "Total No. of Withdrawals", "Total Withdrawal Amount"]
)

PortfolioSummary = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Total Balance in HKD": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Balance in Foreign Currency": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Total Balance in Overdraft": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Net Position": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Current": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double"),
        "Savings": genai.protos.Schema(type=genai.protos.Type.NUMBER, format="double")
    },
    required=["Total Balance in HKD", "Total Balance in Foreign Currency", "Total Balance in Overdraft", "Net Position", "Current", "Savings"]
)

statement = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Number": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Branch": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "HSBC Business Direct Portfolio Summary": PortfolioSummary,
        "HSBC Business Direct HKD Current": HSBCCurrent,
        "HSBC Business Direct HKD Savings": HSBCSavings
    },
    required=["Number", "Branch", "Date", "HSBC Business Direct Portfolio Summary", "HSBC Business Direct HKD Current", "HSBC Business Direct HKD Savings"]
)

BankStatements = genai.protos.Schema(
    type=genai.protos.Type.ARRAY,
    items=statement
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-pro',
                              # Set the `response mime type` to output JSON
                              generation_config={
                                  "response_mime_type": "application/json",
                                  "response_schema": BankStatements                                  },
                              )

PROMPT = """
you are an assistant that takes a context of document and extract the required data in a json format following the provided schema.\n you will create a new json object or complete it if provided. 
"""

def gemini(messages: list):
    messages.insert(0, PROMPT)
    return model.generate_content(messages)