import os


def get_llm():
    """Get LLM based on env config
    
    Set LLM_provider env var to : ollama , 'groq'
    Default: ollama
    """

    provider = os.getenv('LLM_PROVIDER')

    if provider == 'ollama':
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model = os.getenv('OLLAMA_MODEL', 'llama3.2'),
            base_url = os.getenv('OLLAMA_BASE_URL' , 'http://localhost:11434')
        )

    elif provider == 'groq':
        from langchain_groq import ChatGroq
        return ChatGroq(
            model = 'llama-3.1-70b-versatile',
            api_key = os.getenv('GROQ_API_KEY'),
        )

    raise ValueError(f"Unknown LLM Provider: {provider}")

