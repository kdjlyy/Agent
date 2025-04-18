from dotenv import load_dotenv
import os
import streamlit as st

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

@st.cache_data
def load_env_vars():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
    AVAILABLE_MODELS = os.getenv("AVAILABLE_MODELS", None)
    MODEL_LIST = AVAILABLE_MODELS.split(",") if AVAILABLE_MODELS else []
    CURRENT_MODEL = None
    BOCHA_API_KEY = os.getenv("BOCHA_API_KEY", None)
    
    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY in your environment variables.")
    else:
        print(f'✔️ OPENAI_API_KEY: {OPENAI_API_KEY}')

    if not OPENAI_BASE_URL:
        raise ValueError("Please set OPENAI_BASE_URL in your environment variables.")
    else:
        print(f'✔️ OPENAI_BASE_URL: {OPENAI_BASE_URL}')

    if not AVAILABLE_MODELS:
        raise ValueError("Please set AVAILABLE_MODELS in your environment variables.")
    else:
        print(f'✔️ AVAILABLE_MODELS: {AVAILABLE_MODELS}')

    if not BOCHA_API_KEY:
        raise ValueError("Please set BOCHA_API_KEY in your environment variables.")
    else:
        print(f'✔️ BOCHA_API_KEY: {BOCHA_API_KEY}')

    return {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "OPENAI_BASE_URL": OPENAI_BASE_URL,
        "MODEL_LIST": MODEL_LIST,
        "CURRENT_MODEL": CURRENT_MODEL,
        "TEMPERATURE": 0.8,
        "BOCHA_API_KEY": BOCHA_API_KEY,
    }