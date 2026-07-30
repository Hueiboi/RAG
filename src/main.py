from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.pipeline import create_rag_chain
import src.dependencies as deps
from src.api.routes.chat import router 
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# Lifespan và asynccontextmanager để khởi tạo rag_chain khi ứng dụng FastAPI khởi động và dọn dẹp khi ứng dụng tắt
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        deps.rag_chain = create_rag_chain(rebuild=False)
        yield
    finally:
        pass  # Cleanup code if needed

app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://172.23.32.1:3000"],
    allow_headers=["*"],
    allow_methods=["*"]
)
