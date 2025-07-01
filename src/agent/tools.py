from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_tavily import TavilySearch
from src.utils.config import load_config
import os

config = load_config('../config.yaml')

embeddings = OpenAIEmbeddings(
    openai_api_key=config['llm']['api_key'],
    base_url=config['llm']['base_url']
)

vector_store = Chroma(
    collection_name="local-rag",
    embedding_function=embeddings,
    persist_directory=os.path.abspath("../data/doc_rag")
)

retriever = vector_store.as_retriever()

rag_tool = create_retriever_tool(
    retriever,
    "retrieve_nutrition_hints",
    "Возвращает советы по нутрциологии"
)

search_tool = TavilySearch(
    tavily_api_key=config['app']['tavily_api_key'],
    max_results=3,
    topic="general"
)