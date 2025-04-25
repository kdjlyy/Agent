import operator
import random
from typing_extensions import TypedDict, Literal
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START
from langgraph.types import Command

class State(TypedDict):
    # NOTE: 当你从子图节点向父图节点发送针对某个键的更新，且该键在父图和子图的状态模式中都存在时，
    # 你必须为你要在父图状态中更新的键定义一个归约器
    foo: Annotated[str, operator.add]

def node_a(state: State):
    print("Called A")
    value = random.choice(["b", "c"])
    goto = "node_b" if value == "b" else "node_c"

    # Command 命令允许你更新图状态和路由到下一个节点
    return Command(
        update={"foo": value},
        goto=goto,
        # 告诉 LangGraph 导航到父图中的 node_b 或 node_c
        # NOTE：这将导航到相对于子图最近的父图
        graph=Command.PARENT,
    )

# node_a是一个子图节点，它返回一个 Command，该 Command 指示 LangGraph 导航到父图中的 node_b 或 node_c
subgraph = StateGraph(State).add_node(node_a).add_edge(START, "node_a").compile()

def node_b(state: State) -> Command[Literal["node_b"]]:
    print("Called B")
    # NOTE: 因为我们已经定义了一个归约器，所以不需要手动向现有的 foo 值添加新字符。
    # reducer 会自动添加这些（通过 operator.add）
    return {"foo": "b"}

def node_c(state: State) -> Command[Literal["node_c"]]:
    print("Called C")
    return {"foo": "c"}

builder = StateGraph(State)
builder.add_edge(START, "subgraph")
builder.add_node("subgraph", subgraph)

# 这样写做不到可视化
builder.add_node(node_b)
builder.add_node(node_c)

graph = builder.compile()

print(graph.get_graph().print_ascii())

res = graph.invoke({"foo": ""})
print(res)