# OUTLINE BÁO CÁO CUỐI KỲ
## SocialLens BI — Hệ Thống Business Intelligence Phân Tích Mạng Xã Hội Ngành F&B

> **Môn học:** Business Intelligence
> **Thương hiệu chính:** Highlands Coffee Vietnam
> **Nền tảng phân tích:** YouTube (official channels)
> **Nguồn dữ liệu:** PostgreSQL warehouse — schema `social_dw`
> **Độ dài mục tiêu:** 6,000–8,000 từ

---

## TÓM TẮT ĐIỀU HÀNH *(Executive Summary)*
*~300 từ — viết sau cùng, tóm gọn toàn bộ báo cáo*

- Bối cảnh bài toán: thị trường F&B Việt Nam cạnh tranh cao, dữ liệu social media chưa được khai thác có hệ thống.
- Cách tiếp cận: xây hệ thống BI end-to-end từ ETL → Warehouse → Dashboard, tập trung YouTube vì độ tin cậy API.
- Kết quả nổi bật: 817 posts, 167 triệu views proxy, avg engagement 1.9164%, quality gate 26 PASS / 0 FAIL.
- Giá trị thực tiễn: cung cấp baseline đo hiệu suất nội dung và benchmark cạnh tranh có thể tái sử dụng.

---

## CHƯƠNG 1 — GIỚI THIỆU VÀ MỤC TIÊU

### 1.1 Bối cảnh nghiên cứu
- Thị trường F&B Việt Nam và vai trò của social media marketing.
- Khoảng trống: các thương hiệu thu thập data nhưng thiếu hạ tầng phân tích có cấu trúc.
- Lý do chọn Highlands Coffee làm case study chính.

### 1.2 Câu hỏi kinh doanh *(Business Questions)*
Dự án trả lời ba câu hỏi cụ thể:

1. **Nội dung nào hiệu quả?** — Loại video, chủ đề, thời điểm đăng nào mang lại engagement cao nhất cho Highlands Coffee?
2. **Khách hàng đang cảm nhận gì?** — Xu hướng sentiment trong bình luận thay đổi ra sao theo thời gian và sự kiện?
3. **So với đối thủ, Highlands đang ở đâu?** — Share of voice, engagement rate, tần suất đăng bài so với 7 thương hiệu cạnh tranh.

### 1.3 KPI được chọn và lý do
| KPI | Công thức | Lý do chọn |
|-----|-----------|------------|
| Engagement Rate | (likes + comments) / views × 100 | Đo chất lượng tương tác, không phụ thuộc quy mô kênh |
| Virality Score | shares / views × 100 | Đo khả năng lan truyền *(lưu ý: = 0% do YouTube API không expose share count)* |
| Sentiment Ratio | positive_comments / total × 100 | Đo sức khỏe thương hiệu qua nhận thức cộng đồng |
| Share of Voice | reach của page / total reach × 100 | Đo vị trí cạnh tranh tương đối |

### 1.4 Phạm vi và giới hạn có chủ đích
- YouTube only: lý do loại Facebook (App Review API), TikTok (Research API hạn chế).
- 8 thương hiệu chính thức, loại The Coffee House (không xác định được channel ID đáng tin cậy).
- Khoảng thời gian: 2017–2026.

---

## CHƯƠNG 2 — PHƯƠNG PHÁP LUẬN

### 2.1 Dimensional Modeling — Lý thuyết Kimball
- Star Schema vs Snowflake Schema: lý do chọn Star Schema cho bài toán BI dashboard.
- Fact table vs Dimension table: phân biệt và nguyên tắc thiết kế.
- Granularity: mỗi row trong `fact_post` = một video; mỗi row trong `fact_sentiment` = một comment.

### 2.2 ETL Pipeline — Khái niệm và ứng dụng
- Extract → Transform → Load: vai trò từng bước trong pipeline dự án.
- Idempotency và deduplication: tại sao cần natural key `(platform_id, external_post_id)`.
- Quality gate như một tầng kiểm soát bắt buộc, không phải tùy chọn.

### 2.3 Sentiment Analysis trong NLP tiếng Việt
- Thách thức đặc thù: tiếng Việt có dấu, viết tắt mạng xã hội, thiếu dữ liệu gán nhãn công khai.
- Phổ phương pháp: từ keyword/rule-based → PhoBERT → ViSoBERT.
- Lý do chọn rule-based fallback: tài nguyên tính toán capstone, không có tập validation gán nhãn thủ công, kết quả đủ dùng làm tín hiệu định hướng *(directional signal)* — không phải NLP benchmark.

