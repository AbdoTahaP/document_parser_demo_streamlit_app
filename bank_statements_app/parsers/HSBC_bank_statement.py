from typing import List
from decimal import Decimal
from datetime import date
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, ConfigDict

# class Transactions(BaseModel):
#     Date: date = Field(title="Date", description="The day and month of the transcation.")
#     transaction_details: str = Field(title="Transaction Details", description="the details of the transaction like its type and number.")
#     deposit: Decimal = Field(title="Deposit", description="The deposited amount in this transaction.")
#     withdrawal: Decimal = Field(title="Withdrawal", description="The withdrawn amount in this transaction.")
#     balance: Decimal = Field(title="Balance", description="The current balance after the transaction.")
    
#     model_config = ConfigDict(json_schema_serialization_defaults_required=True)

transactions_response_schema = [
    ResponseSchema(name="Date", description="The day and month of the transaction.", type="string"),  # date is serialized as string
    ResponseSchema(name="Transaction Details", description="The details of the transaction like its type and number.", type="string"),
    ResponseSchema(name="Deposit", description="The deposited amount in this transaction.", type="number"),
    ResponseSchema(name="Withdrawal", description="The withdrawn amount in this transaction.", type="number"),
    ResponseSchema(name="Balance", description="The current balance after the transaction.", type="number"),
]

# class HSBCBusinessDirectHKDCurrent(BaseModel):
#     transactions: List[Transactions] = Field(title="Transactions", description="A list of transactions.")
#     total_no_of_deposits: int = Field(title="Total No. of Deposits", description="The number of deposit transactions in this list.")
#     total_deposit_amount: Decimal = Field(title="Total Deposit Amount", description="The total deposited amount from all transactions in this list.")
#     total_no_of_withdrawals: int = Field(title="Total No. of Deposits", description="The number of withdrawal transactions in this list.")
#     total_withdrawal_amount: Decimal = Field(title="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.")
    
    # model_config = ConfigDict(title="HSBC Business Direct HKD Current", json_schema_serialization_defaults_required=True)

hsbc_current_response_schema = [
    ResponseSchema(name="Transactions", description=f"""{transactions_response_schema}""", type="array"),
    ResponseSchema(name="Total No. of Deposits", description="The number of deposit transactions in this list.", type="number"),
    ResponseSchema(name="Total Deposit Amount", description="The total deposited amount from all transactions in this list.", type="number"),
    ResponseSchema(name="Total No. of Withdrawals", description="The number of withdrawal transactions in this list.", type="number"),
    ResponseSchema(name="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.", type="number"),
]

# class HSBCBusinessDirectHKDSavings(BaseModel):
#     transactions: List[Transactions] = Field(title="Transactions", description="A list of transactions.")
#     total_no_of_deposits: int = Field(title="Total No. of Deposits", description="The number of deposit transactions in this list.")
#     total_deposit_amount: Decimal = Field(title="Total Deposit Amount", description="The total deposited amount from all transactions in this list.")
#     total_no_of_withdrawals: int = Field(title="Total No. of Deposits", description="The number of withdrawal transactions in this list.")
#     total_withdrawal_amount: Decimal = Field(title="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.")
    
#     model_config = ConfigDict(title="HSBC Business Direct HKD Savings", json_schema_serialization_defaults_required=True)
    
hsbc_savings_response_schema = [
    ResponseSchema(name="Transactions", description=f"""{transactions_response_schema}""", type="array"),
    ResponseSchema(name="Total No. of Deposits", description="The number of deposit transactions in this list.", type="number"),
    ResponseSchema(name="Total Deposit Amount", description="The total deposited amount from all transactions in this list.", type="number"),
    ResponseSchema(name="Total No. of Withdrawals", description="The number of withdrawal transactions in this list.", type="number"),
    ResponseSchema(name="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.", type="number"),
]

# class HSBCBusinessDirectPortfolioSummary(BaseModel):
#     total_balance_in_hkd: Decimal = Field(title="Total Balance in HKD", description="The total balance in HKD in the account after all related transactions.")
#     total_balance_in_foreign_currency: Decimal = Field(title="Total Balance in Foreign Currency", description="The total balance in the foreign currency in the account after all related transactions.")
#     total_balance_in_overdraft: Decimal = Field(title="Total Balance in Overdraft", description="The total balance in overdraft in the account after all related transactions.")
#     current: Decimal = Field(title="Current", description="The total balance in the current account.")
#     savings: Decimal = Field(title="Savings", description="The total balance in the savings account.")
    
#     model_config = ConfigDict(title="HSBC Business Direct Portfolio Summary", json_schema_serialization_defaults_required=True)

portfolio_summary_response_schema = [
    ResponseSchema(name="Total Balance in HKD", description="The total balance in HKD in the account after all related transactions.", type="number"),
    ResponseSchema(name="Total Balance in Foreign Currency", description="The total balance in the foreign currency in the account after all related transactions.", type="number"),
    ResponseSchema(name="Total Balance in Overdraft", description="The total balance in overdraft in the account after all related transactions.", type="number"),
    ResponseSchema(name="Current", description="The total balance in the current account.", type="number"),
    ResponseSchema(name="Savings", description="The total balance in the savings account.", type="number"),
]

# class HSBCBankStatement(BaseModel):
#     statement_number: str = Field(title="Number", description="The identifing number of the statement.")
#     branch_name: str = Field(title="Branch", description="The name of the branch.")
#     statement_date: date = Field(title="Date", description="The date at which the statement is issued.")
#     hsbc_business_direct_portfolio_summary: HSBCBusinessDirectPortfolioSummary = Field(title="HSBC Business Direct Portfolio Summary", description="The summary of the transactions in the statement.")
#     hsbc_business_direct_hkd_current: List[HSBCBusinessDirectHKDCurrent] = Field(title="HSBC Business Direct HKD Current", description="the details of transactions and total in the current account.")
#     hsbc_business_direct_hkd_savings: List[HSBCBusinessDirectHKDSavings] = Field(title="HSBC Business Direct HKD Savings", description="the details of transactions and total in the savings account.")
    
#     model_config = ConfigDict(title="HSBC Bank Statement", json_schema_serialization_defaults_required=True)
    
bank_statement_response_schema = [
    ResponseSchema(name="Number", description="The identifying number of the statement.", type="string"),
    ResponseSchema(name="Branch", description="The name of the branch.", type="string"),
    ResponseSchema(name="Date", description="The date at which the statement is issued.", type="string"),  # date is serialized as string
    ResponseSchema(name="HSBC Business Direct Portfolio Summary", description=f"""{portfolio_summary_response_schema}""", type="object"),
    ResponseSchema(name="HSBC Business Direct HKD Current", description=f"""{hsbc_current_response_schema}""", type="array"),
    ResponseSchema(name="HSBC Business Direct HKD Savings", description=f"""{hsbc_savings_response_schema}""", type="array"),
]

hsbc_parser = StructuredOutputParser.from_response_schemas(bank_statement_response_schema)