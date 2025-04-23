import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import MessagesState, START
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver


@tool
def play_song_on_spotify(song: str):
    """Play a song on Spotify"""
    return f"Successfully played {song} on Spotify!"

@tool
def play_song_on_apple(song: str):
    """Play a song on Apple Music"""
    return f"Successfully played {song} on Apple Music!"


tools = [play_song_on_apple, play_song_on_spotify]
tool_node = ToolNode(tools)

# 定义模型
llm = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    model_name=get_default_model(),
    base_url=get_openai_base_url(),
    temperature=0.0
)
llm = llm.bind_tools(tools, parallel_tool_calls=False)

# 定义是否继续的函数
def should_continue(state):
    last_message = state["messages"][-1]
    # 如果最后一次对话的消息没有调用工具就结束（）
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# 定义调用模型的节点
def call_model(state):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("action", tool_node)

# 添加边
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        # 如果继续则调用工具（在 Spotify 或 Apple Music 播放音乐），否则直接结束
        "continue": "action",
        "end": END,
    },
)
builder.add_edge("action", "agent")
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# graph.get_graph().print_ascii()
    #         +-----------+           
    #         | __start__ |           
    #         +-----------+           
    #               *                
    #               *                
    #               *                
    #           +-------+             
    #    |----> | agent | <- 调用模型节点            
    #    |      +-------+ 
    #    |          |           
    #    |    should_continue
    #    |       /       \
    #    |      /         \           
    #    |     /           \         
    #    |    /             \        
    # +--------+           +---------+  
    # | action |<-工具节点  | __end__ |  
    # +--------+           +---------+ 

# 1.与 Agent 交互，让其播放音乐
from langchain_core.messages import HumanMessage
config = {"configurable": {"thread_id": "1"}}
input_message = HumanMessage(content="在任意一个平台播放周杰伦的歌曲《七里香》")
for event in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

    # ================================ Human Message =================================
    # 播放周杰伦的歌曲《七里香》
    # ================================== Ai Message ==================================
    # Tool Calls:
    #   play_song_on_spotify (01966198d4c55ed8e21e90de11d58f11)
    #  Call ID: 01966198d4c55ed8e21e90de11d58f11
    #   Args:
    #     song: 七里香 周杰伦
    # ================================= Tool Message =================================
    # Name: play_song_on_spotify
    # Successfully played 七里香 周杰伦 on Spotify!
    # ================================== Ai Message ==================================
    # 已为您在Spotify上播放周杰伦的《七里香》。如果有其他需要，请随时告诉我！

# 2.查看历史记录
all_states = [] # 保存所有状态
for state in graph.get_state_history(config):
    # print(state)
    all_states.append(state)

    # StateSnapshot(values={'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={}, id='e3289d01-760b-413f-afc1-f2e74e884fcb'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '019661af5b6bfd30027c61b795c82271', 'function': {'arguments': '{"song": "七里香"}', 'name': 'play_song_on_spotify'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 223, 'prompt_tokens': 232, 'total_tokens': 455, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af2861e962dd5c92d2ab149b9b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-05855964-2bda-4de4-9fc9-56311ef7a19b-0', tool_calls=[{'name': 'play_song_on_spotify', 'args': {'song': '七里香'}, 'id': '019661af5b6bfd30027c61b795c82271', 'type': 'tool_call'}], usage_metadata={'input_tokens': 232, 'output_tokens': 223, 'total_tokens': 455, 'input_token_details': {}, 'output_token_details': {}}), ToolMessage(content='Successfully played 七里香 on Spotify!', name='play_song_on_spotify', id='61c1f761-e3f2-42b3-b535-43da62543b64', tool_call_id='019661af5b6bfd30027c61b795c82271'), AIMessage(content='已为您在Spotify上播放周杰伦的《七里香》。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 317, 'prompt_tokens': 294, 'total_tokens': 611, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af5bcd82c28ab65faae58d8070', 'finish_reason': 'stop', 'logprobs': None}, id='run-406a5bb8-bd2d-4dc4-8ea5-27745b90ecd0-0', usage_metadata={'input_tokens': 294, 'output_tokens': 317, 'total_tokens': 611, 'input_token_details': {}, 'output_token_details': {}})]}, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019f-006f-695b-8003-e4babd93fe7e'}}, metadata={'source': 'loop', 'writes': {'agent': {'messages': [AIMessage(content='已为您在Spotify上播放周杰伦的《七里香》。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 317, 'prompt_tokens': 294, 'total_tokens': 611, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af5bcd82c28ab65faae58d8070', 'finish_reason': 'stop', 'logprobs': None}, id='run-406a5bb8-bd2d-4dc4-8ea5-27745b90ecd0-0', usage_metadata={'input_tokens': 294, 'output_tokens': 317, 'total_tokens': 611, 'input_token_details': {}, 'output_token_details': {}})]}}, 'step': 3, 'parents': {}, 'thread_id': '1'}, created_at='2025-04-23T08:07:02.174531+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019e-56a1-62ba-8002-3fd8c1115d87'}}, tasks=())
    # StateSnapshot(values={'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={}, id='e3289d01-760b-413f-afc1-f2e74e884fcb'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '019661af5b6bfd30027c61b795c82271', 'function': {'arguments': '{"song": "七里香"}', 'name': 'play_song_on_spotify'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 223, 'prompt_tokens': 232, 'total_tokens': 455, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af2861e962dd5c92d2ab149b9b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-05855964-2bda-4de4-9fc9-56311ef7a19b-0', tool_calls=[{'name': 'play_song_on_spotify', 'args': {'song': '七里香'}, 'id': '019661af5b6bfd30027c61b795c82271', 'type': 'tool_call'}], usage_metadata={'input_tokens': 232, 'output_tokens': 223, 'total_tokens': 455, 'input_token_details': {}, 'output_token_details': {}}), ToolMessage(content='Successfully played 七里香 on Spotify!', name='play_song_on_spotify', id='61c1f761-e3f2-42b3-b535-43da62543b64', tool_call_id='019661af5b6bfd30027c61b795c82271')]}, next=('agent',), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019e-56a1-62ba-8002-3fd8c1115d87'}}, metadata={'source': 'loop', 'writes': {'action': {'messages': [ToolMessage(content='Successfully played 七里香 on Spotify!', name='play_song_on_spotify', id='61c1f761-e3f2-42b3-b535-43da62543b64', tool_call_id='019661af5b6bfd30027c61b795c82271')]}}, 'step': 2, 'parents': {}, 'thread_id': '1'}, created_at='2025-04-23T08:06:44.369058+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019e-569b-6169-8001-d08ca6b25681'}}, tasks=(PregelTask(id='5e1656ae-9138-ebb0-0453-25951fe33ec1', name='agent', path=('__pregel_pull', 'agent'), error=None, interrupts=(), state=None, result={'messages': [AIMessage(content='已为您在Spotify上播放周杰伦的《七里香》。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 317, 'prompt_tokens': 294, 'total_tokens': 611, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af5bcd82c28ab65faae58d8070', 'finish_reason': 'stop', 'logprobs': None}, id='run-406a5bb8-bd2d-4dc4-8ea5-27745b90ecd0-0', usage_metadata={'input_tokens': 294, 'output_tokens': 317, 'total_tokens': 611, 'input_token_details': {}, 'output_token_details': {}})]}),))
    # StateSnapshot(values={'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={}, id='e3289d01-760b-413f-afc1-f2e74e884fcb'), AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '019661af5b6bfd30027c61b795c82271', 'function': {'arguments': '{"song": "七里香"}', 'name': 'play_song_on_spotify'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 223, 'prompt_tokens': 232, 'total_tokens': 455, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af2861e962dd5c92d2ab149b9b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-05855964-2bda-4de4-9fc9-56311ef7a19b-0', tool_calls=[{'name': 'play_song_on_spotify', 'args': {'song': '七里香'}, 'id': '019661af5b6bfd30027c61b795c82271', 'type': 'tool_call'}], usage_metadata={'input_tokens': 232, 'output_tokens': 223, 'total_tokens': 455, 'input_token_details': {}, 'output_token_details': {}})]}, next=('action',), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019e-569b-6169-8001-d08ca6b25681'}}, metadata={'source': 'loop', 'writes': {'agent': {'messages': [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '019661af5b6bfd30027c61b795c82271', 'function': {'arguments': '{"song": "七里香"}', 'name': 'play_song_on_spotify'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 223, 'prompt_tokens': 232, 'total_tokens': 455, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af2861e962dd5c92d2ab149b9b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-05855964-2bda-4de4-9fc9-56311ef7a19b-0', tool_calls=[{'name': 'play_song_on_spotify', 'args': {'song': '七里香'}, 'id': '019661af5b6bfd30027c61b795c82271', 'type': 'tool_call'}], usage_metadata={'input_tokens': 232, 'output_tokens': 223, 'total_tokens': 455, 'input_token_details': {}, 'output_token_details': {}})]}}, 'step': 1, 'parents': {}, 'thread_id': '1'}, created_at='2025-04-23T08:06:44.366557+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019d-d8bb-6398-8000-214a1c710086'}}, tasks=(PregelTask(id='ba13b98a-619d-738d-c88c-d864b324297f', name='action', path=('__pregel_pull', 'action'), error=None, interrupts=(), state=None, result={'messages': [ToolMessage(content='Successfully played 七里香 on Spotify!', name='play_song_on_spotify', id='61c1f761-e3f2-42b3-b535-43da62543b64', tool_call_id='019661af5b6bfd30027c61b795c82271')]}),))
    # StateSnapshot(values={'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={}, id='e3289d01-760b-413f-afc1-f2e74e884fcb')]}, next=('agent',), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019d-d8bb-6398-8000-214a1c710086'}}, metadata={'source': 'loop', 'writes': None, 'step': 0, 'parents': {}, 'thread_id': '1'}, created_at='2025-04-23T08:06:31.167672+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019d-d8b8-6963-bfff-34aa14fb6ea5'}}, tasks=(PregelTask(id='3810f784-f722-dbc9-36ed-8e93c954e402', name='agent', path=('__pregel_pull', 'agent'), error=None, interrupts=(), state=None, result={'messages': [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': '019661af5b6bfd30027c61b795c82271', 'function': {'arguments': '{"song": "七里香"}', 'name': 'play_song_on_spotify'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 223, 'prompt_tokens': 232, 'total_tokens': 455, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661af2861e962dd5c92d2ab149b9b', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-05855964-2bda-4de4-9fc9-56311ef7a19b-0', tool_calls=[{'name': 'play_song_on_spotify', 'args': {'song': '七里香'}, 'id': '019661af5b6bfd30027c61b795c82271', 'type': 'tool_call'}], usage_metadata={'input_tokens': 232, 'output_tokens': 223, 'total_tokens': 455, 'input_token_details': {}, 'output_token_details': {}})]}),))
    # StateSnapshot(values={'messages': []}, next=('__start__',), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f02019d-d8b8-6963-bfff-34aa14fb6ea5'}}, metadata={'source': 'input', 'writes': {'__start__': {'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={})]}}, 'step': -1, 'parents': {}, 'thread_id': '1'}, created_at='2025-04-23T08:06:31.166596+00:00', parent_config=None, tasks=(PregelTask(id='bd71f7cb-861d-12cb-3101-59505a65c8d9', name='__start__', path=('__pregel_pull', '__start__'), error=None, interrupts=(), state=None, result={'messages': [HumanMessage(content='在任意一个平台播放周杰伦的歌曲《七里香》', additional_kwargs={}, response_metadata={}, id='e3289d01-760b-413f-afc1-f2e74e884fcb')]}),))