### 2.4 Quyết định thiết kế tổng thể
- Ưu tiên data quality hơn data volume: loại 59 posts query-search vì 98.76% reach không phải trang chính thức.
- Ưu tiên độ tin cậy hơn độ phủ: thu hẹp YouTube-only để có pipeline ổn định, có thể kiểm chứng.

---

## CHƯƠNG 3 — THU THẬP DỮ LIỆU VÀ ETL PIPELINE

### 3.1 Nguồn dữ liệu và chiến lược khai thác
- YouTube Data API v3: cấu trúc phân cấp `channels.list → uploads playlist → playlistItems.list → videos.list`.
- Tại sao dùng uploads playlist thay vì search API: quota-efficient, chỉ lấy video chính thức.
- Giới hạn API và cách xử lý: rate limit, quota 10,000 units/ngày, retry logic.

### 3.2 Raw Data Storage
- Lưu JSONL dưới `data/raw/`: lý do giữ raw data nguyên bản trước khi transform.
- Cấu trúc một record raw điển hình.

### 3.3 Transform — Làm sạch và chuẩn hóa
- Xử lý missing values: views = 0, likes = null, comments chưa được bật.
- Chuẩn hóa thời gian: ISO 8601 → UTC → GMT+7 cho analytical views.
- Encoding tiếng Việt: UTF-8 xuyên suốt pipeline.
- Tính toán chỉ số dẫn xuất: `engagement_count`, `engagement_rate`, `virality_score`.

### 3.4 Sentiment Analysis Pipeline
- Luồng xử lý comment: lấy top N comment → làm sạch text → phân loại → lưu score.
- Output: label (Positive/Neutral/Negative) + score (−1.0 đến +1.0).
- Hạn chế được thừa nhận: không có confusion matrix, không validate với gold standard.

### 3.5 Deduplication và Upsert
- Natural key rules: post dedup theo `(platform_id, external_post_id)`, comment theo `(platform_id, external_comment_id)`.
- ETL upsert đảm bảo chạy lại pipeline không sinh duplicate.

### 3.6 Quyết định loại query-search batch
- Batch thử nghiệm: 59 posts thêm, 166 comments, 41 orphan pages.
- Vấn đề phát hiện: 98.76% reach thuộc trang không chính thức — nhiễu làm sai lệch KPI.
- Quyết định: archive dưới `data/processed_archive/`, không nạp vào warehouse chính.
- Bài học: volume không thay thế được quality trong BI.

---

## CHƯƠNG 4 — THIẾT KẾ DATA WAREHOUSE

### 4.1 Star Schema — Tổng quan
*[Mô tả sơ đồ ERD bằng văn bản nếu không có hình]*
- 2 fact tables: `fact_post`, `fact_sentiment`.
- 4 dimension tables: `dim_time`, `dim_platform`, `dim_content_type`, `dim_page`.
- Schema `social_dw` trong PostgreSQL.

### 4.2 Fact Tables

**`fact_post`** — một row = một YouTube video:
- Các cột đo lường: `reach` (= views proxy), `likes`, `comment_count`, `engagement_count`, `engagement_rate`, `virality_score`.
- Foreign keys: `time_id`, `platform_id`, `content_type_id`, `page_id`.
- Lưu ý: `reach` là views proxy, không phải unique reach; `virality_score` = 0 do thiếu share data.

**`fact_sentiment`** — một row = một comment đã phân tích:
- Các cột: `sentiment_label`, `sentiment_score`, `comment_text` (hash/truncated).
- Liên kết với `fact_post` qua `post_id`.

### 4.3 Dimension Tables

**`dim_time`**: date, hour, day_name, week, month, quarter, year, is_weekend — phục vụ time intelligence trong Power BI.

**`dim_platform`**: YouTube là platform duy nhất trong MVP — thiết kế giữ trường platform để mở rộng sau.

**`dim_content_type`**: phân loại video theo nội dung (quảng cáo, review, event, vlog...).

**`dim_page`**: page_name, is_competitor, industry — trung tâm của competitor benchmarking.

### 4.4 Analytical Views — 7 views phục vụ trực tiếp Dashboard

| View | Mục đích |
|------|----------|
| `vw_executive_overview` | KPI tổng quan cho trang Overview |
| `vw_daily_engagement` | Time series engagement theo ngày |
| `vw_sentiment_trend` | Xu hướng sentiment theo tuần/tháng |
| `vw_content_performance` | So sánh hiệu suất theo loại nội dung |
| `vw_competitor_benchmark` | So sánh các thương hiệu |
| `vw_posting_time_heatmap` | Ma trận giờ × ngày trong tuần |
| `vw_viral_posts` | Top posts theo engagement |

