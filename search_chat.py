from langchain.agents import ConversationalChatAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
import streamlit as st
from utils.env_util import load_env_vars
from utils.search import bocha_websearch_tool

# 仅首次执行
env_vars = load_env_vars()

with st.sidebar:
    # 下拉框
    env_vars['CURRENT_MODEL'] = st.selectbox(
        label="选择模型",
        options=env_vars["MODEL_LIST"],
        index=3,
        help="选择 LLM 模型的种类",
    )
    env_vars['NET_ENABLE'] = st.selectbox(
        label="联网搜索",
        options=['打开','关闭'],
        index=1,
        help="选择是否打开联网搜索",
    )
    # 滑动条
    env_vars['TEMPERATURE'] = st.slider(
        label="Temperature",
        min_value=0.0, max_value=1.0, value=0.0,
        help="Temperature 参数用于控制 LLM 的输出多样性和确定性，高 Temperature 增加多样性但可能降低确定性，低 Temperature 则增加确定性但可能降低多样性。"
    )

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)
if len(msgs.messages) == 0 or st.sidebar.button("重置聊天上下文"):
    msgs.clear()
    msgs.add_ai_message("有问题欢迎向我提问～")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # 渲染中间步骤（如果已保存）
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

if prompt := st.chat_input(placeholder="shift+enter 换行"):
    st.chat_message("user").write(prompt)
    llm = ChatOpenAI(
        openai_api_key=env_vars["OPENAI_API_KEY"],
        model_name=env_vars["CURRENT_MODEL"],
        temperature=env_vars["TEMPERATURE"],
        base_url=env_vars["OPENAI_BASE_URL"],
        streaming=True,
    )
    # 创建LangChain工具
    bocha_tool = Tool(
        name="BochaWebSearch",
        func=bocha_websearch_tool,
        description="使用 Bocha Web Search API 进行搜索互联网网页，输入应为搜索查询字符串，输出将返回搜索结果的详细信息，包括网页标题、网页 URL、网页摘要、网站名称、网页发布时间。"
    )
    tools = [bocha_tool] if env_vars['NET_ENABLE']=='打开' else []
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke(prompt, cfg)
        st.write(response["output"])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
