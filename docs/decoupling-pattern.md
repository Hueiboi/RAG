# Pattern: gom phụ thuộc bên thứ ba về một biên giới

> Áp dụng lần đầu: 25/10/2026 — tách Supabase auth / storage / chat history khỏi
> `dependencies.py`, `ingestion.py`, `api/routes/chat.py`.
> Xem diff: `git log -- src/auth.py src/storage.py src/history.py`

## Vấn đề

Một nhà cung cấp thường bán **nhiều dịch vụ trong một gói** (Supabase = Postgres +
Auth + Storage + PostgREST). Hệ quả: "đổi database" nghe như đổi một biến môi
trường, nhưng thực tế auth, storage và lịch sử chat vẫn nằm nguyên ở đó.

Sự phụ thuộc không nằm ở việc *dùng* dịch vụ — nó nằm ở **số nơi biết về dịch vụ
đó**. Khi provider chết, chi phí sửa tỉ lệ với số nơi đó, không tỉ lệ với số dòng
code.

## Dấu hiệu nhận biết

- Cùng một chuỗi `from x import client` xuất hiện ở nhiều module.
- Module nghiệp vụ phải biết shape response của provider (`d.get("metadata", {}).get("size")`).
- Có ít nhất một chỗ truy cập dữ liệu **qua API của provider** thay vì qua DB —
  loại này dễ bị bỏ sót nhất khi "đổi DB" (xem mục *Cái bẫy* bên dưới).
- Muốn viết test cho module nghiệp vụ thì phải có credential thật.

## Cấu trúc 3 lớp

```
        caller (route / job)
                 │  chỉ biết nghiệp vụ: user_id, file_name
                 ▼
        adapter  src/auth.py · src/storage.py · src/history.py
                 │  biết provider, biết shape, biết cách xử lý lỗi
                 ▼
        client   src/supabase_client.py
                 │  nơi duy nhất tạo kết nối
                 ▼
             provider
```

Quy tắc:

1. **Chỉ adapter được `import` SDK của provider.** `grep` SDK trong `src/` phải
   chỉ ra file adapter + client factory.
2. **Adapter nhận ID nghiệp vụ, không nhận credential.** `storage.download(user_id, file_name)`
   chứ không phải `download(client, path)` — người gọi không thể vô tình dùng
   quyền của user khác.
3. **Adapter trả shape của app, không trả shape của provider.** `list_files()`
   trả `{name, size, created_at}` để route không phụ thuộc vào việc Supabase đổi
   tên field.
4. **Client khởi tạo lazy + cache**, không tạo lúc import. Lợi ích thật: `import`
   module không cần `.env` hợp lệ, nên test và tooling chạy được khi chưa cấu hình.
5. **Fail-closed ở tầng adapter.** `verify_token` trả `None` cho mọi trường hợp
   không chắc chắn, kể cả khi provider trả response không lỗi nhưng `user is None`.
   Tầng gọi tự quyết định HTTP status.

## Kết quả trong repo này

| Trước | Sau |
|---|---|
| 6 file gọi Supabase trực tiếp | 3 adapter + 1 client factory |
| `deps.supabase_admin.storage.from_("documents")...` × 4 | `storage.upload/download/list_files/remove` |
| `create_client()` tạo lúc import | lazy + `lru_cache` |
| `response.user` không kiểm tra `None` | `verify_token` trả `None`, route trả 401 |
| Route tự map field của provider | Adapter trả shape cố định |

## Cái bẫy: dữ liệu đi qua API, không qua DB

Lịch sử chat dùng `supabase_admin.table("chat_messages")` — tức **PostgREST**,
không dùng `DATABASE_URL`. Nếu chỉ đổi `DATABASE_URL` sang Postgres khác:

- pgvector: chuyển được.
- `chat_messages`: **vẫn nằm ở Supabase**, im lặng, không lỗi.

Đây là lý do tồn tại `src/history.py`: khi chuyển DB, chỉ phải sửa một file. Bài
học chung: trước khi nói "đã tách khỏi X", hãy `grep` mọi đường truy cập dữ liệu,
không chỉ grep connection string.

## Cách đổi provider (checklist)

1. Viết adapter mới cùng chữ ký hàm.
2. Đổi import ở đúng file adapter (không đổi caller).
3. Xoá/giữ client factory cũ.
4. `grep` SDK cũ trong `src/` — phải còn 0 hit ngoài adapter.
5. Kiểm tra hành vi lỗi: provider mới có thể trả `None`/rỗng thay vì raise.

## Cái gì vẫn còn phụ thuộc (biết để không tự lừa mình)

- **Frontend vẫn dùng `@supabase/ssr`** để đăng nhập và lấy token. Backend chỉ còn
  verify token ở một hàm, nhưng nếu bỏ Supabase thì vẫn phải sửa 6 file frontend
  (`lib/api.ts`, `proxy.ts`, `auth/callback/route.ts`, 2 trang auth, 2 client).
- **RLS** là tài sản của Postgres/Supabase, không đi theo code. Đổi DB là mất lớp
  bảo vệ tầng hai (code vẫn filter `user_id` ở mọi query, nhưng mất lưới dự phòng).
- Pattern này **không** làm auth an toàn hơn. Nó chỉ làm auth dễ thay hơn. An toàn
  vẫn phụ thuộc vào việc dùng provider đã được kiểm chứng.

## Khi nào KHÔNG nên làm

Khi mới có một caller. Trừu tượng hoá một thứ chưa có nhu cầu thay thế chỉ tạo
thêm một lớp phải đọc. Ở repo này làm được vì đã có 4 lời gọi storage + 1 hàm auth
+ 1 chỗ PostgREST — đủ để thấy biên giới thật, không phải biên giới vẽ trước.
