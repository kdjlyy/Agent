from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from utils.env_util import load_env_vars
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.messages import AIMessageChunk
from langchain_core.messages import HumanMessage

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


# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")


# Set up the LangChain, passing in Message History

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI(    
    openai_api_key=env_vars["OPENAI_API_KEY"], 
    model_name=env_vars["CURRENT_MODEL"], 
    temperature=env_vars["TEMPERATURE"], 
    base_url=env_vars["OPENAI_BASE_URL"], 
    streaming=True,
)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": "user_12345"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    view_messages.json(st.session_state.langchain_messages)