import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import get_openai_api_key, get_default_model, get_openai_base_url
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# State 是一个 TypedDict, 其中包含一个键: messages
# add_messages 是 reducer 函数, 用于将新消息附加到列表中, 而不是覆盖它。
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name=get_default_model(),
    base_url=get_openai_base_url(),
)

def chatbot(state: State):
    # 使用 llm 根据当前状态的消息列表生成回复
    return {"messages": [llm.invoke(state["messages"])]}

# 添加节点: key 是唯一标识, value 是节点对应的函数或对象
graph_builder.add_node("chatbot", chatbot)

# 添加边: 每次我们运行时从 chatbot 开始, 任何时候运行到 chatbot 节点都可以退出
# START -----> chatbot ----> END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# 生成图结构图
with open(os.path.dirname(__file__) + "/demo_1_graph.mmd", "w", encoding="utf-8") as file:
    file.write(graph.get_graph().draw_mermaid())

# 根据用户输入，流式传输并打印graph中的最新数据
def stream_graph_updates(user_input: str):
    input = {"messages": [{"role": "user", "content": user_input}]}
    for event in graph.stream(input=input):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    stream_graph_updates(user_input)