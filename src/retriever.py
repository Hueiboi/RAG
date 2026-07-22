from src.config import settings
from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever

# Model xuất ra vector chuẩn hóa Khoảng cách gốc của cả Cosine và Inner Product đều là từ -1 đến 1 (nhưng thực tế thường chỉ rơi vào khoảng 0 đến 1).
# FAISS nhận vào, lấy dải điểm thực tế từ 0 đến 1 đó đem nhân với -1.
# Kết quả là dải điểm trong FAISS bị lật ngược thành -1 đến 0.
# Đó là lý do vì sao tài liệu càng khớp, điểm số FAISS trả về càng âm nặng (tiến về phía -1, ví dụ -0.71),
# còn tài liệu không liên quan thì điểm sẽ tiến về 0.
def get_retriever(vectorstore: FAISS) -> BaseRetriever:
    # tạo một retriever từ vectorstore với các tham số tìm kiếm được lấy từ settings
    # tác dụng của retriever là tìm kiếm các tài liệu tương tự dựa trên embedding vector
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold", # tìm kiếm dựa trên ngưỡng điểm tương đồng
        search_kwargs={"k": settings.top_k, "score_threshold": settings.score_threshold}
    )
    
    return retriever