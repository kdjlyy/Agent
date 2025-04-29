
1. **项目配置文件**：
   - `.env`和`.env.example` - 环境变量配置文件
   - `pyproject.toml` - Python项目依赖配置文件
   - `requirements.txt` - 传统requirements文件
   - `uv.lock` - UV包管理器的锁文件

2. **版本控制**：
   - `.git/` - Git版本控制目录
   - `.gitignore` - Git忽略规则

3. **虚拟环境**：
   - `.venv/` - Python虚拟环境目录

4. **主要代码目录**：
   - `chat_bot/` - 聊天机器人相关代码
   - `langgraph_demo/` - LangGraph框架演示代码(包含多个demo和notebook)
   - `langchain_demo/` - LangChain框架演示代码
   - `mcp/` - 数学计算服务相关代码
   - `rag/` - RAG(检索增强生成)相关代码和PDF处理
   - `utils/` - 工具函数(环境变量加载等)
   - `vector_store/` - 向量存储相关代码

5. **其他文件**：
   - `README.md` - 项目说明文档
   - `run.sh` - 运行脚本
   - `output.txt` - 输出日志
   - `.vscode/` - VSCode编辑器配置

项目主要使用Python 3.11+，依赖包括LangChain、LangGraph等AI框架，主要用于构建聊天机器人、RAG系统和多代理系统。代码中包含大量Jupyter notebook演示文件(.ipynb)和Python脚本。

---

- [LangGraph 基础](./langgraph_demo/README.md)
