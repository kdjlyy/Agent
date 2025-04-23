""" 
为 LangGraph 添加线程级持久化功能 
多个对话或用户之间共享的内存（跨线程持久化），参考：https://langchain-ai.github.io/langgraph/how-tos/cross-thread-persistence/
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START

# 定义模型
llm = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name=get_default_model(),
    base_url=get_openai_base_url(),
    temperature=0.0
)

# 定义一个调用聊天模型的单节点
def call_model_node(state: MessagesState):
    """
        MessagesState 的类型定义：
        ```
        class MessagesState(TypedDict):
            messages: Annotated[list[AnyMessage], add_messages]
        ```
    """
    response = llm.invoke(state["messages"])
    return {"messages": response}

# 添加节点和边
builder = StateGraph(MessagesState)
builder.add_node("call_model_node", call_model_node)
builder.add_edge(START, "call_model_node")

# 使用此图，对话上下文将不会在各交互之间持久保存
graph1 = builder.compile()
input_message = {"role": "user", "content": "hi! I'm bob"}
for chunk in graph1.stream({"messages": [input_message]}, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
input_message = {"role": "user", "content": "what's my name?"}
for chunk in graph1.stream({"messages": [input_message]}, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

    # ================================ Human Message =================================
    # hi! I'm bob
    # ================================== Ai Message ==================================
    # Hello Bob! Nice to meet you. How can I assist you today?
    # ================================ Human Message =================================
    # what's my name?
    # ================================== Ai Message ==================================
    # I'm sorry, but I don't know your name yet! Please tell me what your name is, and 
    # I'll make sure to remember it for our conversation. 😊

# 为 LangGraph 添加线程级持久化功能
from langgraph.checkpoint.memory import MemorySaver
# 在编译图时传入一个检查点保存器(checkpointer)，并传入一个 config，用于指定线程 ID
# 如果使用的是 LangGraph Cloud 或 LangGraph Studio，在编译图时无需传递检查点器，因为这会自动完成
memory = MemorySaver()
graph2 = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}
input_message = {"role": "user", "content": "你好我是张三"}
for chunk in graph2.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
input_message = {"role": "user", "content": "我的名字是什么"}
for chunk in graph2.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

    # ================================ Human Message =================================
    # 你好我是张三
    # ================================== Ai Message ==================================
    # 你好张三！今天过得怎么样？有什么想和我分享的吗？😊
    # ================================ Human Message =================================
    # 我的名字是什么
    # ================================== Ai Message ==================================
    # 你之前告诉过我啦，你叫张三！😊 有什么需要我帮忙的吗？或者想聊聊别的什么？

# NOTE: 如果要开启新一轮的对话，可以传入一个不同的 thread_id
config2 = {"configurable": {"thread_id": "2"}}
input_message = {"role": "user", "content": "我的名字是什么"}
for chunk in graph2.stream({"messages": [input_message]}, config2, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

    # ================================== Ai Message ==================================
    # 你好！不过，作为一个AI助手，我无法直接知道你的名字哦。如果你是在某个特定的平台或应用中使用我，
    # 可能需要查看你的账户设置或登录信息来确认自己的名字。或者，你可以告诉我你的名字，这样我以后就可以
    # 用你的名字来称呼你啦！😊

