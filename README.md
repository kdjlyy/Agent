## 项目链接

| 序号  | 模块链接                                                         | 功能简介                                                                                           |
|-----|--------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1   | [LangGraphChatBot](https://github.com/kdjlyy/LangGraphChatBot) | [演示地址](http://14.103.121.86:8090/)<br>基于 LangChain 和 LangGraph 的 AI 聊天机器人，拥有回答问题、生成文章、联网搜索、处理文件等功能 |
| 2   | [LangGraph 基础](./langgraph_demo/README.md) | LangChain、LangGraph 框架基础使用演示 |
| 3   | [MCP 服务端和客户端实现](./mcp/README.md) | 基于 FastMCP 实现的 MCP Server 和 MCP Client，支持动态工具调用和交互式对话 |                                                                                                 |

## 目录结构

> 项目主要使用Python 3.11+，依赖包括LangChain、LangGraph等AI框架，主要用于构建聊天机器人、RAG系统和多代理系统。代码中包含大量Jupyter notebook演示文件(.ipynb)和Python脚本。

1. **根目录**：

   包含了项目的主要配置文件（如`.env`、`pyproject.toml`等）和运行脚本（如`run.sh`）。

2. **子目录**：
   - `chat_bot/`：聊天机器人相关代码。
   - `langchain_demo/`：`LangChain`框架演示代码。
   - `langgraph_demo/`：`LangGraph`框架演示代码，包含多个示例文件和Notebook。
   - `mcp/`：数学计算服务相关代码。
   - `rag/`：RAG（检索增强生成）相关代码和PDF处理。
   - `utils/`：工具函数（如环境变量加载）。
   - `vector_store/`：向量存储相关代码。
3. **资源文件**：

   `resources/`目录下存放了生成的`Mermaid`文件，用于可视化图结构。
