# RAG Chatbot — Progress Log
 
---

## Trước 30/7/2026: Những gì đã hoàn thành
### **Core RAG Pipeline (Python/FastAPI)**
- [x] `config.py` — pydantic-settings, type-safe config, đọc `.env` tự động
- [x] `ingestion.py` — load PDF/DOCX/TXT, chunking bằng `RecursiveCharacterTextSplitter`, embed bằng `HuggingFaceEmbeddings`
- [x] `retriever.py` — `as_retriever()` với top_k filter
- [x] `llm_service.py` — Groq LLM, prompt template tiếng Việt, rule "chỉ trả lời từ tài liệu"
- [x] `pipeline.py` — LangChain LCEL chain dùng `|` operator
- [x] `chatbot.py` — CLI entry point với argparse (`--rebuild-index`)
### **FastAPI**
- [x] `POST /chat` — nhận câu hỏi, trả lời từ RAG chain
- [x] `POST /upload` — nhận file, lưu lên Supabase Storage, trigger ingest
- [x] CORS middleware cho phép Next.js gọi API
- [x] `lifespan` hook khởi tạo chain 1 lần khi app start
- [x] `dependencies.py` — shared state pattern, tránh circular import
### **Vector Store**
- [x] Ban đầu dùng FAISS local
- [x] Debug FAISS score âm — hiểu nguyên nhân L2 distance vs Inner Product, fix threshold `-0.2` [[Note]](docs/retrieval-scoring.md)
- [x] Migrate sang Supabase pgvector (`langchain-postgres`)
- [x] Dùng Transaction Pooler (port 6543) thay Direct Connection
### **Supabase**
- [x] Auth: email/password + Google OAuth
- [x] Database tables: `profiles`, `documents`, `chat_messages`
- [x] RLS enabled, policy per-user
- [x] pgvector extension enabled
- [x] `langchain_pg_collection` + `langchain_pg_embedding` tables tự tạo
### **Next.js Frontend**
- [x] App Router, TypeScript, Tailwind, shadcn/ui
- [x] Dark mode UI — indigo accent, chat bubble layout
- [x] `lib/api.ts` — typed API utility với `ChatResponse`, `UploadResponse` interfaces
- [x] `lib/supabase/` — browser client + server client tách riêng
- [x] Auth pages: email/password form, Google OAuth button
- [x] `middleware.ts` (proxy) — protect `/chat` route, redirect nếu chưa login
- [x] Auth callback route — handle OAuth code exchange
- [x] JWT token tự động đính kèm vào mọi API request

## 30/7/2026
### Xử lý multi tenancy
- [x] `get_current_user` dependency — verify JWT Supabase
- [x] Multi-tenancy design: 1 collection chung `documents`, phân tách bằng `user_id` metadata
- [x] Filter user_id khi retrieve (quan trọng — hiện tại vẫn thấy data của nhau)
    - Đã bổ sung user_id cho get_retriever để tạo đúng retriever cho user đó
    - Không khởi tạo chain xuyên suốt lifespan -> khởi tạo chain theo từng request (tạm thời cho MVP)
    - Lưu ý sau này nâng cấp redis caching để hướng tới production...

### 15/08/2026
- [x] Supabase Storage thay papers/ local

### 22/08/2026
- [x] GET /documents endpoint — `src/api/routes/chat.py`
- [x] DELETE /documents endpoint — `src/api/routes/chat.py`
- [x] Sidebar hiển thị file đã upload — `rag-ui/components/Sidebar.tsx`
- [x] ConfirmDialog xóa file (UI đẹp) — `rag-ui/components/ConfirmDialog.tsx`
- [x] Delete xóa cả Storage + pgvector vectors — `src/api/routes/chat.py` + `src/ingestion.py`
- [x] Strip <think> tag của Qwen — `src/api/routes/chat.py`
- [x] react-markdown render response đúng — `rag-ui/components/MessageBubble.tsx`
- [x] Điều chỉnh score_threshold cho pgvector (0.0), thay model "qwen/qwen3.8-27b" — `src/config.py`

### 06/09/2026
- [x] Chat history lưu DB (mount/race condition/handle edge case api async) - `rag-ui/app/chat/page.tsx`

### 23/09/2026
- [x] Cài đặt Langsmith Observability

### 08/10/2026
- [x] Tích hợp LangSmith Observability — `@traceable` trên endpoint `POST /api/chat` — `src/api/routes/chat.py`
- [x] Trace gắn tag/metadata theo user qua `chain.with_config()` (không mutate chain đang `lru_cache`) — `src/api/routes/chat.py`
- [x] `load_dotenv()` trước mọi import vì LangSmith chỉ đọc `os.environ`, không đọc `Settings` — `src/main.py`
- [x] Thêm biến `LANGSMITH_*` vào `.env.example` — `.env.example`
- [x] Verify: chain `POST /api/chat` → `RunnablePassthrough` → `ChatPromptTemplate` → `ChatGroq`, tag `user:*` lan xuống các run con (project `personal-rag-chatbot`)

### 25/10/2026
- [x] `eval/run_eval.py` — đo recall@k / MRR@k / top1, append mục có timestamp vào `data/eval_log.md`; `--validate-only` kiểm tra anchor không cần DB — `eval/run_eval.py`
- [x] Tách phụ thuộc Supabase khỏi module nghiệp vụ: `src/supabase_client.py`, `src/auth.py`, `src/storage.py`, `src/history.py`; `dependencies.py` / `ingestion.py` / `api/routes/chat.py` chỉ còn gọi interface (+28/−120)
- [x] `verify_token` fail-closed khi `response.user is None` — `src/auth.py`
- [x] Sửa `UnboundLocalError` trong `load_or_build` khi gọi thiếu tham số — `src/ingestion.py`
- [x] Gom ghi chú kỹ thuật vào `docs/`, gộp `FAISS_SCORE_NOTE.md` vào `docs/retrieval-scoring.md` — `docs/`

### 27/10/2026
#### Note
> OpenCode đã thực hiện đo đạc phân bố điểm số tương đồng (Cosine Similarity Scores) của Top-5 chunks trả về từ PGVector cho tập câu hỏi thử nghiệm.    
- score_threshold là "màng lọc rác", không phải "đòn bẩy hiệu năng": Điểm của các chunk chứa đáp án đúng thực tế rơi vào khoảng **0.48 - 0.50**. Nếu nâng ngưỡng lên **0.55**, hệ thống sẽ chặn nhầm đáp án đúng; còn đặt **0.3** thì toàn bộ kết quả hợp lệ đều đi qua.
- Đổi từ **0.0 -> 0.3** chỉ để chuẩn hóa logic code: Trong code, **0.0** tương đương với không lọc gì (no-op). Sửa thành **0.3** giúp chặn các câu hỏi hoàn toàn vô nghĩa/lạc đề, chứ không làm tăng chỉ số **Recall@5** trên tập dữ liệu hiện tại.
#### Progress