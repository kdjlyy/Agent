import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import get_openai_api_key, get_default_model, get_openai_base_url
from utils.search import bocha_websearch_tool
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langchain.agents import Tool
from langgraph.prebuilt import ToolNode, tools_condition

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

# 创建LangChain工具
tool = Tool(
    name="🔍在线搜索",
    func=bocha_websearch_tool,
    description="搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页 URL、网页摘要、网站名称、网页发布时间。"
)
llm_with_tools = llm.bind_tools(tools=[tool])

def chatbot(state: State):
    # 使用 llm 根据当前状态的消息列表生成回复
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 添加节点: key 是唯一标识, value 是节点对应的函数或对象
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# 添加边
# tools_condition: 如果最后一条消息包含 tool calls, 则在 conditional_edge 中使用，路由至 ToolNode, 否则路由至末尾
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每当调用一个工具时, 我们都会返回聊天机器人来决定下一步
graph_builder.add_edge("tools", "chatbot")
# 指定图中要调用的第一个节点,
# graph_builder.set_entry_point("chatbot") 相当于 graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

# 生成图结构图
# with open(os.path.dirname(__file__) + "/demo_3_graph.mmd", "w", encoding="utf-8") as file:
#     file.write(graph.get_graph().draw_mermaid())

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