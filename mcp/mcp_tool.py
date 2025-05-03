import csv
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP Tools Integrated")

@mcp.tool()
def get_task_by_id(task_id: int) -> str:
    """
    根据任务 ID 从 task.csv 文件中读取任务详情。

    :param task_id: 任务 ID
    :return: 任务详情字符串，如果未找到任务则返回相应的提示信息
    """
    # 定义文件路径
    file_path = os.path.join(os.path.dirname(__file__), "task.csv")

    # 读取 CSV 文件
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["Task ID"]) == task_id:
                # 将任务详情格式化为字符串
                return f"Task ID: {row['Task ID']}, Description: {row['Description']}, Status: {row['Status']}"

    # 如果未找到任务，返回提示信息
    return f"未找到任务 ID 为 {task_id} 的任务"

@mcp.tool(description="获取一个城市的天气信息,输入和输出都是字符串类型")
def weather(city:  str) -> str:
    """Get the weather of a city"""
    return f"The weather in {city} is sunny."

# 示例调用
if __name__ == "__main__":
    print(f"mcp server started!")
    mcp.run(transport="stdio")