### 4.5 ETL Run Logging
- Bảng `etl_runs`: ghi lại mỗi lần chạy pipeline — thời gian, số rows, source, trạng thái.
- Phục vụ audit trail và endpoint `GET /api/v1/sync/status/`.

### 4.6 Quality Gate — 43 Validation Rows
Kiểm tra 7 nhóm:
1. Duplicate natural keys.
2. Orphan facts (fact không có dimension tương ứng).
3. Non-negative metrics (views, likes không âm).
4. KPI reconciliation (engagement_rate tính lại khớp với stored value).
5. Valid sentiment labels và score range.
6. YouTube-only platform scope.
7. Approved official-channel page scope.

Kết quả: **26 PASS, 17 INFO, 0 FAIL** — đạt ngưỡng handoff.

---

## CHƯƠNG 5 — BACKEND API VÀ WEB DASHBOARD

### 5.1 Django API — Vai trò và thiết kế
- API layer tách biệt warehouse khỏi presentation layer: frontend không query PostgreSQL trực tiếp.
- Lý do dùng `JsonResponse` thay DRF: không cần serializer framework cho endpoint read-only đơn giản; giảm dependency.
- Error sanitization: warehouse errors → `{detail, source_type, error_code}`, không expose stack trace ra client.

### 5.2 Các Endpoint Chính

| Endpoint | Mục đích |
|----------|----------|
| `GET /api/v1/analytics/overview/` | KPI tổng quan — source: `vw_executive_overview` |
| `GET /api/v1/analytics/engagement/` | Time series — source: `vw_daily_engagement` |
| `GET /api/v1/analytics/sentiment/` | Sentiment trend — source: `vw_sentiment_trend` |
| `GET /api/v1/analytics/competitors/` | Benchmark — source: `vw_competitor_benchmark` |
| `GET /api/v1/analytics/insights/` | Tự động tóm tắt insights + freshness metadata |
| `GET /api/v1/sync/status/` | Trạng thái warehouse, ETL run cuối |

### 5.3 Next.js Web Dashboard
- 6 routes: `/dashboard`, `/content`, `/sentiment`, `/competitors`, `/posts`, `/data-health`.
- Mỗi page: loading state → fetch API → render → error fallback.
- Loại bỏ hoàn toàn static mock JSON: test guard ngăn import từ `frontend/src/data/*.json`.
- i18n: dictionary tiếng Anh/Việt cho label và tiêu đề.

### 5.4 Power BI — Artifact Nộp Chính
- Kết nối trực tiếp PostgreSQL `social_dw` (preferred) hoặc CSV exports (backup).
- 8 trang dashboard tương ứng 8 analytical views.
- DAX measures ánh xạ 1:1 với KPI definitions trong SPEC.
- Lý do `.pbix` tạo thủ công: Power BI Desktop automation không khả dụng trong môi trường này — quyết định thực dụng, có ghi nhận rõ trong STATUS.

---

## CHƯƠNG 6 — KẾT QUẢ PHÂN TÍCH VÀ BI INSIGHTS

*Đây là chương trọng tâm — mỗi insight cần có số liệu, lý giải, và gợi ý hành động.*

### 6.1 Tổng quan dữ liệu
- 817 posts / 8 thương hiệu / ~9 năm (2017–2026).
- 167,066,949 views proxy — con số tuyệt đối ấn tượng nhưng cần đặt vào context phân phối.
- 48,325 total engagement với avg rate 1.9164%.

### 6.2 Insight 1 — Bất cân xứng nghiêm trọng trong tập dữ liệu
- Trung Nguyen Legend: 600/817 posts (73.4%) và 1,258/1,526 comments (82.4%).
- Highlands Coffee: 123 posts (15%) — nhiều hơn về volume so với Phuc Long, Cong Caphe nhưng ít hơn rất nhiều so với Trung Nguyen.
- Ý nghĩa phân tích: comparison phải dùng rate (engagement rate, post frequency) thay vì absolute count; bất kỳ benchmark nào dùng average đều bị kéo lệch bởi Trung Nguyen.

### 6.3 Insight 2 — Engagement Rate không tỷ lệ thuận với quy mô
- Phân tích tương quan: kênh nhỏ (Phuc Long, Cong Caphe) thường có engagement rate cao hơn kênh lớn — hiện tượng phổ biến trên YouTube.
- Gợi ý cho Highlands: quy mô views (reach) không phản ánh chất lượng kết nối với khán giả; cần track engagement rate theo từng loại nội dung.

