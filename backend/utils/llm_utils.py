"""
LLM utility functions - provides unified interface for different LLM providers
"""

import os
from config import LLM_API_KEY, LLM_PROVIDER, DEFAULT_LLM_MODEL


def get_llm(model: str = None, temperature: float = 0.7):
    """
    Get LLM instance based on configured provider.
    
    Supports:
    - Groq (via ChatGroq)
    - OpenAI (via ChatOpenAI)
    - Anthropic (via ChatAnthropic)
    """
    model = model or DEFAULT_LLM_MODEL
    
    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=LLM_API_KEY,
            model_name=model,
            temperature=temperature
        )
    
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            anthropic_api_key=LLM_API_KEY,
            model=model,
            temperature=temperature
        )
    
    else:  # default to OpenAI
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            openai_api_key=LLM_API_KEY,
            model=model,
            temperature=temperature
        )


def get_embeddings():
    """
    Get embeddings instance based on configured provider.
    
    For now, always uses OpenAI embeddings (most compatible).
    Can be extended to support other providers.
    """
    from langchain_openai import OpenAIEmbeddings
    
    # If using Groq, still use OpenAI for embeddings (Groq doesn't provide embeddings)
    api_key = os.getenv("OPENAI_API_KEY") or LLM_API_KEY
    
    return OpenAIEmbeddings(openai_api_key=api_key)
