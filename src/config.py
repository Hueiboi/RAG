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

    # LangSmith tracing
    # Phải khai báo ở đây: pydantic-settings mặc định chặn biến lạ trong .env
    # (extra="forbidden"), thiếu khai báo là app sẽ crash lúc khởi động.
    # Tên field tự map từ biến LANGSMITH_TRACING / LANGSMITH_API_KEY / LANGSMITH_PROJECT.
    langsmith_tracing: str = "false"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "personal-rag-chatbot"

    # Cấu hình để sử dụng biến môi trường từ file .env
    model_config = {"env_file": ".env"}
    
settings = Settings()
    