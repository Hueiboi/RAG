from fastapi import APIRouter, Depends , File, HTTPException, UploadFile
from langsmith import traceable
from pydantic import BaseModel
from src.ingestion import load_or_build, delete_user_file_vectors, connect_to_pgvector
from src.pipeline import get_or_create_rag_chain
from src import storage
from src import history as history_store
from pathlib import Path
import src.dependencies as deps
import logging as log
import re


router = APIRouter()

# Pydantic models cho request và response
class ChatRequest(BaseModel):
    question: str
    
class ChatResponse(BaseModel):
    answer: str

class ChatHistory(BaseModel):
    role: str
    content: str
    
# Hàm loại bỏ phần tư duy
def strip_thinking(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

# Chỉ giữ câu hỏi trong trace, bỏ qua object user của Supabase (rất nặng và không cần thiết).
# FastAPI gọi endpoint bằng keyword nên thường là inputs["req"]; xử lý cả trường hợp
# positional để không rơi vào cảnh báo "dropping inputs".
def _trace_inputs(inputs: dict) -> dict:
    req = inputs.get("req") or (inputs.get("args") or [None])[0]
    return {"question": getattr(req, "question", None)}

# ĐÂY là chỗ cần trace: decorate hàm vào của request (entry point).
# LangSmith sẽ tạo 1 run cha "POST /api/chat", các bước LCEL bên trong
# (retrieve -> prompt -> ChatGroq) tự động nằm dưới run cha này.
# KHÔNG decorate get_llm/get_retriever/get_or_create_rag_chain - đó là code chạy 1 lần lúc
# khởi động (và còn bị lru_cache), trace chúng chỉ gây nhiễu, không phản ánh chất lượng trả lời.
@traceable(
    run_type="chain",
    name="POST /api/chat",
    tags=["rag", "chat-endpoint"],
    process_inputs=_trace_inputs,
)
@router.post("/chat")
async def chat(req: ChatRequest, current_user = Depends(deps.get_current_user)):
    chain = get_or_create_rag_chain(user_id=current_user.id)

    if chain is None:
        return {"answer": "Bạn chưa upload tài liệu nào. Vui lòng upload file trước khi đặt câu hỏi."}
    
    question = req.question
    # with_config gắn tag/metadata cho câu hỏi này để lọc và so sánh được theo user.
    # Nó trả về object MỚI nên không ảnh hưởng chain đang được lru_cache dùng chung.
    answer = chain.with_config(
        run_name="rag_chain",
        tags=[f"user:{current_user.id}"],
        metadata={"user_id": current_user.id},
    ).invoke(question)
    answer = strip_thinking(answer)
    return {"answer": answer}

@router.get("/documents")
async def list_documents(current_user = Depends(deps.get_current_user)):
    return {"documents": storage.list_files(current_user.id)}
    
@router.delete("/documents/{file_name}")
async def delete_document(file_name: str, current_user = Depends(deps.get_current_user)):
    storage.remove(current_user.id, file_name)
    
    vectorstore = connect_to_pgvector()
    delete_user_file_vectors(vectorstore, user_id=current_user.id, file_name=file_name)
    get_or_create_rag_chain.cache_clear()  # clear cache để buộc rebuild lại chain
    
    log.info("Index rebuilt after deletion, new chain: %s", deps.rag_chain)
    
    return {"message": f"File {file_name} deleted successfully."}

@router.post("/upload")
async def upload(file: UploadFile = File(...), current_user = Depends(deps.get_current_user)):
    allowed = {".txt", ".pdf", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt, .pdf, and .docx files are allowed.")
        
    file_content = await file.read()
    file_path = Path(file.filename).name
    
    storage.upload(current_user.id, file_path, file_content)
    
    load_or_build(user_id=current_user.id, files_to_rebuild=[file_path])
    get_or_create_rag_chain.cache_clear()  # clear cache để buộc rebuild lại chain
    
    log.info("Index rebuilt, new chain: %s", deps.rag_chain)
        
    return {"message": f"File {file.filename} uploaded successfully."}

@router.post("/history")
async def save_history(history: ChatHistory, current_user = Depends(deps.get_current_user)):
    history_store.save(current_user.id, history.role, history.content)
    return {"message": "History saved successfully."}

@router.get("/history")
async def get_history_by_id(current_user = Depends(deps.get_current_user)):
    return {"history": history_store.list_for_user(current_user.id)}
    