"""
Single shared factory for the LLM client used by every agent.

Centralizing this means switching model providers or swapping the model
name is a one-line change here, instead of an edit-every-file change.
"""

from langchain_groq import ChatGroq
import config


def get_llm(temperature: float = 0.3) -> ChatGroq:
    if not config.GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=temperature,
    )
