"""在线搜索+人工干预的聊天机器人示例"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from tools.search import bocha_websearch_tool
from tools.human_assistance import human_assistance
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langchain.agents import Tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


# State 是一个 TypedDict, 其中包含一个键: messages
# add_messages 是 reducer 函数, 用于将新消息附加到列表中, 而不是覆盖它。
class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

llm = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name=get_default_model(),
    base_url=get_openai_base_url(),
)

# 创建LangChain工具
search_tool = Tool(
    name="在线搜索",
    func=bocha_websearch_tool,
    description="搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页 URL、网页摘要、网站名称、网页发布时间。"
)

tools=[search_tool, human_assistance]
llm_with_tools = llm.bind_tools(tools=tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # 使用 llm 根据当前状态的消息列表生成回复
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)
# 添加节点: key 是唯一标识, value 是节点对应的函数或对象
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# 添加边
# tools_condition: 如果最后一条消息包含 tool calls, 则在 conditional_edge 中使用，路由至 ToolNode, 否则路由至末尾
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 每当调用一个工具时, 我们都会返回聊天机器人来决定下一步
graph_builder.add_edge("tools", "chatbot")
# 指定图中要调用的第一个节点,
# graph_builder.set_entry_point("chatbot") 相当于 graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge(START, "chatbot")

# MemorySaver 将所有内容都保存在内存中，生产中可能会用到 SqliteSaver 或 PostgresSaver 将数据持久化
# 在图遍历每个节点时对 State 进行检查点操作
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# 应用程序查找 LangGraph 库的“诞生日期”。
# 一旦聊天机器人获得所需信息，我们将引导它调用 human_assistance 工具
user_input = (
    "Can you look up when LangGraph was released? "
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# 在 human_assistance 工具中会遇到 interrupt。在这种情况下，聊天机器人未能识别出正确的日期，因此我们可以提供该日期：
human_command = Command(
    resume={
        "name": "LangGraph",
        "birthday": "Jan 17, 2024",
    },
)

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# 这些字段现在已反映在状态中
# 这使得下游节点（例如，进一步处理或存储信息的节点）能够轻松访问这些信息
snapshot = graph.get_state(config)
print('============ STATE ===============')
print({k: v for k, v in snapshot.values.items() if k in ("name", "birthday")})