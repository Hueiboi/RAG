from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Llm setting
    groq_api_key: str
    groq_model: str = "qwen/qwen3.6-27b"
    
    # Embedding setting
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    
    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 200
    
    top_k: int = 5  # số lượng kết quả trả về khi truy vấn vectorstore
    score_threshold: float = 0.0  # ngưỡng điểm tương đồng để lọc kết quả
    
    database_url: str
    
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # Cấu hình để sử dụng biến môi trường từ file .env
    model_config = {"env_file": ".env"}
    
settings = Settings()
    