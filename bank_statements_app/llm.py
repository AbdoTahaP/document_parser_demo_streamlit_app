import os
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

from parsers.HSBC_bank_statement import hsbc_parser

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
    instructions = hsbc_parser.get_format_instructions()
    
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context"],
        partial_variables={"format_instructions": instructions},
    )

    model = ChatOllama(model="llama3.1:70b", temperature=0.1, format="json")
    # model = ChatGroq(
    #     model="llama-3.1-70b-versatile",
    #     temperature=0.1,
    #     max_tokens=None,
    #     timeout=None,
    #     api_key=os.getenv("GROQ_API_KEY")
    # )
    chain = prompt | model | hsbc_parser
    
    response_text = chain.invoke({"context": context_text})
    
    return response_text