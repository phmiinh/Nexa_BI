Dưới đây là prompt tối ưu để gửi cho Codex:

---

## PROMPT CHO CODEX

**Ngữ cảnh:**
Bạn là sinh viên năm cuối ngành Hệ thống Thông tin / Công nghệ Thông tin, vừa hoàn thành dự án capstone môn Business Intelligence. Dự án tên **SocialLens BI** — một hệ thống BI phân tích mạng xã hội cho ngành F&B tại Việt Nam, tập trung vào Highlands Coffee và các đối thủ cạnh tranh trên YouTube.

Hãy viết báo cáo cuối kỳ hoàn chỉnh bằng **tiếng Việt**, thể hiện tư duy của một sinh viên xuất sắc: hiểu sâu lý thuyết, kết nối chặt với thực tiễn dự án, lập luận mạch lạc, không dùng văn phong AI (không liệt kê máy móc, không câu mở đầu sáo rỗng, không kết luận chung chung).

---

**Thông tin dự án cần nắm:**

*Phạm vi:*
- Ngành: F&B. Thương hiệu chính: Highlands Coffee Vietnam.
- Đối thủ: Trung Nguyen Legend, Phuc Long, Cong Caphe, Cheese Coffee, KOI Thé, Gong Cha, Starbucks Vietnam.
- Nền tảng: YouTube only (quyết định thu hẹp có chủ đích — Facebook bị loại vì rủi ro App Review API).
- Nguồn sự thật: PostgreSQL warehouse schema `social_dw`.

*Kiến trúc kỹ thuật:*
- ETL: Python pipeline → YouTube Data API v3 → raw JSONL → normalize → sentiment → quality gate → PostgreSQL.
- Warehouse: Star Schema — `fact_post`, `fact_sentiment` + 4 dim tables + 7 analytical views.
- API: Django (JsonResponse, không dùng DRF) → 12 endpoints.
- Dashboard: Next.js (App Router, plain CSS) + Power BI là artifact nộp chính.
- Sentiment: Vietnamese keyword/rule fallback (không phải PhoBERT đầy đủ — đây là quyết định có cân nhắc, cần giải thích lý do).

*Số liệu thực tế:*
- 817 fact posts, 1,526 sentiment comments.
- 8 trang YouTube chính thức.
- Dữ liệu từ 2017-09-26 đến 2026-05-26.
- Total reach proxy: 167,066,949 views.
- Total engagement: 48,325. Avg engagement rate: 1.9164%. Virality score: 0% (YouTube không expose share count).
- Quality gate: 26 PASS, 17 INFO, 0 FAIL (43 validation rows).
- Test suite: 56 Python tests passed, 7 frontend tests passed, 0 npm vulnerabilities.

*Các quyết định thiết kế đáng chú ý (cần phân tích, không chỉ liệt kê):*
- Thu hẹp từ đa nền tảng xuống YouTube-only.
- Loại bỏ query-search batch (59 posts, 166 comments, 41 orphan pages) vì 98.76% reach không phải trang chính thức — ưu tiên data quality hơn data volume.
- Dùng lightweight sentiment thay vì PhoBERT vì tài nguyên tính toán và thời gian thực thi trong môi trường capstone.
- Power BI `.pbix` tạo thủ công vì không có automation trong môi trường này.
- Loại The Coffee House vì không xác định được channel ID chính thức đáng tin cậy.

---

**Cấu trúc báo cáo cần viết:**

1. **Tóm tắt điều hành** (Executive Summary) — ~300 từ, nêu bài toán, cách tiếp cận, kết quả nổi bật và giá trị thực tiễn. Viết như tóm tắt cho người quản lý, không phải cho giáo viên chấm điểm.

2. **Giới thiệu & Mục tiêu** — Bối cảnh thị trường F&B Việt Nam, lý do cần BI cho social media, câu hỏi kinh doanh cụ thể dự án trả lời, KPI được chọn và tại sao.

