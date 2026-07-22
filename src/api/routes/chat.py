from fastapi import APIRouter, Depends , File, HTTPException, UploadFile
from pydantic import BaseModel
from src.dependencies import get_chain
from src.config import settings
from src.pipeline import create_rag_chain
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
async def chat(req: ChatRequest, chain = Depends(get_chain)):
    question = req.question
    answer = chain.invoke(question)
    return {"answer": answer}

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    allowed = {".txt", ".pdf", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt, .pdf, and .docx files are allowed.")
    
    save_path = Path(settings.paper_dirs) / file.filename 
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f) 
        
    log.info("File saved to %s, rebuilding index...", save_path)
    deps.rag_chain = create_rag_chain(rebuild=True)
    log.info("Index rebuilt, new chain: %s", deps.rag_chain)
        
    return {"message": f"File {file.filename} uploaded successfully."}