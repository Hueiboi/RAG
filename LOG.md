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
- [x] `POST /upload` — nhận file, lưu vào papers/, trigger ingest
- [x] CORS middleware cho phép Next.js gọi API
- [x] `lifespan` hook khởi tạo chain 1 lần khi app start
- [x] `dependencies.py` — shared state pattern, tránh circular import
### **Vector Store**
- [x] Ban đầu dùng FAISS local
- [x] Debug FAISS score âm — hiểu nguyên nhân L2 distance vs Inner Product, fix threshold `-0.2` [[Note]](FAISS_SCORE_NOTE.md)
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
- [ ] Supabase Storage thay papers/ local
- [ ] Chat history lưu DB