import operator
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from langgraph_utils.common_util import gen_mermaid
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated
from langgraph.types import Send
from pydantic import BaseModel, Field

# 定义 Prompt
subjects_prompt = """后面的对话都使用中文来回答，随机生成4个与 {topic} 相关的关键字，注意只要4个，不要多也不要少，不要重复，生成后你需要自己检查结果是否正确。"""
joke_prompt = """生成一条关于 {subject} 的笑话，使用中文，只返回一行文字，不要返回多行。不要使用\\n等特殊字符，最后你需要检查结果是否满足要求"""
best_joke_prompt = """下面是4行是4个关于 {topic} 的笑话，从前到后ID分别是0、1、2、3，选择其中一个并返回其ID，不要多余的分析或描述，最终结果只要返回一个纯数字。
{jokes}"""

class Subjects(BaseModel):
    subjects: list[str]

class Joke(BaseModel):
    joke: str

class BestJoke(BaseModel):
    id: int = Field(description="序号，int类型，如：1", ge=0)

model = ChatOpenAI(
    openai_api_key=get_openai_api_key(),
    # model_name=get_default_model(),
    model_name="THUDM/GLM-Z1-32B-0414",
    base_url=get_openai_base_url(),
    temperature=0.0,
)

class OverallState(TypedDict):
    topic: str
    subjects: Annotated[list, operator.add]
    jokes: Annotated[list, operator.add]
    best_selected_joke: str


# 笑话的 subject
class JokeState(TypedDict):
    subject: str

# 通过一个 topic 生成多个 subject
def generate_topics(state: OverallState):
    prompt = subjects_prompt.format(topic=state["topic"])
    print(f'👨 {prompt}')
    response = model.with_structured_output(Subjects).invoke(prompt)
    print(f"⚙️生成主题：{response.subjects}")
    return {"subjects": response.subjects}

def continue_to_jokes(state: OverallState):
    """
        返回一个 `Send` 对象列表
        每个 `Send` 对象由图中节点的名称组成
        以及发送到该节点的状态

        这里是把所有生成的 subject 都发送给 `generate_joke` 生成对应主题的笑话
    """
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

# 生成一条笑话
def generate_joke(joke: JokeState) -> OverallState:
    subject = joke["subject"]
    prompt = joke_prompt.format(subject=subject)
    response = model.with_structured_output(Joke).invoke(prompt)
    print(f"⚙️生成[{subject}]笑话：{response.joke}")
    return {"jokes": [response.joke]}

def best_joke(state: OverallState) -> OverallState:
    """
        从多个笑话中找出1个最好的
    """
    jokes = "\n".join(state["jokes"])
    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)

    print("=" * 80)
    print(f'👨 {prompt}')
    print("=" * 80)

    response = model.with_structured_output(BestJoke).invoke(prompt)
    print(f"⚙️选择出了最好的笑话：{response}")
    return {"best_selected_joke": state["jokes"][response.id]}


graph = StateGraph(OverallState)
graph.add_node("generate_topics", generate_topics)
graph.add_node("generate_joke", generate_joke)
graph.add_node("best_joke", best_joke)
graph.add_edge(START, "generate_topics")
graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
graph.add_edge("generate_joke", "best_joke")
graph.add_edge("best_joke", END)
app = graph.compile()

# gen_mermaid(app, "map_reduce.mmd")

for s in app.stream({"topic": "动物"}):
    print(s)