# RAG Chatbot - FastAPI + LangChain

> Ghi chép về project RAG chatbot đầu tay: chạy được CLI lẫn Web API (FastAPI).  
> Document -> embedding (BAAI/bge-m3) -> FAISS index -> Groq LLM trả lời.

---

## Mục lục

- [RAG Chatbot - FastAPI + LangChain](#rag-chatbot---fastapi--langchain)
  - [Mục lục](#mục-lục)
  - [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
  - [Cấu trúc thư mục](#cấu-trúc-thư-mục)
  - [Giải thích code](#giải-thích-code)
    - [src/config.py](#srcconfigpy)
    - [src/ingestion.py](#srcingestionpy)
    - [src/retriever.py](#srcretrieverpy)
    - [src/llm\_service.py](#srcllm_servicepy)
    - [src/pipeline.py](#srcpipelinepy)
    - [src/dependencies.py](#srcdependenciespy)
    - [src/main.py](#srcmainpy)
      - [Lifespan là gì?](#lifespan-là-gì)
    - [src/api/routes/chat.py](#srcapirouteschatpy)
      - [POST /api/chat](#post-apichat)
      - [Dependency Injection (Depends)](#dependency-injection-depends)
      - [POST /api/upload](#post-apiupload)
  - [Cách chạy](#cách-chạy)
    - [CLI Chatbot](#cli-chatbot)
    - [Web API (FastAPI)](#web-api-fastapi)
    - [Test API](#test-api)
  - [Luồng hoạt động](#luồng-hoạt-động)
    - [Lần đầu chạy](#lần-đầu-chạy)
    - [Lần chạy sau](#lần-chạy-sau)
    - [Khi upload file mới](#khi-upload-file-mới)
  - [Swagger UI](#swagger-ui)
  - [Cheatsheet FastAPI](#cheatsheet-fastapi)
  - [Làm lại từ đầu](#làm-lại-từ-đầu)
  - [Troubleshooting](#troubleshooting)
  - [Ghi chú cá nhân](#ghi-chú-cá-nhân)
    - [Mẫu ghi chú nhanh](#mẫu-ghi-chú-nhanh)
    - [Kế hoạch phát triển tiếp](#kế-hoạch-phát-triển-tiếp)

---

## Tổng quan kiến trúc

```
User (CLI / Web API)
    │ câu hỏi
    ▼
create_rag_chain()  (src/pipeline.py)
    │
    ├── Retriever (FAISS) ── tìm context
    ├── Prompt Template   ── context + question
    ├── LLM (Groq)        ── sinh trả lời
    └── Output Parser     ── trích xuất chuỗi
```

**Luồng dữ liệu:**
1. **Ingestion:** Document (.txt/.pdf/.docx) -> chunk -> embedding vector -> FAISS
2. **Retrieval:** Câu hỏi -> embedding -> FAISS tìm chunk gần nhất -> context
3. **Generation:** Prompt(context + question) -> Groq LLM -> trả lời

---

## Cấu trúc thư mục

```
RAG/
├── .env                        # Biến môi trường (GROQ_API_KEY, ...)
├── requirements.txt            # Thư viện Python
├── chatbot.py                  # CLI chatbot
├── README.md                   # File này
├── FAISS_SCORE_NOTE.md         # Ghi chú về FAISS score
│
├── papers/                     # Tài liệu nguồn (.txt, .pdf, .docx)
│   └── Vietnamese_People_Overview.txt
│
├── faiss_index/                # FAISS index (lưu trên đĩa)
│   └── index.faiss
│
└── src/                        # Mã nguồn chính
    ├── config.py               # Cấu hình tập trung
    ├── dependencies.py         # Biến global + dependency injection
    ├── ingestion.py            # Load doc -> chunk -> embedding -> build FAISS
    ├── retriever.py            # Tạo retriever từ FAISS
    ├── llm_service.py          # Khởi tạo LLM (Groq) + prompt template
    ├── pipeline.py             # Kết nối -> RAG chain
    ├── main.py                 # Entrypoint FastAPI (chạy server)
    └── api/
        └── routes/
            └── chat.py         # Endpoint: /api/chat + /api/upload
```

---

## Giải thích code

### src/config.py

```python
class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    chunk_size: int = 1200
    chunk_overlap: int = 200
    paper_dirs: str = "papers/"
    faiss_index: str = "faiss_index/"
    top_k: int = 5
    score_threshold: float = -0.1
    model_config = {"env_file": ".env"}

settings = Settings()
```

**Khái niệm:**
- `pydantic-settings`: Đọc biến môi trường từ `.env` tự động, kiểm tra kiểu dữ liệu
- `BaseSettings`: Class cơ sở - tự động ánh xạ biến `.env` vào thuộc tính
- `settings = Settings()`: Instance singleton dùng chung toàn project

> Ghi chú thêm:


### src/ingestion.py

4 bước ETL:

| Bước | Hàm | Mô tả |
|------|-----|-------|
| 1 | `load_documents()` | Đọc .txt/.pdf/.docx từ `papers/` |
| 2 | `split_documents()` | Chia chunk (1200 ký tự, overlap 200) |
| 3 | `build_vectorstore()` | Embedding -> FAISS index |
| 4 | `load_or_build(rebuild)` | Có index rồi -> load, chưa có -> build |

**Khái niệm:**
- **Chunking:** LLM có giới hạn độ dài đầu vào, phải cắt nhỏ
- **Embedding:** Văn bản -> vector số để máy tính so sánh độ tương đồng ngữ nghĩa
- **FAISS:** Thư viện Facebook tìm vector tương tự siêu nhanh
- **`@lru_cache`:** Cache embedding model - chỉ load 1 lần, tiết kiệm RAM

> Ghi chú thêm:


### src/retriever.py

```python
def get_retriever(vectorstore: FAISS) -> BaseRetriever:
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": settings.top_k, "score_threshold": settings.score_threshold}
    )
    return retriever
```

**Công việc:** Câu hỏi -> embedding -> FAISS tìm `top_k` chunk gần nhất -> context.

> **Về score:** FAISS dùng Inner Product, score càng âm càng tốt. Xem `FAISS_SCORE_NOTE.md` để hiểu rõ.

> Ghi chú thêm:

### src/llm_service.py

```python
def get_llm() -> ChatGroq:
    return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key)

def get_prompt() -> ChatPromptTemplate:
    template = """... NGỮ CẢNH: {context}  CÂU HỎI: {question}  TRẢ LỜI:"""
    return ChatPromptTemplate.from_template(template)
```

**Khái niệm:**
- **Prompt template:** Mẫu câu lệnh có placeholder `{context}`, `{question}` - LangChain tự điền
- **LCEL (LangChain Expression Language):** Cú pháp `|` để xâu chuỗi pipeline

> Ghi chú thêm:


### src/pipeline.py

```python
def create_rag_chain(rebuild=False):
    vectorstore = load_or_build(rebuild)        # 1
    retriever = get_retriever(vectorstore)       # 2
    llm = get_llm()                              # 3
    prompt = get_prompt()                        # 4

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain
```

**Luồng LCEL:**
1. Input: `question` (chuỗi)
2. `RunnablePassthrough()`: Giữ nguyên question
3. `retriever` được gọi với question -> context
4. Ghép `{"context": ..., "question": ...}` -> prompt template
5. Prompt -> LLM -> OutputParser -> chuỗi trả lời

> Ghi chú thêm:


### src/dependencies.py

```python
rag_chain = None

def get_chain():
    return rag_chain
```

**Tại sao có file này?**
- RAG chain được tạo ra khi server **khởi động** (trong lifespan)
- Cần biến global để `main.py` gán giá trị và `chat.py` lấy giá trị
- `get_chain()` là dependency function - FastAPI gọi mỗi khi có request vào `/api/chat`

> Ghi chú thêm:


### src/main.py

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        deps.rag_chain = create_rag_chain(rebuild=False)
        yield
    finally:
        pass

app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")
```

#### Lifespan là gì?

**Vấn đề:** Cần khởi tạo RAG chain khi server start, nhưng nếu để ở global scope sẽ chạy ngay khi import.

**Giải pháp:** `lifespan` - code chạy theo vòng đời server:

```
uvicorn start
  -> lifespan: trước yield  (tạo RAG chain)
  -> Server nhận request      (chat, upload)
  -> uvicorn stop
  -> lifespan: sau yield     (dọn dẹp)
```

**`yield`:**
- **Trước yield:** Chạy 1 lần khi server khởi động
- **Sau yield:** Chạy 1 lần khi server tắt
- **Giữa yield:** Server xử lý request bình thường

> Ghi chú thêm: 


### src/api/routes/chat.py

#### POST /api/chat

```python
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat")
async def chat(req: ChatRequest, chain = Depends(get_chain)):
    answer = chain.invoke(req.question)
    return {"answer": answer}
```

**Các khái niệm:**

| Khái niệm | Giải thích |
|-----------|------------|
| `@router.post("/chat")` | Endpoint POST tại `/chat` (+ prefix `/api` = `/api/chat`) |
| `req: ChatRequest` | FastAPI tự parse JSON body -> Pydantic model |
| `chain = Depends(get_chain)` | Dependency Injection - FastAPI gọi `get_chain()` tự động |
| `ChatRequest(BaseModel)` | Pydantic model - tự validate dữ liệu đầu vào |

#### Dependency Injection (Depends)

**Cách thường làm:**
```python
from src.dependencies import rag_chain
answer = rag_chain.invoke(question)
```

**Cách FastAPI:**
```python
def get_chain():
    return rag_chain

@router.post("/chat")
async def chat(chain = Depends(get_chain)):
    answer = chain.invoke(question)
```

**Lợi ích:**
- Dễ test (mock được dependency)
- Rõ ràng (thấy ngay endpoint cần gì)
- Tái sử dụng (nhiều endpoint chung 1 dependency)
- Tách biệt (khởi tạo riêng, xử lý riêng)

#### POST /api/upload

```python
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    allowed = {".txt", ".pdf", ".docx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="...")

    save_path = Path(settings.paper_dirs) / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    deps.rag_chain = create_rag_chain(rebuild=True)
    return {"message": f"File {file.filename} uploaded successfully."}
```

**Giải thích:**
- `UploadFile = File(...)`: FastAPI nhận file upload, `...` = bắt buộc
- `Path(settings.paper_dirs)`: Đường dẫn thư mục papers
- `shutil.copyfileobj()`: Copy file upload vào ổ cứng
- `create_rag_chain(rebuild=True)`: Load lại doc + rebuild FAISS + gán chain mới

> Ghi chú thêm:
> -


## Cách chạy

### CLI Chatbot
```bash
python chatbot.py
python chatbot.py --rebuild-index    # Nếu thêm file mới
```

### Web API (FastAPI)
```bash
uvicorn src.main:app --reload
# Mở: http://localhost:8000/docs
```

**Giải thích:**
- `uvicorn`: Server ASGI chạy Python async
- `src.main:app`: File `src/main.py`, biến `app`
- `--reload`: Tự restart khi code thay đổi (dev only)

### Test API
```bash
# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Người Việt Nam có đặc điểm gì?"}'

# Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@papers/Vietnamese_People_Overview.txt"
```

---

## Luồng hoạt động

### Lần đầu chạy
```
1. Server start
2. lifespan -> create_rag_chain(rebuild=False)
3. load_or_build() -> không thấy index.faiss -> build mới
4. Load doc -> chunk -> embed -> save FAISS
5. POST /api/chat -> chain.invoke(question) -> trả lời
```

### Lần chạy sau
```
1. Server start
2. lifespan -> create_rag_chain(rebuild=False)
3. load_or_build() -> thấy index.faiss -> load từ đĩa (nhanh)
```

### Khi upload file mới
```
1. POST /api/upload -> lưu file -> create_rag_chain(rebuild=True)
2. load_or_build(rebuild=True) -> bỏ qua index cũ
3. Load TẤT CẢ doc -> chunk -> embed -> save
4. Gán chain mới vào biến global
```

---

## Swagger UI

FastAPI tự sinh Swagger (OpenAPI). Khi server chạy:

1. **`http://localhost:8000/docs`**
2. Thấy 2 endpoint: `POST /api/chat` và `POST /api/upload`
3. "Try it out" -> nhập dữ liệu -> "Execute"

---

## Cheatsheet FastAPI

| Khái niệm | Ý nghĩa |
|-----------|---------|
| `FastAPI()` | Tạo ứng dụng web |
| `@app.get/post/...` | Định nghĩa endpoint |
| `APIRouter()` | Nhóm endpoint theo module |
| `lifespan` | Code chạy khi start/stop server |
| `Depends()` | Dependency Injection |
| `BaseModel` | Pydantic - định nghĩa & validate dữ liệu |
| `UploadFile` | Nhận file upload |
| `Path()` / `Query()` | Tham số URL path / query string |
| `HTTPException` | Trả lỗi HTTP |
| `uvicorn` | Server ASGI |

---

## Làm lại từ đầu

Các bước xây RAG chatbot tương tự:

1. **Cài đặt:** `fastapi`, `uvicorn`, `langchain-community`, `langchain-groq`, `faiss-cpu`, `pydantic-settings`
2. **config.py** - Settings
3. **ingestion.py** - Load doc -> chunk -> embed -> vectorstore
4. **retriever.py** - Retriever từ vectorstore
5. **llm_service.py** - LLM + prompt
6. **pipeline.py** - LCEL chain
7. **dependencies.py** - Global + get_chain()
8. **main.py** - FastAPI + lifespan
9. **chat.py** - Endpoint chat + upload

---

## Troubleshooting

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| "Không tìm thấy thông tin" | FAISS threshold quá cao | Hạ `score_threshold` hoặc dùng `search_type="similarity"` |
| Server không start | Thiếu .env / sai API key | Kiểm tra `GROQ_API_KEY` trong `.env` |
| Upload xong không có kết quả | Chưa rebuild | API tự rebuild; CLI dùng `--rebuild-index` |
| "no module named ..." | Thiếu thư viện | `pip install -r requirements.txt` |

---

## Ghi chú cá nhân

*Phần này để ghi lại những gì học được sau mỗi lần sửa code, thêm tính năng, hoặc debug.*

### Mẫu ghi chú nhanh

```
## YYYY-MM-DD - Tiêu đề

**Vấn đề:**
...

**Giải pháp:**
...

**Bài học:**
...
```

- Ghi chú về NextJS (basic nhưng rewind cho đỡ quên)
    > Client component và Server component khác nhau khi Client là component cho người dùng và **interactive** (VD: nhập liệu, submit) còn Server để hiển thị những nội dung **readonly** (VD: db info, api-key,...)
    
    > Gửi Text thông thường: Dùng JSON.stringify().Gửi File tài liệu (PDF, TXT) cho RAG: KHÔNG dùng stringify vì Internet không chuyển file nhị phân thành chữ được. Phải đóng gói vào đối tượng FormData() rồi gửi thẳng body là formData.

    > Lỗi onclick={function()}: Viết trực tiếp kèm dấu ngoặc () sẽ làm hàm bị thực thi ngay lập tức khi vừa tải trang, gây vòng lặp vô tận (Infinite Loop).Cách sửa: Bọc trong một hàm mũi tên onClick={() => deleteMessage(msg.id)} để biến nó thành một "hộp quà", khi nào click chuột thật mới mở ra chạy.

    > useRef: Là một chiếc hộp dùng để "tóm" và giữ cố định một thẻ HTML thật trên trình duyệt mà không làm trang bị load lại.Cách auto-scroll: Cắm một thẻ <div ref={messagesEndRef} /> trống rỗng ở đáy cùng của khung chat để làm "cột mốc". Mỗi khi có tin nhắn mới, gọi lệnh .scrollIntoView() để ép màn hình tự trượt xuống đúng vị trí cái cột mốc đó.

### Kế hoạch phát triển tiếp

- [ ] Chuyển FAISS -> PostgreSQL pgvector (production)
- [ ] Thêm authentication
- [ ] Streaming response
- [ ] Lịch sử chat (session)
- [ ] ...


# RAG
