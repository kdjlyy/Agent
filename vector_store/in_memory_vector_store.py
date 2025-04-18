import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_util import *

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# Initialize the embeddings
embedding = OpenAIEmbeddings(
    api_key=get_openai_api_key(), 
    base_url=get_openai_base_url(),
    model=get_default_embedding_model(),
)

# Initialize the vector store
vector_store = InMemoryVectorStore(embedding=embedding)

document_1 = Document(
    page_content="""北京市是中华人民共和国的首都，位于华北平原北部，是全国政治、文化、国际交往和科技创新中心。
    作为历史文化名城，北京拥有故宫、长城、颐和园等7项世界文化遗产，展现着古都的厚重底蕴。同时，它也是现代化国际大都市，
    中关村科技园区聚集全球创新资源，金融街、CBD彰显经济活力。天安门广场、人民大会堂等标志性建筑，既承载着国家记忆，也见证着城市的飞速发展。
    北京以多元包容的姿态，融合传统与现代，成为举世瞩目的国际交往枢纽。""",
    metadata={"source": "a", "tag": "1"},
)
document_2 = Document(
    page_content="""香蕉是芭蕉科多年生草本植物的果实，外皮多为黄色，成熟后果肉柔软香甜，富含钾、维生素B6和膳食纤维，是广受欢迎的热带水果。
    其原产于亚洲东南部，现广泛种植于热带、亚热带地区，全球年产量超1亿吨。香蕉既可直接食用，也可制成奶昔、甜品或烘焙食材，还因便于携带、能量丰富，
    成为运动前后的理想补给。中医认为香蕉性寒味甘，有清热润肠、促进消化的功效，但脾胃虚寒者需适量食用。作为全球贸易量最大的水果之一，香蕉在热带农业经济中占据重要地位。""",
    metadata={"source": "b", "tag": "1"},
)
document_3 = Document(
    page_content="""伊曼努尔·康德（1724-1804）是德国古典哲学的奠基人，其思想深刻影响了西方哲学、伦理学和科学认识论。
    他提出“人为自然立法”的哲学命题，在《纯粹理性批判》中探讨人类认知的边界，区分现象与物自体；《实践理性批判》构建了以“道德法则”为核心的伦理体系，强调意志自由与责任；
    《判断力批判》则研究审美与目的论，完善了其哲学大厦。康德主张“人是目的而非手段”，奠定了现代人文主义的重要基础。尽管其理论因抽象性备受争议，但其对理性、道德和美的追问，
    至今仍是哲学研究的重要课题，被誉为“哲学界的哥白尼革命”。""",
    metadata={"source": "c", "tag": "2"},
)
document_4 = Document(
    page_content="""LLM（大语言模型）是基于深度学习的人工智能系统，通过海量文本数据训练，具备理解、生成和推理自然语言的能力。
    其核心技术包括Transformer架构、自监督学习等，代表模型如GPT-4、PaLM等，参数规模可达万亿级。LLM能完成问答、翻译、代码生成、创意写作等复杂任务，
    已渗透到教育、医疗、客服等多个领域，推动人机交互方式的变革。然而，其发展也面临伦理挑战，如信息偏见、生成内容的真实性把控等。
    随着技术迭代，LLM正从单一文本处理向多模态交互演进，成为人工智能领域最具影响力的技术之一，重塑着数字时代的信息生产与传播模式。""",
    metadata={"source": "d", "tag": "2"},
)
document_5 = Document(
    page_content="""鲨鱼是一类古老的软骨鱼类，最早出现于4亿年前，现存约500种，广泛分布于全球海洋。
    其身体呈流线型，皮肤覆盖盾鳞，拥有敏锐的嗅觉和电感应能力，是海洋生态系统中的顶级捕食者。鲨鱼食性多样，从浮游生物到大型海洋哺乳动物均可成为猎物，对维持海洋生物多样性至关重要。
    然而，因鱼翅捕捞、栖息地破坏等因素，多数鲨鱼种群面临生存威胁，约三分之一物种被列为濒危或易危。作为海洋健康的“晴雨表”，保护鲨鱼对于维护海洋生态平衡具有关键意义，
    国际社会已通过多项公约限制商业捕捞。""",
    metadata={"source": "e", "tag": "2"},
)

documents = [document_1, document_2, document_3, document_4, document_5]
# Add documents to the vector store
vector_store.add_documents(documents=documents, ids=["doc1", "doc2", "doc3", "doc4", "doc5"])

query = "香蕉能促进消化"
# 相似性搜索
docs = vector_store.similarity_search(query, k=3, filter=lambda doc: doc.metadata["tag"] == "1")
print(docs)


query2 = "纯粹理性批判是哪位哲学家的作品"
docs2 = vector_store.similarity_search_with_score(query2, k=3)
print(docs2)

# 删除文档
# vector_store.delete(ids=["doc1"])