# Chuẩn của corpus dùng cho eval

> Viết 27/10/2026 sau khi phát hiện 9/12 file trong `data/` bị cắt không đúng:
> 3 file dính cap 50.000 ký tự **kèm marker chèn vào text**, 5 file dính cap
> ~3.000 ký tự, 1 file dừng ở tiêu đề section.
>
> Mục đích: crawl lại một lần, kiểm tra bằng máy, không phải đọc mắt từng file.

## Vì sao nghiêm ngặt

`data/eval_set.json` dùng `context_anchor` là **đoạn văn nguyên văn** trong
nguồn. Anchor khớp được ⟺ text giữ đúng câu chữ. Mọi thứ làm lệch text (viết
lại, tóm tắt, chèn ghi chú) đều làm anchor hỏng và biến một câu hỏi "đúng" thành
MISS vĩnh viễn — đã từng xảy ra với câu #5 bị cắt cụt bằng `...`.

Ngoài ra corpus còn là **kiến thức thật của app**: file bị cắt giữa câu nghĩa là
phần lớn nội dung không tồn tại trong index, và hệ thống vẫn trả lời tự tin.

## Những gì cần chốt trước khi crawl

1. **Nguồn**: giả định là `vi.wikipedia.org`. Nếu phải nguồn khác, nói rõ.
2. **Đúng bài nào** — phải khớp các slug dưới đây, để không phải sửa
   `context_anchor`:

   | File | Bài |
   |---|---|
   | `wiki_nha_tran.txt` | Nhà Trần |
   | `wiki_ha_noi.txt` | Hà Nội |
   | `wiki_giao_thong_viet_nam.txt` | Giao thông Việt Nam |
   | `wiki_duong_cao_toc_bac_nam_phia_dong.txt` | Đường cao tốc Bắc – Nam phía Đông |
   | `wiki_duong_sat_do_thi_ha_noi.txt` | Đường sắt đô thị Hà Nội |
   | `wiki_postgresql.txt` | PostgreSQL |
   | `wiki_bien_doi_khi_hau_tai_viet_nam.txt` | Biến đổi khí hậu ở Việt Nam |
   | `wiki_nang_luong_tai_tao_tai_viet_nam.txt` | Năng lượng tái tạo ở Việt Nam |
   | `wiki_tri_tue_nhan_tao.txt` | Trí tuệ nhân tạo |
   | `wiki_doi_moi.txt` | Đổi Mới |
   | `wiki_dien_toan_dam_may.txt` | Điện toán đám mây |

3. **Giữ hay bỏ `Traffic_in_Vietnam_Overview.pdf`** (1 trang tiếng Anh, 731 ký
   tự). Đề xuất: **giữ** — đây là ca cross-lingual duy nhất và là file PDF duy
   nhất, tức kiểm tra được cả đường extract PDF.
4. **Đổi tên file = phải làm lại anchor**. Giữ nguyên tên cũ.

## Yêu cầu kỹ thuật

### Không được cắt

- Không dùng `exchars`, `exintro`, `exlimit`, không `[:N]`, không "max chars".
- Lấy **toàn bộ bài**, mọi section.
- Nếu vì lý do nào đó một bài quá lớn (> 200.000 ký tự), **báo lại con số**, đừng
  tự cắt.
- Kết thúc file phải ở **cuối câu hoặc cuối section**, không dừng giữa từ, giữa
  câu, hay ngay sau một tiêu đề.

### Không được chèn text của công cụ

Phải loại bỏ hoàn toàn:

- `content has been truncated to stay below … characters`
- `[...]`, `…`, `[N characters omitted]`
- `Retrieved from …`, timestamp crawl, URL nguồn
- liên kết sửa bài `[sửa | sửa mã nguồn]`, chú thích `[1]`, `[2]`
- chân trang điều hướng, hộp thông tin (infobox) dạng bảng, caption ảnh
- mã HTML còn sót (`<p>`, `<div>`, `<br>`, `<table>`, `<a href…>`)

### Định dạng

- UTF-8, **không BOM**. Giữ nguyên dấu tiếng Việt, `%`, `–`, `“ ”`.
- Plain text, mỗi đoạn cách nhau **một dòng trống**.
- Tiêu đề section giữ trên dòng riêng, dạng `== Tên section ==`,
  `=== Tên mục ===` (giúp chunker cắt theo ranh giới ngữ nghĩa).
- Danh sách giữ dạng dòng bắt đầu bằng `- ` hoặc `* `.
- Một file = một bài. Không nối nhiều bài.

### Có thể bỏ

Các section thuần tham khảo, không mang kiến thức: `Tham khảo`, `Chú thích`,
`Liên kết ngoài`, `Xem thêm`. Bỏ được thì tốt, không bỏ cũng không sao — nhưng
đừng bỏ phần nội dung chính.

## Nghiệm thu (bắt buộc chạy trước khi ingest)

```bash
python -m eval.check_corpus
```

Script kiểm tra:

| Check | Bắt được lỗi gì |
|---|---|
| `MARKER[...]` | text công cụ chèn vào |
| `MID-SENTENCE` | dừng giữa câu, giữa từ, hoặc ngay sau `:` |
| `HTML` | thẻ HTML còn sót |
| `cap?` | ≥3 file dừng trong cùng khoảng 10% độ dài → cap cứng |
| `Anchor` | anchor trong eval_set không khớp, hoặc khớp nhiều chunk |

**Điều kiện đạt**: `12/12 file sạch` và `anchor 16/16`.

### Sạch theo script chưa đủ

Script chỉ bắt được cắt **giữa câu**. Một file có thể kết thúc đúng dấu chấm mà
vẫn thiếu nửa bài — ví dụ `wiki_duong_sat_do_thi_ha_noi.txt` (20.096 ký tự) hiện
được coi là `ok` nhưng chưa chắc đã đủ section. Khi crawl lại, đối chiếu thêm:
số section trong file phải bằng số section của bài gốc (nhìn mục lục), và độ dài
file phải tương đương bản `action=raw` của bài đó.


## Sau khi crawl xong

1. `python -m eval.seed_corpus --user-id 9e4f550f-7163-405d-9af0-0a7b441e6315`
2. `python -m eval.run_eval --label baseline-v2 --user-id 9e4f550f-…`
3. So `baseline` (216 chunk, cũ) với `baseline-v2` (corpus mới). **Chỉ so được
   recall giữa hai lần khi corpus giống nhau** — khác corpus là khác đề bài, ghi
   rõ trong log, đừng kết luận "retrieval tốt lên/xuống".
