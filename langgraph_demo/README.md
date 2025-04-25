## LangGraph 基础 

1. [Command 基本用法：状态更新和导航](./command_basic_usage.py)  

    在同一个节点中既执行状态更新，又决定接下来要前往哪个节点

2. [Command 进阶用法：子图导航到父图](./command_extend_usage.py)  

    从子图内部导航到父图中的不同节点

3. [LangGraph 持久化 - checkpointer 基本用法](./checkpointer.py)   

    ![](./resources/checkpoint.png)  
    在编译图时传入一个检查点保存器（`checkpointer`），并在 `invoke` 时传入一个 config，用于指定线程 ID


4. [LangGraph 持久化应用于连续聊天](./persistence_storage.py)  

5. [LangGraph 重放](./checkpointer_replay.py)  

    - 要从某个位置重新开始重新执行，我们只需将对应位置的 `State` 配置信息传递回 Agent
    - 重新执行某个状态时，我们还可以通过修改 `State` 的值来更改过去的状态

    ⚠️实现此功能需要传入一个检查点器，使用的关键方法有：  
    - `get_state`：从目标配置中获取值  
    - `update_state`：将给定的值应用到目标状态

6. [LangGraph 中断（interrupt）](./interrupt.py)  
    
    LangGraph 中的 `interrupt` 函数 可通过在特定节点暂停图、向人类展示信息并使用人类输入恢复图的执行，从而实现人工介入的工作流。`interrupt` 函数与 `Command` 对象结合使用，以使用人类提供的值恢复图的执行。

    要在你的图中使用 `interrupt`，你需要：
    1. 指定一个检查点保存器，以在每一步之后保存图的状态
    2. 在适当的位置调用 `interrupt()`
    3. 使用线程 ID 运行图，直到遇到 `interrupt`
    4. 使用 `invoke`/`ainvoke`/`stream`/`astream` 恢复执行

7. [LangGraph 人工审核](./human_review.ipynb)  

   ```mermaid
   graph TD;
       __start__([<p>__start__</p>]):::first
       call_llm(call_llm)
       run_tool(run_tool)
       human_review_node(human_review_node)
       __end__([<p>__end__</p>]):::last
       __start__ --> call_llm;
       run_tool --> call_llm;
       call_llm -.-> __end__;
       call_llm -.-> human_review_node;
       human_review_node -.-> call_llm;
       human_review_node -.-> run_tool;
       classDef default fill:#f2f0ff,line-height:1.2
       classDef first fill-opacity:0
       classDef last fill:#bfb6fc
   ```

    一次人工审核通过的工具调用的流程如下：
    1. 用户输入：“上海天气怎么样？”，生成 `HumanMessage`
    2. 从 `START` 节点流转到 `call_llm` 节点，调用 LLM，LLM 判断需要调用 `Tools`, 生成了带 `tool_call` 信息的 `AIMessage`
    3. `route_after_llm` 把流程从 `call_llm` 节点路由到 `human_review_node` 节点，调用了 `interrupt()` 产生中断，人工介入后同意调用工具，从 `human_review_node` 节点流转到 `run_tool` 节点
    4. `run_tool` 调用工具，生成 `ToolMessage`，内容存放在 `ToolMessage` 的 `content` 字段
    5. 从 `run_tool` 节点流转到 `call_llm` 节点，调用 LLM，LLM 根据返回的结果判断已经不需要调用 `Tools` 了, 生成普通的 `AIMessage`
    6. `route_after_llm` 把流程从 `call_llm` 节点路由到 `END`，流程结束

8. [LangGraph 并行执行](./map_reduce.ipynb)  

   ```mermaid
   graph TD;
       __start__([<p>__start__</p>]):::first
       generate_topics(generate_topics)
       generate_joke(generate_joke)
       best_joke(best_joke)
       __end__([<p>__end__</p>]):::last
       __start__ --> generate_topics;
       best_joke --> __end__;
       generate_joke --> best_joke;
       generate_topics -.-> generate_joke;
       classDef default fill:#f2f0ff,line-height:1.2
       classDef first fill-opacity:0
       classDef last fill:#bfb6fc
   ```
    
    Map-Reduce 将一个任务分解为较小的子任务，并行处理每个子任务，并汇总所有已完成子任务的结果。  
    LangGraph 的 `Send` 可以实现类似的功能，将不同的状态（例如，主题）分发到一个节点的多个实例（例如，文章生成）。重要的是，发送的状态可以与核心图的状态不同，从而实现灵活和动态的工作流管理。

9. [LangGraph 多 Agent 调用（监督者模式）](./multi_agent_supervisor.ipynb)

    ```mermaid
    graph TD;
        __start__([<p>__start__</p>]):::first
        supervisor(supervisor)
        researcher(researcher)
        coder(coder)
        __end__([<p>__end__</p>]):::last
        __start__ --> supervisor;
        supervisor -.-> researcher;
        supervisor -.-> coder;
        supervisor -.-> __end__;
        researcher -.-> supervisor;
        coder -.-> supervisor;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
    ```

    多 Agnet 系统的介绍参考：[多 Agent 系统](https://langgraphcn.org/concepts/multi_agent/)  

10. [LangGraph 多 Agent 多轮对话）](./multi_agent_multi_turn_convo.ipynb)  

    ```mermaid
    graph TD;
        __start__([<p>__start__</p>]):::first
        travel_advisor(travel_advisor)
        hotel_advisor(hotel_advisor)
        human(human)
        __start__ --> travel_advisor;
        travel_advisor -.-> hotel_advisor;
        travel_advisor -.-> human;
        hotel_advisor -.-> travel_advisor;
        hotel_advisor -.-> human;
        human -.-> hotel_advisor;
        human -.-> travel_advisor;
        human -.-> human;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
    ```

    参考：[如何在多智能体应用程序中添加多轮对话](https://langgraphcn.org/how-tos/multi-agent-multi-turn-convo/)

11. [LangGraph 函数式 API](./functional_api.ipynb)

    使用 `@entrypoint` 和 `@task` 装饰器，可以轻松地创建函数式 API。  
    参考：[函数式 API](https://langgraphcn.org/concepts/functional_api/)
    
---

参考  
- [LangGraph API](https://langgraphcn.org/reference/graphs/)
