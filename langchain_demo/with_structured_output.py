import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel, Field
from utils.env_util import *
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 定义 Pydantic 模型
class Restaurant(BaseModel):
    name: str = Field(description="餐厅的名称")
    cuisine: str = Field(description="餐厅的菜系")
    location: str = Field(description="餐厅的位置")
    rating: float = Field(description="餐厅的评分，范围 0 - 5")

# 构建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的餐厅推荐助手，请严格按以下要求处理输入文本：\n{format_instructions}"),
    ("human", "{input}")
])

llm = init_chat_model(
    openai_api_key=get_openai_api_key(),
    # model=get_default_model(),
    model='deepseek-ai/DeepSeek-R1',
    base_url=get_openai_base_url(),
    model_provider='openai',
    temperature=0.3,
)

# 创建链
chain = prompt | llm | JsonOutputParser(pydantic_object=Restaurant)  # 转换为 json

input_text = """
推荐1家北京的川菜餐厅
"""
result = chain.invoke({
    "input": input_text,
    "format_instructions": Restaurant.model_json_schema()  # 自动生成格式说明
})

print(result)

# {
#   "name": "四川饭店",
#   "cuisine": "川菜",
#   "location": "北京市西城区西绒线胡同51号",
#   "rating": 4.5
# }