# 🗺️ ROADMAP — Phân Tích Dữ Liệu Mạng Xã Hội Cho Doanh Nghiệp
> Business Intelligence Project | Tổng thời gian: 15 tuần

---

## 📌 Tổng Quan Tiến Độ

| Giai đoạn | Thời gian | Nội dung chính | Đầu ra |
|-----------|-----------|----------------|--------|
| 1 | Tuần 1–2  | Khởi động & Lập kế hoạch | Project Plan, Đề cương |
| 2 | Tuần 3–5  | Thu thập dữ liệu & ETL | Dataset đã xử lý |
| 3 | Tuần 6–8  | Data Warehouse | DW hoàn chỉnh + SQL queries |
| 4 | Tuần 9–12 | Dashboard & Phân tích | Power BI Dashboard + Insights |
| 5 | Tuần 13–15 | Hoàn thiện & Báo cáo | Báo cáo + Slide thuyết trình |

---

## 🔵 Giai Đoạn 1 — Khởi Động & Lập Kế Hoạch (Tuần 1–2)

### Mục tiêu
Xác định rõ phạm vi dự án, câu hỏi kinh doanh cần trả lời, và chuẩn bị nền tảng kỹ thuật.

### Công việc chi tiết

**Tuần 1 — Phân tích yêu cầu**
- [ ] Chọn doanh nghiệp/thương hiệu làm case study (gợi ý: F&B, thời trang, TMĐT)
- [ ] Xác định các câu hỏi kinh doanh (Business Questions):
  - Nội dung nào đang hoạt động hiệu quả nhất?
  - Cảm xúc khách hàng đang ở mức nào?
  - Đối thủ cạnh tranh đang làm gì tốt hơn?
- [ ] Xác định các KPI cần đo lường
- [ ] Phân công vai trò trong nhóm

**Tuần 2 — Thiết kế kiến trúc**
- [ ] Khảo sát và đăng ký API: Facebook Graph API, YouTube Data API v3, TikTok Research API
- [ ] Đánh giá giới hạn API (rate limit, dữ liệu có thể truy cập)
- [ ] Vẽ sơ đồ kiến trúc hệ thống BI (data flow diagram)
- [ ] Chọn stack công nghệ và cài đặt môi trường phát triển
- [ ] Tạo repository GitHub, thiết lập cấu trúc thư mục dự án

### Đầu ra (Deliverables)
- `docs/Project_Plan.pdf` — Kế hoạch dự án chi tiết
- `docs/Business_Requirements.md` — Yêu cầu kinh doanh và KPI
- `docs/diagrams/architecture.png` — Sơ đồ kiến trúc hệ thống
- Repository GitHub đã thiết lập đầy đủ

### Công nghệ
Python, Git/GitHub, draw.io (vẽ sơ đồ)

---

## 🟢 Giai Đoạn 2 — Thu Thập Dữ Liệu & ETL (Tuần 3–5)

### Mục tiêu
Xây dựng pipeline tự động thu thập, làm sạch và xử lý dữ liệu từ các nền tảng mạng xã hội.

### Công việc chi tiết

**Tuần 3 — Extract: Thu thập dữ liệu**
- [ ] Viết script kết nối Facebook Graph API
  - Thu thập: bài đăng, số like/comment/share, reach, impressions
  - Thu thập: bình luận (top 100 per post)
- [ ] Viết script kết nối YouTube Data API v3
  - Thu thập: video metadata, view count, like, comment
- [ ] Lưu raw data dạng JSON/CSV vào thư mục `data/raw/`
- [ ] Xử lý lỗi kết nối, retry logic, logging

**Tuần 4 — Transform: Làm sạch & xử lý**
- [ ] Xử lý missing values, duplicate records
- [ ] Chuẩn hoá định dạng ngày giờ (UTC → GMT+7)
- [ ] Chuẩn hoá encoding tiếng Việt (UTF-8)
- [ ] Tính toán các chỉ số dẫn xuất:
  - `engagement_rate = (likes + comments + shares) / reach * 100`
  - `virality_score = shares / reach * 100`
