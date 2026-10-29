# Vì sao không dùng hybrid search (và thay bằng lexical boost)

> Kết luận của một lần đo, không phải định kiến về hybrid search.
>
> Hybrid search (dense + BM25/RRF) là thực hành chuẩn trong retrieval, và nó **có**
> tác dụng trên nhiều hệ thống. Tài liệu này giải thích vì sao nó **không đáng làm**
> trong dự án này: không phải vì ý tưởng sai, mà vì (1) Postgres không cho ta BM25,
> và (2) phần lớn lỗi còn lại của hệ thống không phải lỗi từ vựng.

## TL;DR

- Đo bằng `ts_rank` thật của Postgres: FTS thuần **0.308**, RRF(dense, FTS) **0.615–0.731** — không hơn dense thuần (0.731).
- Con số 0.769 trước đó là BM25 **mô phỏng bằng Python**; nó không phải thứ deploy được. `ts_rank` không có IDF nên yếu hơn hẳn BM25.
- Biến thể thay thế: dense top-20 + xếp hạng theo **token hiếm** + RRF → **0.808**, không mất câu nào, không cần migration.
- 5/7 câu còn MISS của dense là cross-lingual (#1, #3, #4, #5, #6). Không phương pháp từ vựng nào sửa được; đó là việc của embedding/dịch query.

## 1. Cách đo

| Thành phần | Giá trị |
|---|---|
| Corpus | 370 chunk / 12 file (11 wiki tiếng Việt + 1 PDF tiếng Anh 731 ký tự) |
| Bộ eval | 26 câu, chia 5 nhóm: `cross-lingual` 6, `vn-natural` 10, `lookup` 5, `short` 2, `descriptive` 3 |
| Metric | `recall@5` (chính), MRR@5, top1 |
| Nguồn | `python -m eval.run_eval`, chi tiết append trong `data/eval_log.md` |

Cùng một corpus, cùng một bộ câu, chỉ đổi bộ xếp hạng. Đo cả bản **mô phỏng**
(BM25 viết bằng Python, tách token + IDF) và bản **deploy được** (`to_tsvector` /
`ts_rank` của Postgres 17.6).

## 2. Kết quả

### Bản mô phỏng — dễ gây ảo tưởng

| Retriever | recall@5 | Ghi chú |
|---|---|---|
| dense (bge-m3) | 0.731 | baseline |
| BM25 Python | 0.692 | yếu ở câu diễn đạt tự nhiên (#7, #16) |
| RRF(dense, BM25) | **0.769** | +2 câu lookup, −1 câu cross-lingual |

Nhìn bảng này thì hybrid "đáng làm". Nhưng BM25 Python là code của chính mình,
không phải của Postgres.

### Bản deploy được — kết quả ngược lại

| Retriever | recall@5 |
|---|---|
| dense | 0.731 |
| FTS `plainto_tsquery` (AND) | **0.000** |
| FTS `to_tsquery` nối OR | 0.308 |
| FTS OR + bỏ token phổ biến (df > 25%) | 0.346 |
| RRF(dense, FTS OR) | 0.615 |
| RRF(dense, FTS OR đã lọc) | 0.731 |

Không cấu hình nào vượt dense. RRF tốt nhất **bằng** dense nhưng đổi thành phần:
được #20 (`428/QĐ-TTg`) và #22 (`Hòn Khoai`), mất #10 và #15.

## 3. Bốn lý do hybrid thất bại ở đây

### 3.1 `ts_rank` không có IDF

Đây là điểm chết. BM25 dìm từ phổ biến bằng IDF; `ts_rank`/`ts_rank_cd` chỉ dựa
trên tần suất và khoảng cách, **không có IDF**. Hệ quả: query 15 từ tiếng Việt,
chunk chứa "năm", "về", "của" leo lên top.

```sql
-- query #2 (cross-lingual): chunk PDF đúng đứng dense #3,
-- nhưng ts_rank xếp nó ra ngoài top-20 vì query toàn từ phổ biến không trùng khớp
to_tsvector('simple', document) @@ to_tsquery('simple', 'xu | hướng | sở | hữu | ...')
```

### 3.2 `plainto_tsquery` AND toàn bộ từ → 0 hit

Câu hỏi tự nhiên không chunk nào chứa đủ mọi từ ("nào", "ban", "hành"...). AND cho
**0.000 trên toàn bộ 26 câu**. Phải tự nối OR, tức là tự viết lại một nửa BM25.

### 3.3 Postgres/Supabase không có BM25

`pg_available_extensions` chỉ có `unaccent`, `pg_trgm`, `rum` — không có
`pg_search`/ParadeDB. Muốn BM25 thật thì phải tự dựng bảng `term_df`, tính IDF
trong SQL, và ghi lại mọi đường ghi dữ liệu. Ước tính ~300 dòng, lệch khỏi
`langchain_postgres` — vượt xa mức "dễ handle" của dự án.

### 3.4 RRF pha loãng đúng chunk mà ta cần

Chunk được **cả hai** retriever đồng ý thì được cộng điểm hai lần. Chunk
cross-lingual chỉ có dense bầu (BM25 không chung token) nên bị 5 chunk đồng thuận
vượt qua. Đo được: #2 rớt khỏi top-5 ngay cả khi trọng số BM25 chỉ 0.3.

```
w=0.3: idx 163 (dense #1 + bm25 #1) → 0.0213
       idx 272 (chỉ dense #3, PDF tiếng Anh) → 0.0159 → rớt hạng 7
```

Đây là trade-off thật của RRF, không phải tham số tinh chỉnh được: hạ trọng số
không cứu #2 mà vẫn mất #20.

## 4. Thay thế: lexical boost trên dense top-20

Lấy dense top-20, dựng danh sách phụ xếp hạng theo **token hiếm của query**
(df ≤ 2% corpus; ưu tiên token có số/`/`), rồi RRF hai danh sách.

| Biến thể | recall@5 | Câu mất |
|---|---|---|
| dense | 0.731 | #1,3,4,5,6,**20,22** |
| lexical toàn corpus + RRF | 0.808 | #1,3,4,5,6 |
| lexical **trong top-20** + RRF | **0.808** | #1,3,4,5,6 |
| lexical top-20, IDF tính trong 20 ứng viên | 0.731 | #1,3,4,5,6,20 |

Vì sao chọn:

- **Cùng kết quả với bản toàn corpus** ⇒ không phải quét cả bảng mỗi query, chỉ
  dùng 20 chunk đã có từ dense.
- **Không migration**: không thêm cột `tsv`, không GIN index, không backfill, không
  phụ thuộc `unaccent`. Bật/tắt bằng một cờ cấu hình.
- **Không mất câu nào**, khác với RRF dùng FTS thật.
- **Vẫn cần df toàn corpus** (dòng cuối bảng chứng minh: tính IDF trong 20 ứng viên
  là không đủ) — lấy bằng một query `ts_stat` hoặc cache theo user, refresh lúc ingest.
- Về bản chất nó vẫn là hybrid (dense + tín hiệu từ vựng), chỉ khác là tín hiệu từ
  vựng là **khớp token hiếm** thay vì BM25 — đúng thứ cần cho mã quyết định, số
  hiệu, tên riêng.

## 5. Điều hybrid không sửa được

Sau mọi biến thể, các câu MISS luôn là **#1, #3, #4, #5, #6**: query tiếng Việt hỏi
về PDF tiếng Anh 731 ký tự. Nhóm `cross-lingual` đứng nguyên 0.167 ở mọi cấu hình.

Không có IDF, token hiếm hay RRF nào cứu được khi hai bên không chia sẻ token. Muốn
sửa phải đổi bản chất: dịch query trước khi embed, hoặc embedding đa ngữ tốt hơn.
Đó là việc riêng, không được trộn vào commit hybrid — nếu trộn sẽ không biết delta
đến từ đâu.

## 6. Khi nào xem lại quyết định

- Corpus vượt ~5.000 chunk: danh sách lexical dựng trên dense top-20 vẫn ổn, nhưng
  chi phí quét `df` toàn corpus mỗi query bắt đầu đáng kể → lúc đó cache df là bắt buộc,
  không phải tuỳ chọn.
- Có `pg_search`/ParadeDB (BM25 thật trong Postgres) → làm lại phép đo này, đừng
  suy ra từ tài liệu.
- Bộ eval vượt ~100 câu → con số bớt nhiễu, có thể phát hiện delta nhỏ hơn 0.04.

## 7. Tái lập

```bash
python -m eval.check_corpus                      # corpus + anchor hợp lệ
python -m eval.run_eval --label <tên> --user-id <uuid>   # ghi vào data/eval_log.md
```

Các probe dùng `ts_rank`, BM25 Python và RRF nằm ngoài repo (chạy một lần để quyết
định, không phải cấu hình app). Con số trong tài liệu này ứng với:
`recall@5` dense **0.731** · MRR@5 **0.660** · top1 **0.615** trên 370 chunk.
