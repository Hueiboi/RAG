from fastapi import APIRouter, Depends , File, HTTPException, UploadFile
from pydantic import BaseModel
from src.config import settings
from src.ingestion import load_or_build
from src.pipeline import get_or_create_rag_chain
from pathlib import Path
import src.dependencies as deps
import shutil
import logging as log

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    
class ChatResponse(BaseModel):
    answer: str

@router.post("/chat")
async def chat(req: ChatRequest, current_user = Depends(deps.get_current_user)):
    chain = get_or_create_rag_chain(user_id=current_user.id)

    if chain is None:
        return {"answer": "Bạn chưa upload tài liệu nào. Vui lòng upload file trước khi đặt câu hỏi."}
    
    question = req.question
    answer = chain.invoke(question)
    return {"answer": answer}

@router.post("/upload")
async def upload(file: UploadFile = File(...), current_user = Depends(deps.get_current_user)):
    allowed = {".txt", ".pdf", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt, .pdf, and .docx files are allowed.")
    
    save_path = Path(settings.paper_dirs) / file.filename 
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f) 
        
    log.info("File saved to %s, rebuilding index...", save_path)
    
    load_or_build(user_id=current_user.id, files_to_rebuild=[file.filename])
    get_or_create_rag_chain.cache_clear()  # Clear the cache to force rebuilding the chain
    
    log.info("Index rebuilt, new chain: %s", deps.rag_chain)
        
    return {"message": f"File {file.filename} uploaded successfully."}