- [ ] Phân loại loại nội dung: video, image, story, reel, text

**Tuần 5 — Sentiment Analysis**
- [ ] Cài đặt và cấu hình mô hình NLP:
  - Tiếng Việt: PhoBERT (`vinai/phobert-base`) hoặc underthesea
  - Tiếng Anh: VADER / TextBlob
- [ ] Xây dựng pipeline phân loại cảm xúc bình luận:
  - Label: Tích cực (Positive) / Trung tính (Neutral) / Tiêu cực (Negative)
  - Score: -1.0 đến +1.0
- [ ] Validate kết quả với tập dữ liệu mẫu đã gán nhãn thủ công
- [ ] Lưu kết quả vào `data/processed/`

### Đầu ra (Deliverables)
- `etl/extract/facebook_crawler.py`
- `etl/extract/youtube_api.py`
- `etl/transform/clean_data.py`
- `etl/transform/sentiment_analysis.py`
- `data/processed/` — Dataset sạch, sẵn sàng nạp vào DW
- `notebooks/01_data_exploration.ipynb` — EDA sơ bộ

### Công nghệ
Python, Pandas, Requests, PhoBERT/underthesea, Jupyter Notebook

---

## 🟡 Giai Đoạn 3 — Data Warehouse (Tuần 6–8)

### Mục tiêu
Thiết kế và triển khai Data Warehouse theo mô hình Star Schema, nạp dữ liệu và viết các analytical queries.

### Công việc chi tiết

**Tuần 6 — Thiết kế Star Schema**
- [ ] Thiết kế Fact Tables:
  - `fact_post`: post_id, platform_id, time_id, content_type_id, page_id, reach, impressions, likes, comments, shares, engagement_rate, virality_score
  - `fact_sentiment`: sentiment_id, comment_id, post_id, time_id, sentiment_label, sentiment_score
- [ ] Thiết kế Dimension Tables:
  - `dim_time`: time_id, date, hour, day_name, week, month, quarter, year, is_weekend
  - `dim_platform`: platform_id, platform_name, platform_type
  - `dim_content_type`: type_id, type_name, type_category
  - `dim_page`: page_id, page_name, industry, is_competitor, follower_count
- [ ] Vẽ ERD (Entity Relationship Diagram)
- [ ] Viết DDL scripts tạo bảng

**Tuần 7 — Load dữ liệu**
- [ ] Cài đặt và cấu hình PostgreSQL
- [ ] Chạy DDL scripts tạo schema
- [ ] Viết ETL Load scripts (`etl/load/load_to_dw.py`)
- [ ] Nạp toàn bộ dữ liệu đã xử lý vào DW
- [ ] Kiểm tra tính toàn vẹn: row count, null check, constraint validation

**Tuần 8 — Analytical Queries**
- [ ] Viết SQL queries phân tích:
  - Engagement rate theo platform và loại nội dung
  - Trend cảm xúc theo tuần/tháng
  - Top bài đăng hiệu quả nhất
  - So sánh hiệu suất với đối thủ cạnh tranh
  - Heatmap thời điểm đăng bài tối ưu
- [ ] Tối ưu hiệu năng: index, query plan
- [ ] Kiểm thử queries với dữ liệu thực tế

### Đầu ra (Deliverables)
- `warehouse/schema/fact_tables.sql`
- `warehouse/schema/dim_tables.sql`
- `warehouse/queries/engagement_analysis.sql`
- `warehouse/queries/sentiment_trend.sql`
- `warehouse/queries/competitor_benchmark.sql`
- `docs/diagrams/ERD.png` — Sơ đồ ERD
- Data Warehouse đã có dữ liệu, sẵn sàng kết nối Dashboard

### Công nghệ
PostgreSQL, SQLAlchemy, Python, dbdiagram.io (ERD)

---

## 🟣 Giai Đoạn 4 — Dashboard & Phân Tích Sâu (Tuần 9–12)

