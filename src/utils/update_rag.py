import os.path
import shutil
from docx import Document
from config import load_config
from langchain_core.documents.base import Document as LangDoc
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def split_docx_by_bold(file_path):
    doc = Document(file_path)
    sections = []
    current_section = {'title': None, 'content': []}

    for para in doc.paragraphs:
        is_bold = False
        for run in para.runs:
            if run.bold:
                is_bold = True
                break

        text = para.text.strip()
        if not text:
            continue

        if is_bold:
            if current_section['title'] is not None:
                sections.append(current_section)

            current_section = {
                'title': text,
                'content': []
            }
        else:
            if current_section['title'] is not None:
                current_section['content'].append(text)

    if current_section['title'] is not None:
        sections.append(current_section)

    docs = []
    for section in sections:
        docs.append(LangDoc(
            page_content=f"Название секции: {section['title']}\n\n" + '\n'.join(section['content']),
            metadata={"title": section["title"]}
        ))

    return docs


def create_vectorstore(docs, path=None):
    if path:
        if os.path.exists(path):
            shutil.rmtree(path)

    config = load_config('../../config.yaml')

    embeddings = OpenAIEmbeddings(
        openai_api_key=config['llm']['api_key'],
        base_url=config['llm']['base_url']
    )

    vector_store = Chroma.from_documents(
        collection_name="local-rag",
        documents=docs,
        embedding=embeddings,
        persist_directory=path,
    )

docs = split_docx_by_bold('../../data/готовые схемы.docx')
create_vectorstore(docs=docs, path="../../data/doc_rag")