3. **Phương pháp luận** — Giải thích lý thuyết Kimball Dimensional Modeling, Star Schema, ETL pipeline concept, sentiment analysis trong NLP tiếng Việt. Kết nối lý thuyết với lựa chọn thiết kế thực tế của dự án.

4. **Thu thập dữ liệu & ETL** — Mô tả quy trình extract từ YouTube API v3 (uploads playlist → playlistItems → videos.list), chiến lược deduplication (natural key: platform_id + external_id), xử lý rate limit, raw JSONL storage, normalization. Giải thích tại sao loại query-search batch.

5. **Thiết kế Data Warehouse** — Mô tả Star Schema, từng bảng fact/dim, KPI definitions (`engagement_rate`, `virality_score`, `sentiment_ratio`, `share_of_voice`), 7 analytical views và mục đích từng view, quality gate 43 validation rows.

6. **Backend API & Web Dashboard** — Giải thích vai trò của Django API layer, thiết kế endpoint, lý do dùng JsonResponse thay DRF trong bối cảnh này. Next.js dashboard các trang chính, error/loading states, i18n.

7. **Kết quả phân tích & BI Insights** — Đây là phần trọng tâm. Phân tích thực sự từ số liệu: tại sao Trung Nguyen Legend chiếm 600/817 posts (73%); ý nghĩa avg engagement rate 1.9164% trong ngành F&B YouTube; virality score 0% và hạn chế dữ liệu share; phân phối không đều giữa các thương hiệu và gợi ý chiến lược. Đưa ra ít nhất 5 insights có lập luận, không chỉ mô tả số.

8. **Dashboard & Visualization** — Mô tả Power BI (8 trang) và Next.js dashboard, lựa chọn chart type và lý do, cách DAX measures ánh xạ KPI definitions.

9. **Kiểm thử & Đảm bảo chất lượng** — Python regression tests, frontend Jest tests, warehouse quality gate, npm audit. Giải thích tại sao mỗi lớp test tồn tại và nó bắt được loại lỗi gì.

10. **Hạn chế & Hướng phát triển** — Thành thật về: YouTube-only scope, sentiment rule-based, virality score = 0, không có The Coffee House. Mỗi hạn chế đi kèm lý do quyết định và hướng cải thiện cụ thể (không phải "có thể mở rộng trong tương lai").

11. **Kết luận** — Nhìn lại bài toán ban đầu, dự án đã trả lời được câu hỏi kinh doanh nào, câu nào chưa, và giá trị học thuật của quá trình thực hiện.

12. **Phụ lục** — Data Dictionary các bảng chính, schema diagram mô tả bằng text, danh sách endpoint API.

---

**Yêu cầu văn phong:**
- Viết như sinh viên năm cuối có kinh nghiệm thực tế, không phải như chatbot tóm tắt tài liệu.
- Câu văn đa dạng độ dài. Có đoạn ngắn để nhấn mạnh, có đoạn phân tích dài.
- Khi giải thích quyết định kỹ thuật, dùng ngôi thứ nhất số nhiều ("nhóm quyết định...", "chúng tôi chọn...") và nêu trade-off thật sự.
- Tránh: mở đầu bằng "Trong bối cảnh...", kết luận bằng "Tóm lại, dự án đã...", liệt kê bullet 5 điểm cho mọi thứ, câu bị động thụ động liên tục.
- Dùng số liệu thực cụ thể ở mọi nơi có thể. Đừng viết "lượng dữ liệu lớn" khi có thể viết "817 bài đăng trải dài gần 9 năm".
- Độ dài mục tiêu: 6,000–8,000 từ.

---

Đây là prompt đủ để Codex tự handle phần kỹ thuật sâu và nội dung phân tích — bạn không cần thêm gì nữa. Nếu muốn kiểm soát thêm, có thể append một dòng cuối như: *"Ưu tiên chiều sâu phân tích ở mục 7 (Insights) và mục 3 (Phương pháp luận) — đây là phần giám khảo sẽ đọc kỹ nhất."*