### Mục tiêu
Xây dựng dashboard trực quan bằng Power BI và thực hiện phân tích chuyên sâu để rút ra insights kinh doanh.

### Công việc chi tiết

**Tuần 9–10 — Xây dựng Power BI Dashboard**

Trang 1 — **Executive Overview**
- Tổng quan KPIs: Tổng reach, Avg. engagement rate, Sentiment score, Follower growth
- Biểu đồ line: Trend reach & engagement theo tháng
- Biểu đồ cột: So sánh hiệu suất theo platform

Trang 2 — **Content Performance**
- Heatmap: Engagement theo giờ và ngày trong tuần
- Biểu đồ tròn: Phân bổ loại nội dung (video/image/story)
- Bảng: Top 10 bài đăng hiệu quả nhất
- Biểu đồ scatter: Reach vs. Engagement Rate

Trang 3 — **Sentiment Analysis**
- Gauge chart: Overall sentiment score
- Biểu đồ line: Trend cảm xúc theo thời gian
- Word cloud: Từ khoá phổ biến trong bình luận tích cực / tiêu cực
- Biểu đồ stacked bar: Phân bổ sentiment theo platform

Trang 4 — **Competitor Benchmarking**
- Biểu đồ so sánh: Follower growth của thương hiệu vs. đối thủ
- Radar chart: So sánh đa chiều (engagement, sentiment, frequency)
- Bảng: Nội dung viral của đối thủ

**Tuần 11 — Phân tích chuyên sâu (Jupyter Notebook)**
- [ ] `02_sentiment_analysis.ipynb`: Phân tích chi tiết sentiment, confusion matrix, accuracy
- [ ] `03_trend_analysis.ipynb`: Time-series analysis, phát hiện bất thường
- [ ] Forecasting: Dự báo engagement rate 4 tuần tiếp theo (ARIMA / Prophet)
- [ ] Clustering: Phân nhóm nội dung theo hiệu suất (K-Means)

**Tuần 12 — Tổng hợp Insights & Khuyến nghị**
- [ ] Xác định ít nhất 5 insights kinh doanh có giá trị
- [ ] Đề xuất chiến lược nội dung dựa trên dữ liệu:
  - Loại nội dung nên ưu tiên
  - Khung giờ đăng bài tối ưu
  - Chủ đề/hashtag nên tập trung
  - Cách phản hồi bình luận tiêu cực
- [ ] Viết phần Insights & Recommendations cho báo cáo

### Đầu ra (Deliverables)
- `dashboard/power_bi/SocialMedia_BI.pbix` — File Power BI hoàn chỉnh
- `dashboard/screenshots/` — Ảnh chụp các trang dashboard
- `notebooks/02_sentiment_analysis.ipynb`
- `notebooks/03_trend_analysis.ipynb`
- `docs/Insights_Report.md` — Tóm tắt insights và khuyến nghị

### Công nghệ
Power BI Desktop, DAX, Python (Prophet, scikit-learn, matplotlib, seaborn)

---

## 🟠 Giai Đoạn 5 — Hoàn Thiện & Báo Cáo (Tuần 13–15)

### Mục tiêu
Hoàn thiện toàn bộ tài liệu, chuẩn bị thuyết trình và nộp bài.

### Công việc chi tiết

**Tuần 13 — Viết báo cáo chi tiết**
- [ ] Cấu trúc báo cáo:
  1. Tóm tắt điều hành (Executive Summary)
  2. Giới thiệu & Mục tiêu dự án
  3. Phương pháp luận (Methodology)
  4. Mô tả dữ liệu & ETL Process
  5. Thiết kế Data Warehouse
  6. Kết quả phân tích & Insights
  7. Dashboard & Visualization
  8. Kết luận & Hướng phát triển
  9. Phụ lục (code, schema, data dictionary)
- [ ] Viết Data Dictionary cho toàn bộ bảng trong DW
- [ ] Chụp screenshot và chú thích tất cả biểu đồ trong dashboard

