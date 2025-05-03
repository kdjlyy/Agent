## 核心功能

### MCP Server
`mcp_tool.py` 提供了以下工具函数：
- `get_task_by_id(task_id: int)` 根据任务 ID 从 `task.csv` 文件中读取任务详情。 

  示例输出：`Task ID: 1, Description: Develop a new feature, Status: In Progress`

- `weather(city: str)` 获取指定城市的天气信息。 

  示例输出：`The weather in Beijing is sunny.`

### MCP Client
`client.py` 实现了以下功能：
1. 连接服务器

    MCP 客户端通过 `connect_to_server` 方法连接到 MCP 服务器，并列出可用工具。

2. 动态工具调用 

    客户端支持动态调用服务器提供的工具函数，例如查询任务详情或获取天气信息。

3. 交互式对话

    客户端提供交互式命令行界面，用户可以通过输入查询任务详情或获取天气信息

## 使用说明

1. 安装好对应的依赖，将 OpenAI 所需的环境变量写入 `.env` 文件；
2. 指定 MCP Server 的文件路径，启动 MCP Client `uv run client.py <ABSOLUTE_PATH>/mcp_tool.py`

## 输出示例
> 这里使用的模型是Qwen/Qwen2.5-7B-Instruct
```shell
[05/03/25 17:58:25] INFO     Processing request of type ListToolsRequest                                                                                             server.py:534

Connected to server with tools: ['get_task_by_id', 'weather']

MCP Client Started!
Type your queries or 'quit' to exit.

Query: 查询任务ID为2的任务详情
[05/03/25 17:58:37] INFO     Processing request of type ListToolsRequest                                                                                             server.py:534
[05/03/25 17:58:40] INFO     Processing request of type CallToolRequest                                                                                              server.py:534


[Calling tool get_task_by_id with args {'task_id': 2}]

任务ID为2的任务详情如下：
- 任务描述：Develop math calculation server
- 当前状态：已完成（Completed）

这个任务已经成功完成，其核心目标是研发一个数学计算服务系统。如果有其他需要查询的任务ID，请随时告知。

Query: 查询北京天气
[05/03/25 17:59:16] INFO     Processing request of type ListToolsRequest                                                                                             server.py:534
[05/03/25 17:59:21] INFO     Processing request of type CallToolRequest                                                                                              server.py:534


[Calling tool weather with args {'city': '北京'}]

北京今天天气晴朗，适合外出活动。

Query: 

```
