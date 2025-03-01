from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json

load_dotenv()

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

llm = ChatOpenAI(
  openai_api_key=os.getenv("API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name=os.getenv("MODEL_NAME")
)

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.load_local("data/vectordb", embeddings_model, allow_dangerous_deserialization=True)


def search(query, vectordb=vectordb, k=20):
    # Perform similarity search
    results = vectordb.similarity_search_with_score(query, k=k)
    return results
    

def search_filter(results_with_score=None, vectordb=vectordb, week_filter=None, section_filter=None):
    documents = results_with_score or [(doc, None) for doc in vectordb.docstore._dict.values()]
    return [
        (doc, score) for doc, score in documents
        if (week_filter is None or doc.metadata.get("week") == week_filter)
        and (section_filter is None or doc.metadata.get("section") == section_filter)
    ]

def get_content_by_week(week: int, vectordb=vectordb):
    docs = search_filter(week_filter=week, vectordb=vectordb)
    result = ""
    line = "=" * 50

    for doc, score in docs:
        title = f"\nWEEK: {doc.metadata['week']}; SECTION: {doc.metadata['section']}\n\n"
        content = doc.page_content

        result += "\n" + line + title + re.sub(r'([.!?])\s*', r'\1\n', content) + line

    return result


def get_llm_response(query):
    prompt = PromptTemplate(
                template=config.get("template"), 
                input_variables=config.get("input_variables")
            )
    llm_chain = prompt | llm

    output = []
    for chunk in llm_chain.stream(query):
        print(chunk.content, end="", flush=True)
        output.append(chunk.content)
    final_output = "".join(output)


if __name__ == "__main__":
    get_llm_response({
        "question": "what I need to do", 
        "context": get_content_by_week(10)
    })

