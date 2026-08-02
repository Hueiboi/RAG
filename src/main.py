from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import src.dependencies as deps
from src.api.routes.chat import router 
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# Lifespan và asynccontextmanager to manage startup and shutdown events
async def lifespan(app: FastAPI):
    try:
        logging.info("RAG ready to serve")
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
