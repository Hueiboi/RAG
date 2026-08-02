from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Llm setting
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    
    # Embedding setting
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    
    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 200
    
    # Paths
    paper_dirs: str = "papers/"
    faiss_index: str = "faiss_index/"
    
    top_k: int = 5  # số lượng kết quả trả về khi truy vấn vectorstore
    score_threshold: float = 0.5  # ngưỡng điểm tương đồng để lọc kết quả
    
    database_url: str
    
    supabase_url: str
    supabase_anon_key: str

    # Cấu hình để sử dụng biến môi trường từ file .env
    model_config = {"env_file": ".env"}
    
settings = Settings()
    