### 6.4 Insight 3 — Virality Score = 0% và hạn chế dữ liệu
- Nguyên nhân kỹ thuật: YouTube Data API v3 không expose share count trong response tiêu chuẩn.
- Ý nghĩa: metric này không có giá trị trong báo cáo hiện tại — trình bày rõ thay vì ẩn đi.
- Hướng cải thiện: cross-platform tracking (theo dõi video YouTube được share lên Facebook/TikTok) hoặc dùng YouTube Analytics API nội bộ nếu có quyền truy cập kênh.

### 6.5 Insight 4 — Posting Heatmap và thời điểm tối ưu
- Phân tích ma trận giờ × ngày từ `vw_posting_time_heatmap`.
- Xác định khung giờ và ngày có engagement cao nhất cho Highlands Coffee.
- So sánh với pattern của Trung Nguyen Legend — thương hiệu có data dày nhất.

### 6.6 Insight 5 — Sentiment như tín hiệu định hướng
- Phân phối Positive/Neutral/Negative theo thương hiệu.
- Xu hướng sentiment của Highlands Coffee theo thời gian: có đỉnh hay đáy bất thường không?
- Caveat quan trọng cần nêu rõ: sentiment rule-based, không validate bằng human annotation — dùng làm directional signal, không phải KPI tuyệt đối.

### 6.7 Insight 6 — Share of Voice trong ngành F&B YouTube
- Highlands Coffee chiếm bao nhiêu % total reach trong tập 8 thương hiệu?
- Trung Nguyen Legend vs Highlands: khoảng cách về SOV và hàm ý chiến lược.
- Các thương hiệu có presence thấp (KOI Thé 3 posts, Gong Cha 2 posts, Starbucks 1 post): thiếu dữ liệu hay thiếu chiến lược YouTube?

---

## CHƯƠNG 7 — KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG

### 7.1 Chiến lược kiểm thử đa tầng
*Giải thích tại sao cần nhiều lớp, không phải chỉ một.*

### 7.2 Python Regression Tests — 56 passed, 1 skipped
- Bắt gì: ETL logic, normalization, KPI calculation, deduplication, quality gate validation.
- 1 test skipped: YouTube live contract test — chỉ chạy khi có API key (`RUN_YOUTUBE_LIVE_TESTS=1`).

### 7.3 Frontend Tests — 7 passed (Jest + React Testing Library)
- Bắt gì: component rendering, API data mapping, no-mock guard (ngăn import static JSON).
- Tại sao có no-mock guard test: đảm bảo không ai vô ý restore fallback mock data.

### 7.4 Django Check và Build
- `python manage.py check`: phát hiện misconfiguration Django trước khi chạy.
- `npm run build`: đảm bảo production bundle không có lỗi.
- `npm audit`: 0 vulnerabilities trong production dependencies.

### 7.5 Warehouse Quality Gate — 43 rows, 26 PASS, 17 INFO, 0 FAIL
- INFO vs FAIL: INFO là cảnh báo có nhận thức (ví dụ: virality = 0 do thiếu share data) — không phải lỗi.
- Ngưỡng chấp nhận: 0 FAIL là điều kiện cần trước khi xuất exports dùng cho Power BI.

---

## CHƯƠNG 8 — HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

*Mỗi hạn chế: tên → nguyên nhân → quyết định tại thời điểm đó → hướng giải quyết cụ thể.*

### 8.1 YouTube-only Scope
- Nguyên nhân: Facebook Graph API yêu cầu App Review (rủi ro thời gian), TikTok Research API hạn chế quyền truy cập.
- Hướng mở rộng: thêm Facebook khi có Business account với quyền pages_read_engagement; TikTok khi Research API mở rộng cho academic.

### 8.2 Sentiment Rule-based
- Nguyên nhân: PhoBERT cần GPU và tập validation gán nhãn thủ công để đánh giá.
- Hướng cải thiện: gán nhãn 500–1,000 comments thủ công → fine-tune ViSoBERT → so sánh F1 score với rule-based baseline.

### 8.3 Virality Score = 0%
- Nguyên nhân: YouTube Data API không trả về share count.
- Hướng cải thiện: YouTube Analytics API (cần channel ownership) hoặc social listening tool bên thứ ba.

### 8.4 Thiếu The Coffee House
- Nguyên nhân: không xác định được official YouTube channel ID với độ tin cậy đủ cao — thêm nhầm channel sẽ làm sai toàn bộ competitor data.
- Hướng giải quyết: xác minh qua website chính thức của thương hiệu hoặc Social Blade.

