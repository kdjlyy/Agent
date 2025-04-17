from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import time
from utils.env_util import load_env_vars

# 仅首次执行
env_vars = load_env_vars()

OPENAI_API_KEY = None
OPENAI_BASE_URL = None
MODEL = None

class StreamHandler(BaseCallbackHandler):
    """继承 BaseCallbackHandler，通过 on_llm_new_token 方法捕获每个新生成的 token 并实时更新界面"""
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

with st.sidebar:
    env_vars["CURRENT_MODEL"] = st.selectbox(
        label="选择模型",
        options=env_vars["MODEL_LIST"],
        index=0,
        help="选择 LLM 模型的种类",
    )
    # 滑动条
    env_vars['TEMPERATURE'] = st.slider(
        label="Temperature",
        min_value=0.0, max_value=1.0, value=0.8,
        help="Temperature 参数用于控制 LLM 的输出多样性和确定性，高 Temperature 增加多样性但可能降低确定性，低 Temperature 则增加确定性但可能降低多样性。"
    )

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
        print(f"{time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())} [{env_vars["CURRENT_MODEL"]}] {[message.content for message in st.session_state.messages]}")
        response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))

