import logging as log
import tempfile as tmp
import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres.vectorstores import PGVector
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import settings
from functools import lru_cache
from langchain_core.documents import Document   
from sqlalchemy import text
from src import storage

# Cải tiến hàm load_documents để chỉ load các file của user_id cụ thể từ supabase storage
# Loader chỉ nạp từ đường dẫn file thay vì bytes -> download từ supabase rồi ghi ra file tạm để có đường dẫn file
def load_documents(user_id: str, file_name: str) -> list[Document]:
    data = storage.download(user_id, file_name)
    suffix = Path(file_name).suffix.lower()
    temp = tmp.NamedTemporaryFile(suffix=suffix, delete=False)
    temp.write(data); temp.close()
    try:
        # TextLoader mặc định đọc theo locale của máy, không phải UTF-8. Trên
        # Windows locale là cp1252 nên file .txt tiếng Việt sẽ ném RuntimeError
        # ngay ở bước decode. Phải chỉ định encoding tường minh.
        loader = {
            ".pdf": PyPDFLoader, 
            ".docx": Docx2txtLoader, 
            ".txt": lambda path: TextLoader(path, encoding="utf-8"),
            }[suffix]
        return loader(temp.name).load()
    except Exception as e:
        log.error("Error loading document %s for user %s: %s", file_name, user_id, e)
        raise 
    finally:
        os.unlink(temp.name)  # Xóa file tạm sau khi sử dụng
        
        
def split_documents(documents: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(  # ghi rõ keyword arguments thay vì positional arguments
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    chunks = text_splitter.split_documents(documents)
    
    log.info("Split %d documents into %d chunks", len(documents), len(chunks))
    
    return chunks

# caching embedding model tránh việc load lại nhiều lần, chỉ load 1 lần và cache lại
# tốt hơn global variable tránh load lại mỗi lần gọi hàm
@lru_cache(maxsize=1) 
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings (
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True}
    )    

def connect_to_pgvector() -> PGVector:
    try:
        embedding_model = get_embeddings()
        vectorstore = PGVector(
            embeddings=embedding_model,      
            collection_name="documents",  # tên collection trong PGVector
            connection=settings.database_url,
            use_jsonb=True
        )
        
        log.info("Connected to PGVector database")
        
    except Exception as e:
        log.error("Error connecting to PGVector: %s", e)
        raise e
        
    return vectorstore 
    

# Hàm được cải tiến để load hoặc build vectorstore cho một user_id cụ thể 
def load_or_build(user_id: str = None, files_to_rebuild: list[str] = None) -> PGVector:
    # Kết nối đến cơ sở dữ liệu PostgreSQL qua supabase
    vectorstore = connect_to_pgvector()

    if not user_id or not files_to_rebuild:
        log.warning("load_or_build cần user_id và files_to_rebuild — không có gì để build")
        return None

    documents = load_documents(user_id, files_to_rebuild[0])
    if not documents:
        log.warning("Không có tài liệu nào — khởi động không có index")
        return None

    chunks = split_documents(documents)
    
    for chunk in chunks: 
        chunk.metadata["user_id"] = user_id  # gắn user_id vào metadata của chunk
        chunk.metadata["file_name"] = files_to_rebuild[0]
    
    delete_user_file_vectors(vectorstore, user_id, files_to_rebuild[0])
    
    vectorstore.add_documents(chunks)
    log.info("Added %d chunks for user %s and file %s to vectorstore", len(chunks), user_id, files_to_rebuild[0])
    
    return vectorstore

# Hàm xóa các vector của một user_id và file_name cụ thể trong PGVector
# Xóa các vector thuộc về user_id và file_name cụ thể.
# Không xóa toàn bộ collection, chỉ xóa dữ liệu của riêng user đó.
def delete_user_file_vectors(vectorstore, user_id: str, file_name: str):
    with vectorstore._engine.connect() as conn:
        statement = text("""
            DELETE FROM langchain_pg_embedding
            WHERE collection_id = (
                SELECT uuid
                FROM langchain_pg_collection
                WHERE name = :coll_name
            )
            AND cmetadata->>'user_id' = :uid
            AND cmetadata->>'file_name' = :fname
        """)

        conn.execute(
            statement,
            {
                "coll_name": "documents",
                "uid": user_id,
                "fname": file_name,
            }
        )
        conn.commit()