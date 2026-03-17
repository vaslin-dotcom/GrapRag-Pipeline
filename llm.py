import os
from langchain_openai import ChatOpenAI
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL

def get_llm(output_schema=None):
    """
    Returns a Groq-backed ChatOpenAI LLM.
    If output_schema (a Pydantic model) is provided,
    returns llm.with_structured_output(output_schema).
    """
    llm = ChatOpenAI(
        model=GROQ_MODEL,
        temperature=0,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL
    )

    if output_schema:
        return llm.with_structured_output(output_schema, method="function_calling")

    return llm