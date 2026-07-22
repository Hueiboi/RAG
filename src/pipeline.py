from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.retriever import get_retriever
from src.llm_service import get_llm, get_prompt
from src.ingestion import load_or_build

def create_rag_chain(rebuild=False): 
    vectorstore = load_or_build(rebuild=rebuild) # Nhớ truyền rebuild để load_or_build để rebuild index khi upload file mới
    retriever = get_retriever(vectorstore)
    llm = get_llm()
    prompt = get_prompt()
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain