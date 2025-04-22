from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt


@tool
# Note that because we are generating a ToolMessage for a state update, we
# generally require the ID of the corresponding tool call. We can use
# LangChain's InjectedToolCallId to signal that this argument should not
# be revealed to the model in the tool's schema.
# 这是一个 人机协作验证工具，主要实现：
# 1. 向人类操作员请求验证（姓名+生日信息）
# 2. 根据人类反馈决定是否修正数据
# 3. 通过 ToolMessage 更新系统状态
# 典型应用场景
# 1. 关键数据校验
# 当AI生成姓名、生日等敏感信息时，强制人工复核
# 2. 流程控制
# 人工确认后才能继续后续操作（如订单提交）
# 3. 审计追踪
# 通过 tool_call_id 关联原始请求和人工操作记录
def human_assistance(
    name: str, 
    birthday: str,
    tool_call_id: Annotated[str, InjectedToolCallId] # 通过 InjectedToolCallId 标记为 LangChain 内部使用的调用ID（不会暴露给AI模型）
) -> str:
    """Request assistance from a human."""
    # 调用 interrupt() 中断流程并显示验证请求（假设这是对接人工审核的接口）
    human_response = interrupt(
        {
            "question": "以下信息是否正确吗？",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)