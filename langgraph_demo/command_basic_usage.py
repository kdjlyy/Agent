""" Command 基本用法 """
import random
from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START
from langgraph.types import Command

# 定义 State
class State(TypedDict):
    foo: str

# 节点函数中返回 Command 时，必须添加返回类型注解，列出该节点要路由到的节点名称
def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["a", "b"])
    # 根据条件返回不同的节点（与条件边类似）
    if value == "a":
        goto = "node_b"
    else:
        goto = "node_c"

    # 同一个节点中既执行状态更新，又决定接下来要前往哪个节点，可以返回 Command 类型
    return Command(
        # 更新 State
        update={"foo": value},
        # goto 标识要前往的节点
        goto=goto,
    )

def node_b(state: State):
    print("Called B")
    return {"foo": state["foo"] + "b"}


def node_c(state: State):
    print("Called C")
    return {"foo": state["foo"] + "c"}

builder = StateGraph(State)
builder.add_edge(START, "node_a")
builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)
# 注意，该图没有用于路由的条件边！这是因为控制流是在 node_a 内部使用 Command 定义的

graph = builder.compile()

# graph.get_graph().print_ascii()
#         +-----------+          
#         | __start__ |          
#         +-----------+          
#                *               
#                *               
#                *               
#           +--------+           
#           | node_a |           
#           +--------+           
#           .         .          
#         ..           ..        
#        .               .       
# +--------+          +--------+ 
# | node_b |          | node_c | 
# +--------+          +--------+ 


# 如果我们多次运行该图，我们会看到它根据节点 A 中的随机选择走不同的路径（A -> B 或 A -> C）
graph.invoke({"foo": ""})