import os

from langgraph.graph.state import CompiledStateGraph

def gen_mermaid(graph: CompiledStateGraph, file_name: str):
    """ 生成 graph 对应的 mermaid 文件 """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', file_name))
    with open(path, "w", encoding="utf-8") as file:
        file.write(graph.get_graph().draw_mermaid())
    print(f"✏️ 已生成 mermaid 文件 {path}")

# NOTE: to be fixed
def gen_mermaid_png(graph: CompiledStateGraph, file_name: str):
    """ 生成 graph 对应的 mermaid 图片 """
    if file_name.endswith(".png"):
        pic_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', file_name))
        with open(pic_path, "wb") as file:
            file.write(graph.get_graph().draw_mermaid_png())
    else:
        raise ValueError("file_name must end with .png")
