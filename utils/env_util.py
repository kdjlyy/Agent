from dotenv import load_dotenv
import os

def get_openai_api_key():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY", None)
    print(f'✔️ OPENAI_API_KEY: {openai_api_key}')
    return openai_api_key

def get_openai_base_url():
    load_dotenv()
    openai_base_url = os.getenv("OPENAI_BASE_URL", None)
    print(f'✔️ OPENAI_BASE_URL: {openai_base_url}')
    return openai_base_url

def get_default_model():
    load_dotenv()
    default_model = os.getenv("DEFAULT_MODEL", "Qwen/QwQ-32B")
    print(f'✔️ DEFAULT_MODEL: {default_model}')
    return default_model

def get_default_embedding_model():
    load_dotenv()
    embedding_model = os.getenv("EMBEDDING_MODEL", "Pro/BAAI/bge-m3")
    print(f'✔️ EMBEDDING_MODEL: {embedding_model}')
    return embedding_model