import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.search import bocha_websearch_tool
from langchain.agents import Tool

# 创建LangChain工具
tool = Tool(
    name="🔍在线搜索",
    func=bocha_websearch_tool,
    description="搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页 URL、网页摘要、网站名称、网页发布时间。"
)

tools = [tool]

print(tool.invoke("LangGraph的节点是什么"))

