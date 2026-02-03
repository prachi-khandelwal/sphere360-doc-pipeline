import os


def get_llm():
    """Get LLM based on env config
    
    Set LLM_provider env var to : ollama , 'groq' or etc
    Default: ollama
    """

    provider = os.getenv('LLM_PROVIDER', 'ollama')

    if provider == 'ollama':
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            base_url = os.getenv('OLLAMA_BASE_URL' , 'http://localhost:11434'),
            temperature = 0.1
        )

    elif provider == 'groq':
        from langchain_groq import ChatGroq
        return ChatGroq(
            model = 'llama-3.1-70b-versatile',
            api_key = os.getenv('GROQ_API_KEY'),
            temperature = 0
        )

    raise ValueError(f"Unknown LLM Provider: {provider}")

