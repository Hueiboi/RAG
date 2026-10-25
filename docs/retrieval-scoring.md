# Score và threshold của vector store

> Gộp từ `FAISS_SCORE_NOTE.md` (giai đoạn FAISS, ~tháng 7/2026) và bổ sung phần
> pgvector + cách đo chất lượng retrieval (25/10/2026).
>
> Đọc mục 1 để hiểu vì sao "score" không phải một khái niệm thống nhất giữa các
> store. Đọc mục 3 trước khi tin bất kỳ con số recall nào.

## 1. FAISS: relevance score âm (giai đoạn đầu)

### Triệu chứng

Chatbot trả "Tôi không tìm thấy thông tin này trong tài liệu" dù tài liệu có đủ
thông tin.

### Chuỗi nguyên nhân

```
Model embedding (all-MiniLM-L6-v2)
→ output vector đã normalize (độ dài = 1)
→ Inner Product ≈ Cosine Similarity (vì |A| = |B| = 1)

FAISS
→ chỉ có 1 thuật toán: tìm MIN distance
→ Inner Product: gần nhau → score +1 (cần MAX) — không khớp
→ FAISS nhân -1 để đảo chiều: gần nhau → score -1 (tìm MIN) ✓

LangChain nhận score âm từ FAISS
→ convert sang relevance score bằng công thức L2: score = 1 - (L2/2)
→ công thức này sai cho Inner Product
→ relevance score bị lệch, có thể âm

Threshold mặc định 0.5
→ score thực tế ~ -0.71 → bị lọc hết → LLM không có context
```

### Vì sao `distance_strategy=COSINE` không cứu được

LangChain FAISS có bug: set `COSINE` thì index type đúng (`IndexFlatIP`) nhưng
công thức tính relevance score vẫn dùng L2. Score vẫn lệch.

### Cách tính thực tế

```
FAISS Inner Product score = -0.71
LangChain convert: score / 2 + 0.5 = 0.145

Threshold 0.5  → 0.145 < 0.5  → bị lọc
Threshold -0.2 → 0.145 > -0.2 → pass
```

### Fix đã dùng

Hạ threshold xuống `-0.2` (tạm), sau đó chuyển sang pgvector — nơi score là cosine
chuẩn trong [0, 1] và threshold dùng được bình thường.

### Bài học

- "Score" là quy ước của từng store, không phải đại lượng vật lý. Đổi store là đổi
  cả ý nghĩa của threshold.
- Phải kiểm tra metric của embedding model có khớp metric của store không.
- Đừng để lỗi bị nuốt trong `except`.

## 2. pgvector: threshold bằng 0 là no-op

`src/retriever.py` dùng:

```python
search_type="similarity_score_threshold"
search_kwargs={"k": 5, "score_threshold": 0.0, "filter": {"user_id": user_id}}
```

`langchain_postgres` trả relevance = `1 - cosine_distance`, nên giá trị nằm trong
khoảng [0, 1] (với vector đã normalize). Điều kiện `score >= 0.0` chỉ loại chunk
có similarity **âm** — gần như không tồn tại với cosine trên văn bản.

Kết luận: **threshold hiện tại không lọc gì cả.** Nó là trang trí. `src/README.md`
ghi `SCORE_THRESHOLD=0.5` trong khi code là `0.0` — chỗ lệch này là dấu hiệu của
cùng một hiểu nhầm.

Giá trị hợp lý cho cosine + `bge-m3`: **0.3–0.4**. Đừng đặt 0.7–0.8 rồi tự hỏi vì
sao không bao giờ có context.

## 3. Đo chất lượng retrieval cho đúng

### Corpus phải lớn hơn k rất nhiều

Với `k=5`, nếu corpus chỉ có 1 chunk thì mọi query đều lấy được chunk đúng →
recall@5 = 1.000. Con số đó **không** nói retrieval tốt, nó nói corpus bé.

Quy tắc thực dụng: corpus nên có **≥ 20×k** chunk mới bắt đầu phân biệt được
(100 chunk với k=5 thì đoán mò đã được 5%).

### Chunk count đến từ `chunk_size`, không phải `chunk_overlap`

```
số chunk ≈ (độ dài văn bản - overlap) / (chunk_size - overlap)
```

Giảm `chunk_overlap` làm **bước nhảy tăng** → số chunk **giảm**, không tăng.
Ví dụ 4291 ký tự, `chunk_size=1200`:

| overlap | bước nhảy | số chunk xấp xỉ |
|---|---|---|
| 200 | 1000 | 5 |
| 50 | 1150 | 4 |

Muốn nhiều chunk hơn từ cùng văn bản thì phải giảm `chunk_size`. Nhưng hạ
`chunk_size` để "làm eval có ý nghĩa" là **gian lận chính phép đo**: bạn đang đổi
hệ thống rồi so với chính nó. Cách đúng là thêm tài liệu thật.

### Bộ eval

- Mỗi câu: `{id, query, ground_truth, context_anchor}`. `context_anchor` là **đoạn
  văn bản nguyên văn** trong nguồn — dùng để xác định chunk đúng mà không cần gán
  nhãn thủ công.
- Anchor phải khớp **tuyệt đối** sau khi chuẩn hoá khoảng trắng. Anchor bị cắt cụt
  bằng `...` sẽ không bao giờ khớp và luôn tính là MISS — lỗi này đã từng xảy ra
  với câu #5 của `data/eval_set.json`.
- Metric: `recall@k` (có chunk đúng trong top-k không), `MRR@k` (chunk đúng đứng
  thứ mấy), `top1`.
- Dùng `python -m eval.run_eval --validate-only` để kiểm tra anchor trước khi đo.
  Kết quả append vào `data/eval_log.md` kèm timestamp + commit hash.
