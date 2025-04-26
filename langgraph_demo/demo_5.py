"""在线搜索+流式输出+时间回溯的聊天机器人示例"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from tools.search import websearch_tool
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langchain.agents import Tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


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
    func=websearch_tool,
    description="搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页 URL、网页摘要、网站名称、网页发布时间。"
)

tools=[search_tool]
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
# tools_condition: 如果最后一条消息包含 tool calls, 则在 conditional_edge 中使用，路由至 tools, 否则路由至末尾
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

# 生成图结构图
# with open(os.path.dirname(__file__) + "/demo_3_graph.mmd", "w", encoding="utf-8") as file:
#     file.write(graph.get_graph().draw_mermaid())


# step 1
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I'm learning LangGraph. "
                    "Could you do some research on it for me?"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
# step 2
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Ya that's helpful. Maybe I'll "
                    "build an autonomous agent with it!"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

to_replay = None
for state in graph.get_state_history(config):
    print("Num Messages:", len(state.values["messages"]), "  Next:", state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 2:
        # 根据该状态中的聊天消息数量任意选择一个特定的状态
        to_replay = state

# Num Messages:  6 Next:  ()
# --------------------------------------------------------------------------------
# Num Messages:  5 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  4 Next:  ('__start__',)
# --------------------------------------------------------------------------------
# Num Messages:  4 Next:  ()
# --------------------------------------------------------------------------------
# Num Messages:  3 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  2 Next:  ('tools',)
# --------------------------------------------------------------------------------
# Num Messages:  1 Next:  ('chatbot',)
# --------------------------------------------------------------------------------
# Num Messages:  0 Next:  ('__start__',)
# --------------------------------------------------------------------------------

# 每一步都会保存检查点，可以回溯整个线程的历史记录。我们选择了 to_replay 作为恢复的状态
print("*" * 80)
print(to_replay.next)
print(to_replay.config)
print("*" * 80)

# The `checkpoint_id` in the `to_replay.config` corresponds to a state we've persisted to our checkpointer.
# 从第2步开始回放，重新进行网页搜索功能
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()