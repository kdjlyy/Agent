from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import time
from utils.env_util import load_env_vars

OPENAI_API_KEY = None
OPENAI_BASE_URL = None
MODEL = None

# 仅首次执行
env_vars = load_env_vars()

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


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个正在与人类对话的AI聊天机器人"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(
    openai_api_key=env_vars["OPENAI_API_KEY"], 
    model_name=env_vars["CURRENT_MODEL"], 
    temperature=env_vars["TEMPERATURE"], 
    base_url=env_vars["OPENAI_BASE_URL"], 
)
chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)


view_messages = st.expander("查看会话状态中的消息内容")

# StreamlitChatMessageHistory 初始化（key 用于在 session_state 中唯一标识存储）
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("🙃 有问题可以向我提问哦~")

# 从 StreamlitChatMessageHistory 渲染当前消息，自动区分角色 human 和 ai 消息
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# 定义一个用户输入框并处理相关逻辑
if prompt := st.chat_input(placeholder = "shift+enter 换行", max_chars = 2048):
    st.chat_message("human").write(prompt)
    # 当使用 ​​StreamlitChatMessageHistory​​ 时，新消息会在运行过程中自动保存到历史记录中，无需手动管理
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)

# 在最后绘制消息，以便新生成的消息立即显示
with view_messages:
    view_messages.json(st.session_state.langchain_messages)
