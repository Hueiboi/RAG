from fastapi import APIRouter, Depends , File, HTTPException, UploadFile
from pydantic import BaseModel
from src.ingestion import load_or_build, delete_user_file_vectors, connect_to_pgvector
from src.pipeline import get_or_create_rag_chain
from pathlib import Path
import src.dependencies as deps
import logging as log
import re


router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    
class ChatResponse(BaseModel):
    answer: str
    
def strip_thinking(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

@router.post("/chat")
async def chat(req: ChatRequest, current_user = Depends(deps.get_current_user)):
    chain = get_or_create_rag_chain(user_id=current_user.id)

    if chain is None:
        return {"answer": "Bạn chưa upload tài liệu nào. Vui lòng upload file trước khi đặt câu hỏi."}
    
    question = req.question
    answer = chain.invoke(req.question)
    answer = strip_thinking(answer)
    return {"answer": answer}

@router.get("/documents")
async def list_documents(current_user = Depends(deps.get_current_user)):
    documents = deps.supabase_admin.storage.from_("documents").list(path=f"{current_user.id}")
    return {"documents": [
            {
                "name": d["name"],
                "size": d.get("metadata", {}).get("size"),
                "created_at": d.get("created_at")
            }
            for d in documents
            if d.get("name") and not d["name"].endswith("/")  # filter folder
        ]}
    
@router.delete("/documents/{file_name}")
async def delete_document(file_name: str, current_user = Depends(deps.get_current_user)):
    deps.supabase_admin.storage.from_("documents").remove(paths=[f"{current_user.id}/{file_name}"])
    
    vectorstore = connect_to_pgvector()
    delete_user_file_vectors(vectorstore, user_id=current_user.id, file_name=file_name)
    get_or_create_rag_chain.cache_clear()  # Clear the cache to force rebuilding the chain
    
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
    
    deps.supabase_admin.storage.from_("documents").upload(
        path=f"{current_user.id}/{file_path}",
        file=file_content,
        file_options={"upsert": "true"}
    )
    
    load_or_build(user_id=current_user.id, files_to_rebuild=[file_path])
    get_or_create_rag_chain.cache_clear()  # Clear the cache to force rebuilding the chain
    
    log.info("Index rebuilt, new chain: %s", deps.rag_chain)
        
    return {"message": f"File {file.filename} uploaded successfully."}