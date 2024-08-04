from langchain.output_parsers import ResponseSchema, StructuredOutputParser

transactions_response_schema = [
    ResponseSchema(name="Date", description="The day and month of the transaction.", type="string"),  # date is serialized as string
    ResponseSchema(name="Transaction Details", description="The details of the transaction like its type and number.", type="string"),
    ResponseSchema(name="Deposit", description="The deposited amount in this transaction.", type="number"),
    ResponseSchema(name="Withdrawal", description="The withdrawn amount in this transaction.", type="number"),
    ResponseSchema(name="Balance", description="The current balance after the transaction.", type="number"),
]

hsbc_current_response_schema = [
    ResponseSchema(name="Transactions", description=f"""{transactions_response_schema}""", type="array"),
    ResponseSchema(name="Total No. of Deposits", description="The number of deposit transactions in this list.", type="number"),
    ResponseSchema(name="Total Deposit Amount", description="The total deposited amount from all transactions in this list.", type="number"),
    ResponseSchema(name="Total No. of Withdrawals", description="The number of withdrawal transactions in this list.", type="number"),
    ResponseSchema(name="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.", type="number"),
]

hsbc_savings_response_schema = [
    ResponseSchema(name="Transactions", description=f"""{transactions_response_schema}""", type="array"),
    ResponseSchema(name="Total No. of Deposits", description="The number of deposit transactions in this list.", type="number"),
    ResponseSchema(name="Total Deposit Amount", description="The total deposited amount from all transactions in this list.", type="number"),
    ResponseSchema(name="Total No. of Withdrawals", description="The number of withdrawal transactions in this list.", type="number"),
    ResponseSchema(name="Total Withdrawal Amount", description="The total withdrawn amount from all transactions in this list.", type="number"),
]

portfolio_summary_response_schema = [
    ResponseSchema(name="Total Balance in HKD", description="The total balance in HKD in the account after all related transactions.", type="number"),
    ResponseSchema(name="Total Balance in Foreign Currency", description="The total balance in the foreign currency in the account after all related transactions.", type="number"),
    ResponseSchema(name="Total Balance in Overdraft", description="The total balance in overdraft in the account after all related transactions.", type="number"),
    ResponseSchema(name="Current", description="The total balance in the current account.", type="number"),
    ResponseSchema(name="Savings", description="The total balance in the savings account.", type="number"),
]
    
statement_response_schema = [
    ResponseSchema(name="Number", description="The identifying number of the statement.", type="string"),
    ResponseSchema(name="Branch", description="The name of the branch.", type="string"),
    ResponseSchema(name="Date", description="The date at which the statement is issued.", type="string"),
    ResponseSchema(name="HSBC Portfolio Summary", description=f"""{portfolio_summary_response_schema}""", type="object"),
    ResponseSchema(name="HSBC HKD Current", description=f"""{hsbc_current_response_schema}""", type="array"),
    ResponseSchema(name="HSBC HKD Savings", description=f"""{hsbc_savings_response_schema}""", type="array"),
]

bank_statements_schema = [ResponseSchema(name="Statements", description=f"""{statement_response_schema}""", type="array")]

hsbc_parser = StructuredOutputParser.from_response_schemas(bank_statements_schema)