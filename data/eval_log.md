# Eval log — retrieval

Append-only. Mỗi mục là một lần đo, ghi rõ thời điểm và cấu hình,
để so sánh trước/sau và dùng lại khi viết báo cáo.

Metric: `recall@k` = tỉ lệ câu có chunk đúng trong top-k ·
`MRR@k` = trung bình 1/rank · `top1` = tỉ lệ chunk đúng đứng đầu.

---

## 2026-10-27 10:25 SE Asia Standard Time — baseline

- commit: `47dd0f3`
- embedding: `BAAI/bge-m3`
- chunk_size/overlap: `1200` / `200` (đơn vị: ký tự)
- retriever: dense `similarity_score_threshold`, k=`5`, score_threshold=`0.0`
- corpus: **216 chunk** / 12 file (Traffic_in_Vietnam_Overview.pdf, wiki_bien_doi_khi_hau_tai_viet_nam.txt, wiki_dien_toan_dam_may.txt, wiki_doi_moi.txt, wiki_duong_cao_toc_bac_nam_phia_dong.txt, wiki_duong_sat_do_thi_ha_noi.txt, wiki_giao_thong_viet_nam.txt, wiki_ha_noi.txt, wiki_nang_luong_tai_tao_tai_viet_nam.txt, wiki_nha_tran.txt, wiki_postgresql.txt, wiki_tri_tue_nhan_tao.txt); toàn DB 216 chunk

| metric | value |
| --- | --- |
| recall@5 | 0.688 |
| MRR@5 | 0.615 |
| top1 | 0.562 |

| # | query | rank | chunks trả về |
| --- | --- | --- | --- |
| 1 | Phương tiện giao thông phổ biến nhất tại Việt Nam hiện nay là gì? | MISS | 5 |
| 2 | Xu hướng sở hữu phương tiện giao thông cá nhân và công cộng ở Việt Nam đang diễn ra như thế nào? | 3 | 5 |
| 3 | Những nguyên nhân chính nào gây ra tình trạng ùn tắc giao thông vào giờ cao điểm tại các đô thị lớn? | MISS | 5 |
| 4 | Các cơ quan chức năng Việt Nam đã áp dụng những giải pháp nào để giảm thiểu tai nạn giao thông? | MISS | 5 |
| 5 | Việt Nam đang tập trung đầu tư vào những loại hình hạ tầng giao thông nào cho tương lai? | MISS | 5 |
| 6 | Mục tiêu dài hạn của việc nâng cấp hệ thống giao thông thông minh và đường cao tốc là gì? | MISS | 5 |
| 7 | Nhà Trần cai trị nước Đại Việt trong khoảng thời gian nào? | 1 | 5 |
| 8 | Vì sao hiện tượng nhiều thế hệ cùng sống chung trong một ngôi nhà lại phổ biến ở Hà Nội? | 1 | 5 |
| 9 | Tuyến đường cao tốc Bắc – Nam phía Đông bắt đầu và kết thúc ở đâu? | 1 | 5 |
| 10 | Dự án đường cao tốc khởi công ngày 1 tháng 1 năm 2023 đã được thông xe kỹ thuật vào ngày nào? | 1 | 5 |
| 11 | Hệ thống đường sắt đô thị Hà Nội khi hoàn thiện gồm bao nhiêu tuyến và tổng chiều dài bao nhiêu km? | 1 | 5 |
| 12 | Vì sao phần lớn tuyến đường thủy nội địa của Việt Nam chạy theo hướng Đông - Tây? | 1 | 5 |
| 13 | Việt Nam được dự báo sẽ chịu ảnh hưởng của biến đổi khí hậu ở mức độ nào? | 1 | 5 |
| 14 | Thủy điện chiếm bao nhiêu phần trăm tổng công suất điện của Việt Nam tính đến cuối năm 2018? | 2 | 5 |
| 15 | PostgreSQL là loại hệ quản trị cơ sở dữ liệu gì? | 1 | 5 |
| 16 | Trí tuệ nhân tạo được định nghĩa là gì? | 1 | 5 |

---

## 2026-10-27 11:31 SE Asia Standard Time — baseline-v2

- commit: `47dd0f3`
- embedding: `BAAI/bge-m3`
- chunk_size/overlap: `1200` / `200` (đơn vị: ký tự)
- retriever: dense `similarity_score_threshold`, k=`5`, score_threshold=`0.0`
- corpus: **370 chunk** / 12 file (Traffic_in_Vietnam_Overview.pdf, wiki_bien_doi_khi_hau_tai_viet_nam.txt, wiki_dien_toan_dam_may.txt, wiki_doi_moi.txt, wiki_duong_cao_toc_bac_nam_phia_dong.txt, wiki_duong_sat_do_thi_ha_noi.txt, wiki_giao_thong_viet_nam.txt, wiki_ha_noi.txt, wiki_nang_luong_tai_tao_tai_viet_nam.txt, wiki_nha_tran.txt, wiki_postgresql.txt, wiki_tri_tue_nhan_tao.txt); toàn DB 370 chunk

| metric | value |
| --- | --- |
| recall@5 | 0.688 |
| MRR@5 | 0.646 |
| top1 | 0.625 |

| # | query | rank | chunks trả về |
| --- | --- | --- | --- |
| 1 | Phương tiện giao thông phổ biến nhất tại Việt Nam hiện nay là gì? | MISS | 5 |
| 2 | Xu hướng sở hữu phương tiện giao thông cá nhân và công cộng ở Việt Nam đang diễn ra như thế nào? | 3 | 5 |
| 3 | Những nguyên nhân chính nào gây ra tình trạng ùn tắc giao thông vào giờ cao điểm tại các đô thị lớn? | MISS | 5 |
| 4 | Các cơ quan chức năng Việt Nam đã áp dụng những giải pháp nào để giảm thiểu tai nạn giao thông? | MISS | 5 |
| 5 | Việt Nam đang tập trung đầu tư vào những loại hình hạ tầng giao thông nào cho tương lai? | MISS | 5 |
| 6 | Mục tiêu dài hạn của việc nâng cấp hệ thống giao thông thông minh và đường cao tốc là gì? | MISS | 5 |
| 7 | Nhà Trần cai trị nước Đại Việt trong khoảng thời gian nào? | 1 | 5 |
| 8 | Vì sao hiện tượng nhiều thế hệ cùng sống chung trong một ngôi nhà lại phổ biến ở Hà Nội? | 1 | 5 |
| 9 | Tuyến đường cao tốc Bắc – Nam phía Đông bắt đầu và kết thúc ở đâu? | 1 | 5 |
| 10 | Dự án đường cao tốc khởi công ngày 1 tháng 1 năm 2023 đã được thông xe kỹ thuật vào ngày nào? | 1 | 5 |
| 11 | Hệ thống đường sắt đô thị Hà Nội khi hoàn thiện gồm bao nhiêu tuyến và tổng chiều dài bao nhiêu km? | 1 | 5 |
| 12 | Vì sao phần lớn tuyến đường thủy nội địa của Việt Nam chạy theo hướng Đông - Tây? | 1 | 5 |
| 13 | Việt Nam được dự báo sẽ chịu ảnh hưởng của biến đổi khí hậu ở mức độ nào? | 1 | 5 |
| 14 | Thủy điện chiếm bao nhiêu phần trăm tổng công suất điện của Việt Nam tính đến cuối năm 2018? | 1 | 5 |
| 15 | PostgreSQL là loại hệ quản trị cơ sở dữ liệu gì? | 1 | 5 |
| 16 | Trí tuệ nhân tạo được định nghĩa là gì? | 1 | 5 |

