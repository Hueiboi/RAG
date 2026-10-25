# Ghi chú kỹ thuật

Các note dài, giữ lại để đọc sau — khác với `PROGRESS.md` (nhật ký việc đã làm)
và `LOG.md` (nhật ký theo ngày).

| File | Nội dung |
|---|---|
| [decoupling-pattern.md](decoupling-pattern.md) | Pattern gom phụ thuộc bên thứ ba (Supabase auth/storage, provider...) về một biên giới. Đọc trước khi thêm bất kỳ dịch vụ ngoài nào |
| [retrieval-scoring.md](retrieval-scoring.md) | Score và threshold qua các đời vector store: FAISS (bug L2 vs Inner Product) → pgvector (`score_threshold=0.0` là no-op). Kèm cách đo chất lượng retrieval đúng |

## Quy ước

- Mỗi file là **một chủ đề**, không phải một ngày. Nhật ký theo thời gian nằm ở
  `PROGRESS.md` / `LOG.md` / `data/eval_log.md`.
- Ghi cả **cái đã sai và tại sao sai**, không chỉ cái đã đúng. Lý do: 6 tháng sau
  bạn sẽ nhớ "đã sửa" nhưng không nhớ "đã thử gì và loại vì sao" — và sẽ thử lại
  đúng cái vừa loại.
- Khi một note hết đúng (ví dụ đổi provider), sửa tại chỗ và ghi ngày, đừng xoá.
