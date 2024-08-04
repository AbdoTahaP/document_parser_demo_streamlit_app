import os
import google.generativeai as genai

Transactions = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Transaction Details": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Deposit": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Withdrawal": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Balance": genai.protos.Schema(type=genai.protos.Type.NUMBER)
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
        "Total No. of Deposits": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Deposit Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total No. of Withdrawals": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Withdrawal Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER)
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
        "Total No. of Deposits": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Deposit Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total No. of Withdrawals": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Withdrawal Amount": genai.protos.Schema(type=genai.protos.Type.NUMBER)
    },
    required=["Transactions", "Total No. of Deposits", "Total Deposit Amount", "Total No. of Withdrawals", "Total Withdrawal Amount"]
)

PortfolioSummary = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Total Balance in HKD": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Balance in Foreign Currency": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Total Balance in Overdraft": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Current": genai.protos.Schema(type=genai.protos.Type.NUMBER),
        "Savings": genai.protos.Schema(type=genai.protos.Type.NUMBER)
    },
    required=["Total Balance in HKD", "Total Balance in Foreign Currency", "Total Balance in Overdraft", "Current", "Savings"]
)

BankStatement = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "Number": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Branch": genai.protos.Schema(type=genai.protos.Type.STRING),
        "Date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "HSBC Business Direct Portfolio Summary": PortfolioSummary,
        "HSBC Business Direct HKD Current": genai.protos.Schema(
            type=genai.protos.Type.ARRAY,
            items=HSBCCurrent
        ),
        "HSBC Business Direct HKD Savings": genai.protos.Schema(
            type=genai.protos.Type.ARRAY,
            items=HSBCSavings
        )
    },
    required=["Number", "Branch", "Date", "HSBC Business Direct Portfolio Summary", "HSBC Business Direct HKD Current", "HSBC Business Direct HKD Savings"]
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash',
                              # Set the `response mime type` to output JSON
                              generation_config={
                                  "response_mime_type": "application/json",
                                  "response_schema": BankStatement,
                                  },
                              )

PROMPT = """
you are an assistant that takes an image and extract the required data in a json format following the provided schema
"""

def gemini(messages: list):
    messages.insert(0, PROMPT)
    return model.generate_content(messages)