# 历史记录中有5个中间状态，已经按时间降序排列，从后往前分别对应：START --> AGENT --> ACTION --> AGENT --> END

# 3. 回放某个状态（从第三步 ACTION 开始按序回放）
to_replay = all_states[-3]
print(f"********************* 从调用 Tools 开始开始重放, 下个状态: {to_replay.next} *********************")
# 要从某个位置重新开始重新执行，我们只需将对应位置的 State 配置信息传递回 Agent
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event["messages"][-1].pretty_print()

    # {'messages': [ToolMessage(content='Successfully played 周杰伦 七里香 on Spotify!', name='play_song_on_spotify', id='e6bb45d6-8e91-495d-8d66-417e1bf958c2', tool_call_id='019661d2814c614a4998b01f093af7a1')]}
    # {'messages': [AIMessage(content='已帮您在Spotify上播放周杰伦的《七里香》。如果需要在Apple Music播放或有其他歌曲需求，请随时告诉我！', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 330, 'prompt_tokens': 317, 'total_tokens': 647, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'Qwen/QwQ-32B', 'system_fingerprint': '', 'id': '019661d2aa2d05bd5268765c8e8c5e98', 'finish_reason': 'stop', 'logprobs': None}, id='run-e109dd58-37ca-4b38-ad3e-a6c17673ff7b-0', usage_metadata={'input_tokens': 317, 'output_tokens': 330, 'total_tokens': 647, 'input_token_details': {}, 'output_token_details': {}})]}

# 4. 更改过去的状态
# 重新执行某个状态时，我们可以通过修改 State 的值来更改过去的状态
# 例如，我们想让 Agent 在执行 ACTION 时，不从 Spotify 播放歌曲，而是从 Apple Music 播放
# 我们可以通过修改 State 的值来更改过去的状态
last_message = to_replay.values["messages"][-1]
print('修改前: ', last_message.tool_calls[0]["name"])
last_message.tool_calls[0]["name"] = "play_song_on_apple"
print('修改后: ', last_message.tool_calls[0]["name"])

branch_config = graph.update_state(
    to_replay.config,
    {"messages": [last_message]},
)

print(f"********************* 修改后进行重放, 下个状态: {to_replay.next} *********************")
for event in graph.stream(None, branch_config, stream_mode="values"):
    event["messages"][-1].pretty_print()

    # ================================== Ai Message ==================================
    # Tool Calls:
    #   play_song_on_apple (019661fae68f6e770a1f6eb7211da14f)
    #  Call ID: 019661fae68f6e770a1f6eb7211da14f
    #   Args:
    #     song: 七里香
    # ================================= Tool Message =================================
    # Name: play_song_on_apple
    # Successfully played 七里香 on Apple Music!
    # ================================== Ai Message ==================================
    # 好的，七里香已经在Apple Music成功播放了！希望您喜欢这首经典歌曲。如果需要在Spotify或其他平台
    # 播放，或者想听周杰伦的其他歌曲，随时告诉我哦～ 😊
    # （另外，如果您有偏好使用的音乐平台，可以告诉我，以后会优先为您调用对应的服务！）
