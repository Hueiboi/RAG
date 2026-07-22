# Ghi chú: FAISS Score & Distance Metrics

## Vấn đề gặp phải

Chatbot trả về "Tôi không tìm thấy thông tin này trong tài liệu" dù document có đủ thông tin.
Nguyên nhân: relevance score âm bị lọc bởi `similarity_score_threshold`.

---

## Chuỗi nguyên nhân

```
Model embedding (all-MiniLM-L6-v2)
→ output vector đã normalize (độ dài = 1)
→ Inner Product ≈ Cosine Similarity (vì |A| = |B| = 1)

FAISS
→ chỉ có 1 thuật toán: tìm MIN distance
→ Inner Product: gần nhau → score +1 (tìm MAX) — không khớp
→ FAISS nhân -1 để đảo chiều: gần nhau → score -1 (tìm MIN) ✓

LangChain nhận score âm từ FAISS
→ convert sang relevance score bằng công thức L2: score = 1 - (L2/2)
→ công thức này không đúng cho Inner Product
→ relevance score bị lệch, có thể âm

Threshold mặc định = 0.5
→ score thực tế ~ -0.71 → bị lọc hết → LLM không có context
```

---

## Tại sao `distance_strategy=COSINE` không fix được?

LangChain FAISS có bug: khi set `COSINE` thì index type đúng (`IndexFlatIP`) nhưng công thức tính relevance score vẫn dùng L2 — nên score vẫn lệch.

---

## Cách tính relevance score thực tế

```
FAISS Inner Product score = -0.71
LangChain convert: score / 2 + 0.5 = -0.71/2 + 0.5 = 0.145

Threshold 0.5 → 0.145 < 0.5 → bị lọc
Threshold -0.2 → 0.145 > -0.2 → pass ✓
```

---

## Fix tạm thời

**Cách 1** — Hạ threshold trong `config.py`:
```python
similarity_threshold: float = -0.2
```

**Cách 2** — Bỏ threshold, dùng top_k đơn giản trong `retriever.py`:
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": settings.top_k}
)
```

Cách 2 sạch hơn — FAISS vẫn tìm đúng chunk liên quan nhất, score chỉ là số để filter không ảnh hưởng ranking.

---

## Fix thật sự (sau này)

Swap FAISS → **Supabase pgvector**: handle cosine chuẩn, score trả về đúng 0-1, dùng threshold bình thường.

---

## Bài học

- FAISS phù hợp để học và prototype, không phải production multi-user
- Khi chọn vector store phải kiểm tra metric của embedding model khớp với metric của DB
- `traceback.print_exc()` là tool debug quan trọng khi lỗi bị nuốt trong `except`
