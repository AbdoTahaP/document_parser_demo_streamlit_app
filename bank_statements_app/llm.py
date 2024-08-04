import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


# def llm_ocr(image):
#     schema = [ResponseSchema(name="response", description="the extracted text from the image.")]
    
#     PROMPT_TEMPLATE = """
# You are an OCR assistant that takes the image and extract the text in an organized format in a valid JSON object matches the following JSON schema.\n

# JSON Schema:
# ```
# {format_instructions}
# ```

# image:
# {image}
#     """
#     output_parser = StructuredOutputParser.from_response_schemas(schema)
#     format_instructions = output_parser.get_format_instructions()
#     prompt = PromptTemplate(
#         template=PROMPT_TEMPLATE,
#         input_variables=["image"],
#         partial_variables={"format_instructions": format_instructions},
#     )
#     model = ChatGoogleGenerativeAI(
#         model="gemini-1.5-flash",
#         format="json",
#         temperature=0.1,
#         max_tokens=None,
#         timeout=None,
#         api_key=os.getenv("GEMINI_API_KEY")
#     )
#     parser = JsonOutputParser()
#     chain = prompt | model | output_parser
    
#     response_text = chain.invoke({"image": image})
    
#     return response_text


def llm(context_text, parser):
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
    instructions = parser.get_format_instructions()
    
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context"],
        partial_variables={"format_instructions": instructions},
    )

    # model = ChatOllama(model="llama3.1:70b", temperature=0.1, format="json")
    # model = ChatGroq(
    #     model="llama-3.1-70b-versatile",
    #     temperature=0.1,
    #     max_tokens=None,
    #     timeout=None,
    #     api_key=os.getenv("GROQ_API_KEY")
    # )
    model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    api_key=os.getenv("GEMINI_API_KEY")
)
    chain = prompt | model | parser
    
    response_text = chain.invoke({"context": context_text})
    
    return response_text


def evaluate(context, res):
    PROMPT_TEMPLATE ="""
    You are an assistant calculates the accuracy of the json response based on the given context and outputs a ratio in a JSON object following the instructions.

    Instructions:
    ```
    {format_instructions}
    ```

    context:
    ```    
    {context}
    ```

    response:
    ```
    {response}
    ```

    """

    schema = [ResponseSchema(name="accuracy", description="a ratio that determines the accuracy", type="number")]
    output_parser = StructuredOutputParser.from_response_schemas(schema)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "response"],
        partial_variables={"format_instructions": format_instructions},
    )
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        format="json",
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        api_key=os.getenv("GEMINI_API_KEY")
    )
    parser = JsonOutputParser()
    chain = prompt | model | output_parser
    response_text = chain.invoke({"context": context, "response": res})
    
    return response_text