### 8.5 Không có Forecasting và Clustering
- Thuộc roadmap giai đoạn 4 (ARIMA/Prophet cho engagement, K-Means cho content clustering).
- Lý do chưa productionize: ưu tiên data quality và pipeline ổn định trong MVP; forecasting trên 817 posts với phân phối lệch có thể cho kết quả misleading.

---

## CHƯƠNG 9 — KẾT LUẬN

### 9.1 Nhìn lại câu hỏi kinh doanh ban đầu
- Câu hỏi 1 (nội dung hiệu quả): trả lời được qua `vw_content_performance` và posting heatmap.
- Câu hỏi 2 (sentiment khách hàng): trả lời được ở mức directional — cần NLP tốt hơn để dùng làm KPI tuyệt đối.
- Câu hỏi 3 (vị trí so với đối thủ): trả lời được cho 7/8 thương hiệu target (thiếu The Coffee House).

### 9.2 Giá trị học thuật của quá trình
- Hiểu thực tế rằng API không bao giờ cho đủ data như thiết kế ban đầu — cần có kế hoạch dự phòng và quyết định trade-off có lý do.
- Star Schema không chỉ là lý thuyết giáo khoa: granularity sai một bậc sẽ phá vỡ toàn bộ analytical views.
- Quality gate là tư duy engineering, không phải checklist cuối kỳ.

### 9.3 Đề xuất tiếp theo (nếu dự án tiếp tục)
- Mở rộng sang Facebook + TikTok.
- Upgrade sentiment lên ViSoBERT với validation set.
- Tự động hóa Power BI refresh qua PostgreSQL live connection.
- Thêm alerting: tự động flag khi engagement rate của một thương hiệu drop >20% so với baseline.

---

## PHỤ LỤC

### A. Data Dictionary — Các bảng chính

**`fact_post`**
| Cột | Kiểu | Mô tả |
|-----|------|-------|
| post_id | BIGINT PK | Surrogate key |
| external_post_id | VARCHAR | YouTube video ID |
| platform_id | INT FK | → dim_platform |
| time_id | INT FK | → dim_time (published date) |
| page_id | INT FK | → dim_page |
| content_type_id | INT FK | → dim_content_type |
| reach | BIGINT | View count (proxy) |
| likes | INT | Like count |
| comment_count | INT | Comment count từ API |
| engagement_count | INT | likes + comment_count |
| engagement_rate | DECIMAL | engagement_count / reach × 100 |
| virality_score | DECIMAL | shares / reach × 100 (= 0) |

**`fact_sentiment`**
| Cột | Kiểu | Mô tả |
|-----|------|-------|
| sentiment_id | BIGINT PK | Surrogate key |
| post_id | BIGINT FK | → fact_post |
| time_id | INT FK | → dim_time (comment date) |
| sentiment_label | VARCHAR | Positive / Neutral / Negative |
| sentiment_score | DECIMAL | −1.0 đến +1.0 |

### B. Danh sách Endpoint API

```
GET /health/
GET /api/v1/posts/
GET /api/v1/posts/{post_id}/
GET /api/v1/analytics/overview/
GET /api/v1/analytics/engagement/?limit=120
GET /api/v1/analytics/sentiment/?limit=120
GET /api/v1/analytics/top-posts/
GET /api/v1/analytics/content-performance/
GET /api/v1/analytics/heatmap/
GET /api/v1/analytics/competitors/
GET /api/v1/analytics/insights/
GET /api/v1/sync/status/
```

### C. Kết quả Kiểm thử Tổng hợp

| Hạng mục | Kết quả |
|----------|---------|
| Python tests | 56 passed, 1 skipped |
| Frontend tests | 7 passed |
| Django check | No issues |
| Next.js build | Pass |
| npm audit (production) | 0 vulnerabilities |
| Warehouse quality gate | 26 PASS, 17 INFO, 0 FAIL |

### D. Snapshot Dữ liệu Cuối

| Metric | Giá trị |
|--------|---------|
| Fact posts | 817 |
| Fact sentiment comments | 1,526 |
| Active pages | 8 |
| Date range | 2017-09-26 → 2026-05-26 |
| Total reach (views proxy) | 167,066,949 |
| Total engagement | 48,325 |
| Avg engagement rate | 1.9164% |
| Avg virality score | 0.0000% |

---

*Outline này là tài liệu làm việc — các con số và insights trong chương 6 cần được thay bằng kết quả phân tích thực tế từ warehouse trước khi nộp.*