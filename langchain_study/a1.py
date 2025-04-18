import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *
from langchain.chat_models import init_chat_model



model = init_chat_model(
    openai_api_key=get_openai_api_key(),
    model=get_default_model(),
    base_url=get_openai_base_url(),
    model_provider='openai',
)

print(model.invoke("北京到上海的距离"))