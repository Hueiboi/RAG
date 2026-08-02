import logging as log
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


def load_documents(paper_dirs: str) -> list[Document]: # -> là return type annotation, chỉ định kiểu dữ liệu của giá trị trả về
    if not Path(paper_dirs).exists():
        raise FileNotFoundError(f"Directory {paper_dirs} does not exist.")
        
    log.info("Loading documents from %s", paper_dirs)
    try: 
        docs = []

        loaders = [
            DirectoryLoader(paper_dirs, glob="**/*.docx", loader_cls=Docx2txtLoader),
            DirectoryLoader(paper_dirs, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(paper_dirs, glob="**/*.pdf", loader_cls=PyPDFLoader),
        ]

        for loader in loaders: 
            docs.extend(loader.load())
        
        log.info("Loaded %d documents from %s", len(docs), paper_dirs)
            
        return docs
        
    except Exception as e:
        log.error("Error loading documents: %s", e)
        raise e

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
    
# def build_vectorstore(chunks: list[Document]) -> FAISS:
#     try: 
#         embedding_model = get_embeddings()
#         faiss_path = Path(settings.faiss_index)
#         faiss_path.mkdir(parents=True, exist_ok=True)  # tự động tạo thư mục nếu chưa tồn tại
        
#         vectorstore = FAISS.from_documents(
#             documents=chunks,
#             embedding=embedding_model,
#             distance_strategy=DistanceStrategy.COSINE
#         )
    
#         vectorstore.save_local(folder_path=str(faiss_path))
        
#         log.info("Vectorstore built and saved to %s", faiss_path)
        
#         return vectorstore
    
#     except Exception as e:
#         log.error("Error building vectorstore: %s", e)
#         raise e

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
    
# def load_or_build(rebuild: bool = False) -> FAISS:
#     # kiểm tra xem có tồn tại thư mục faiss_index hay không
#     # nếu tồn tại thì load vectorstore từ thư mục đó
#     faiss_file = Path(settings.faiss_index) / "index.faiss"

#     if not rebuild and faiss_file.exists(): 
#         vectorstore = FAISS.load_local(
#             folder_path=str(Path(settings.faiss_index)), 
#             embeddings=get_embeddings(),
#             distance_strategy=DistanceStrategy.COSINE,
#             allow_dangerous_deserialization=True
#         )
#         log.info("Loaded existing vectorstore from %s", settings.faiss_index)
#     # nếu không tồn tại thì build vectorstore mới
#     else:
#         documents = load_documents(settings.paper_dirs)
#         if not documents:
#             log.warning("Không có tài liệu nào — khởi động không có index")
#             return None
        
#         chunks = split_documents(documents)
#         vectorstore = build_vectorstore(chunks)
#         log.info("Built new vectorstore and saved to %s", settings.faiss_index) 
    
#     return vectorstore

# Hàm được cải tiến để load hoặc build vectorstore cho một user_id cụ thể 
def load_or_build(user_id: str = None, files_to_rebuild: list[str] = None) -> PGVector:
    # Kết nối đến cơ sở dữ liệu PostgreSQL qua supabase
    vectorstore = connect_to_pgvector()
    
    if user_id and files_to_rebuild:
        documents = load_documents(settings.paper_dirs)
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
def delete_user_file_vectors(vectorstore, user_id: str, file_name: str):
    """
    Xóa các vector thuộc về user_id và file_name cụ thể.
    Không xóa toàn bộ collection, chỉ xóa dữ liệu của riêng user đó.
    """
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