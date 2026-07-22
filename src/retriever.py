from src.config import settings
from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever

def get_retriever(vectorstore: FAISS) -> BaseRetriever:
    # tạo một retriever từ vectorstore với các tham số tìm kiếm được lấy từ settings
    # tác dụng của retriever là tìm kiếm các tài liệu tương tự dựa trên embedding vector
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold", # tìm kiếm dựa trên ngưỡng điểm tương đồng
        search_kwargs={"k": settings.top_k, "score_threshold": settings.score_threshold}
    )
    
    return retriever