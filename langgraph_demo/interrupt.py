""" 人工介入的工作流（通过 interrupt 实现） """
from typing import TypedDict
import uuid
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

class State(TypedDict):
    """图的状态"""
    text: str
   
   

def human_node(state: State):
   value = interrupt(
      # 任何可进行 JSON 序列化的值，用于展示给人类。
      # 例如，一个问题、一段文本或状态中的一组键
      {"text_to_revise": state["text"]}
   )
   return {
      # 使用人类的输入更新状态
      "text": value
   }


# 构建图
graph_builder = StateGraph(State)
# 将 human-node 添加到图中
graph_builder.add_node("human_node", human_node)
graph_builder.add_edge(START, "human_node")
graph_builder.add_edge("human_node", END)

# `interrupt` 正常工作需要一个检查点
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

# 向图传递一个线程 ID 以运行它。
thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
# 使用 stream() 直接展示 `__interrupt__` 信息。
for chunk in graph.stream({"text": "删除用户 Tom 的数据"}, config=thread_config):
    if chunk["__interrupt__"]:
        print(f'产生中断需要人工介入, 用户请求为: {chunk["__interrupt__"][0].value.get("text_to_revise")}')

    # 产生中断需要人工介入, 用户请求为: 删除用户 Tom 的数据

# 使用 Command 恢复执行
for chunk in graph.stream(Command(resume="同意"), config=thread_config):
   print(chunk)

   # {'human_node': {'text': '同意'}}
