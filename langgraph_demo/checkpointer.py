from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]

def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}

def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}

workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
# graph.get_state(config) 来查看图的最新状态
print(graph.get_state(config))

    # StateSnapshot(
    #   values={}, # 此时 State 的值
    #   next=(), # 图中接下来要执行的节点名称的元组
    #   config={'configurable': {'thread_id': '1'}}, # 与此检查点关联的配置
    #   metadata=None, # 与此检查点关联的元数据
    #   created_at=None, 
    #   parent_config=None, 
    #   tasks=() # PregelTask 对象的元组，包含有关接下来要执行的任务的信息
    # )


res = graph.invoke({"foo": ""}, config)

# graph.get_state_history(config) 来获取给定线程的图执行的完整历史记录
# 检查点将按时间顺序排序，最新的检查点 / StateSnapshot 将位于列表的首位
print(list(graph.get_state_history(config)))

    # [
    #     StateSnapshot(
    #         values={'foo': 'b', 'bar': ['a', 'b']}, 
    #         next=(), 
    #         config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd8-6de5-8002-0c8309f7d2d2'}}, 
    #         metadata={'source': 'loop', 'writes': {'node_b': {'foo': 'b', 'bar': ['b']}}, 'step': 2, 'parents': {}, 'thread_id': '1'}, 
    #         created_at='2025-04-23T06:21:45.071553+00:00', 
    #         parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd7-669e-8001-21fdf44bf9b7'}}, 
    #         tasks=()
    #     ), 
    #     StateSnapshot(
    #         values={'foo': 'a', 'bar': ['a']}, 
    #         next=('node_b',), 
    #         config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd7-669e-8001-21fdf44bf9b7'}}, 
    #         metadata={'source': 'loop', 'writes': {'node_a': {'foo': 'a', 'bar': ['a']}}, 'step': 1, 'parents': {}, 'thread_id': '1'}, 
    #         created_at='2025-04-23T06:21:45.070957+00:00', 
    #         parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd5-6b14-8000-599fcd551f38'}}, 
    #         tasks=(
    #             PregelTask(id='6d83ec90-68b6-bc12-54dc-dc6c4152ce02', name='node_b', path=('__pregel_pull', 'node_b'), error=None, interrupts=(), state=None, result={'foo': 'b', 'bar': ['b']}),
    #         )
    #     ), 
    #     StateSnapshot(
    #         values={'foo': '', 'bar': []}, 
    #         next=('node_a',), 
    #         config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd5-6b14-8000-599fcd551f38'}}, 
    #         metadata={'source': 'loop', 'writes': None, 'step': 0, 'parents': {}, 'thread_id': '1'}, 
    #         created_at='2025-04-23T06:21:45.070251+00:00', 
    #         parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd3-6d9e-bfff-a7e2d26c9556'}}, 
    #         tasks=(
    #             PregelTask(id='b096fffb-c3c9-1be6-4b9f-eb1c5950e8e6', name='node_a', path=('__pregel_pull', 'node_a'), error=None, interrupts=(), state=None, result={'foo': 'a', 'bar': ['a']}),
    #         )
    #     ), 
    #     StateSnapshot(
    #         values={'bar': []}, 
    #         next=('__start__',), 
    #         config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f0200b3-abd3-6d9e-bfff-a7e2d26c9556'}}, 
    #         metadata={'source': 'input', 'writes': {'__start__': {'foo': ''}}, 'step': -1, 'parents': {}, 'thread_id': '1'}, 
    #         created_at='2025-04-23T06:21:45.069500+00:00', 
    #         parent_config=None, 
    #         tasks=(
    #             PregelTask(id='4f034a8a-806e-f817-a6ab-6e2663834c62', name='__start__', path=('__pregel_pull', '__start__'), error=None, interrupts=(), state=None, result={'foo': ''}),
    #         )
    #     )
    # ]