from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
import os

OPENAI_API_KEY = None
OPENAI_BASE_URL = None
MODEL = None

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

@st.cache_data
def load_env_vars():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
    AVIAILABLE_MODELS = os.getenv("AVIAILABLE_MODELS", None)
    MODEL_LIST = AVIAILABLE_MODELS.split(",") if AVIAILABLE_MODELS else []
    CURRENT_MODEL = None

    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY in your environment variables.")
    else:
        print(f'✔️ OPENAI_API_KEY: {OPENAI_API_KEY}')

    if not OPENAI_BASE_URL:
        raise ValueError("Please set OPENAI_BASE_URL in your environment variables.")
    else:
        print(f'✔️ OPENAI_BASE_URL: {OPENAI_BASE_URL}')

    if not AVIAILABLE_MODELS:
        raise ValueError("Please set AVIAILABLE_MODELS in your environment variables.")
    else:
        print(f'✔️ AVIAILABLE_MODELS: {AVIAILABLE_MODELS}')

    return {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "OPENAI_BASE_URL": OPENAI_BASE_URL,
        "MODEL_LIST": MODEL_LIST,
        "CURRENT_MODEL": CURRENT_MODEL,
        "TEMPERATURE": 0.8
    }

# 仅首次执行
env_vars = load_env_vars()

with st.sidebar:
    env_vars["CURRENT_MODEL"] = st.selectbox(
        "👇选择模型",
        env_vars["MODEL_LIST"],
        index=0,
        help="选择模型",
    )
    # 滑动条
    env_vars['TEMPERATURE'] = st.slider("Temperature", 0.0, 1.0, 0.8)

if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="🙃 有问题可以向我提问哦~")]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input(placeholder = "shift+enter 换行", max_chars = 2048):
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = ChatOpenAI(
            openai_api_key=env_vars["OPENAI_API_KEY"], 
            model_name=env_vars["CURRENT_MODEL"], 
            temperature=env_vars["TEMPERATURE"], 
            base_url=env_vars["OPENAI_BASE_URL"], 
            streaming=True, 
            callbacks=[stream_handler]
        )
        response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
        # print(env_vars)
