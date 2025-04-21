# math_server.py
from mcp.server.fastmcp import FastMCP

# 注册智能体
mcp = FastMCP("Math Demo")
# SSE 方式
# mcp = FastMCP("Math Demo", port=5000)
# mcp.run(transport="sse")

# @mcp.tool() 用于将普通函数注册为智能体可调用的工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    # 使用标准输入输出（命令行）作为交互通道，用户通过命令行输入查询，智能体返回结果。
    mcp.run(transport="stdio")