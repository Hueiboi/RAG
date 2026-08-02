from src.config import settings
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore

def get_retriever(vectorstore: VectorStore, user_id: str) -> BaseRetriever:
    # tạo một retriever từ vectorstore với các tham số tìm kiếm được lấy từ settings
    # tìm kiếm các tài liệu tương tự dựa trên embedding vector
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold", # tìm kiếm dựa trên ngưỡng điểm tương đồng
        search_kwargs={
            "k": settings.top_k,
            "score_threshold": settings.score_threshold,
            "filter": {"user_id": user_id}  # lọc kết quả theo user_id
            }
    )
    
    return retriever