**Tuần 14 — Chuẩn bị thuyết trình**
- [ ] Thiết kế slide deck (15–20 trang):
  - Slide 1: Tiêu đề + thành viên nhóm
  - Slide 2–3: Vấn đề kinh doanh & Mục tiêu
  - Slide 4–5: Kiến trúc hệ thống & Công nghệ
  - Slide 6–7: Dữ liệu & ETL Process
  - Slide 8–9: Data Warehouse Design
  - Slide 10–14: Demo Dashboard + Key Insights
  - Slide 15: Kết luận & Q&A
- [ ] Chuẩn bị demo live dashboard (Power BI)
- [ ] Luyện tập thuyết trình, phân chia thời gian cho từng thành viên
- [ ] Chuẩn bị câu hỏi Q&A dự kiến

**Tuần 15 — Review & Submit**
- [ ] Review toàn bộ code: clean up, comment, docstring
- [ ] Kiểm tra báo cáo: chính tả, format, trích dẫn tài liệu
- [ ] Quay video demo (nếu yêu cầu): 5–10 phút walkthrough dashboard
- [ ] Đóng gói và nộp bài:
  - Báo cáo PDF
  - Link GitHub repository
  - File Power BI (.pbix)
  - Video demo (nếu có)
- [ ] Thuyết trình trước hội đồng

### Đầu ra (Deliverables)
- `docs/report/Final_Report.pdf` — Báo cáo cuối kỳ hoàn chỉnh
- `docs/presentation/Slides.pptx` — Slide thuyết trình
- `docs/Data_Dictionary.md` — Từ điển dữ liệu
- Video demo (tuỳ yêu cầu giảng viên)
- Repository GitHub sạch, có README đầy đủ

---

## 📊 Phân Bổ Công Việc Theo Thành Viên (Gợi ý)

| Thành viên | Trách nhiệm chính |
|------------|-------------------|
| Leader | Quản lý tiến độ, kiến trúc hệ thống, báo cáo tổng hợp |
| Member 2 | ETL Pipeline, Data Cleaning, Sentiment Analysis (NLP) |
| Member 3 | Data Warehouse design, SQL queries, Power BI Dashboard |
| Member 4 | Data Collection (API), EDA notebooks, Slide thuyết trình |

---

## ⚠️ Rủi Ro & Phương Án Dự Phòng

| Rủi ro | Mức độ | Phương án dự phòng |
|--------|--------|-------------------|
| API bị giới hạn / chặn | Cao | Dùng dataset công khai từ Kaggle hoặc dữ liệu crawl thủ công |
| PhoBERT không đủ chính xác | Trung bình | Kết hợp với keyword-based rules; gán nhãn thủ công thêm |
| Thiếu dữ liệu lịch sử | Trung bình | Dùng dữ liệu mẫu để demo, chạy pipeline với khoảng thời gian ngắn hơn |
| Trễ tiến độ giai đoạn 2–3 | Trung bình | Rút gọn số lượng platform (ưu tiên Facebook + YouTube) |
| Power BI không kết nối được DW | Thấp | Export CSV từ PostgreSQL, import trực tiếp vào Power BI |

---

## 📚 Tài Nguyên Tham Khảo

**APIs & Dữ liệu**
- Facebook Graph API Explorer: https://developers.facebook.com/tools/explorer/
- YouTube Data API v3 Docs: https://developers.google.com/youtube/v3/docs
- Kaggle Social Media Datasets: https://www.kaggle.com/datasets (từ khoá: "social media analytics")

**NLP Tiếng Việt**
- PhoBERT: https://github.com/VinAIResearch/PhoBERT
- underthesea: https://github.com/undertheseanlp/underthesea
- ViSoBERT (sentiment): https://huggingface.co/uitnlp/visobert

**Data Warehouse**
- Kimball Group — Dimensional Modeling: https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

**Visualization**
- Power BI Documentation: https://docs.microsoft.com/power-bi/
- DAX Guide: https://dax.guide/

---

*Cập nhật lần cuối: 2024 | Môn: Business Intelligence*
