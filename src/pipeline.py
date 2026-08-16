from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.retriever import get_retriever
from src.llm_service import get_llm, get_prompt
from src.ingestion import load_or_build, connect_to_pgvector
from functools import lru_cache
import logging as log

# Cache the RAG chain -> tránh việc tạo lại chain nhiều lần cho cùng một user_id, chỉ tạo 1 lần và cache lại
# TODO: Consider Redis or other caching mechanisms for production use
@lru_cache(maxsize=100)  
def get_or_create_rag_chain(user_id: str): 
    vectorstore = connect_to_pgvector()
    
    if vectorstore is None:
        log.warning("Không có tài liệu nào — không thể tạo chain")
        return None  # Trả về None để chain không được tạo
    
    retriever = get_retriever(vectorstore, user_id)
    llm = get_llm()
    prompt = get_prompt()
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain