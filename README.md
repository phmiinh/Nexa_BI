# 📊 Phân Tích Dữ Liệu Mạng Xã Hội Cho Doanh Nghiệp
> Business Intelligence Project — Môn Học: Business Intelligence

---

## 🎯 Mục Tiêu Dự Án

Xây dựng hệ thống Business Intelligence để thu thập, xử lý và phân tích dữ liệu từ các nền tảng mạng xã hội (Facebook, TikTok, YouTube, Instagram), từ đó cung cấp insight chiến lược cho doanh nghiệp trong việc ra quyết định marketing, quản lý thương hiệu và tối ưu hóa nội dung.

---

## 📁 Cấu Trúc Dự Án

```
social-media-bi/
│
├── 📂 data/
│   ├── raw/                    # Dữ liệu thô từ API / crawl
│   │   ├── facebook/
│   │   ├── tiktok/
│   │   ├── youtube/
│   │   └── instagram/
│   ├── processed/              # Dữ liệu sau khi làm sạch
│   └── sample/                 # Dữ liệu mẫu để demo
│
├── 📂 etl/
│   ├── extract/                # Scripts thu thập dữ liệu
│   │   ├── facebook_crawler.py
│   │   ├── tiktok_api.py
│   │   └── youtube_api.py
│   ├── transform/              # Scripts xử lý & làm sạch
│   │   ├── clean_data.py
│   │   ├── sentiment_analysis.py
│   │   └── normalization.py
│   └── load/                   # Scripts nạp vào Data Warehouse
│       └── load_to_dw.py
│
├── 📂 warehouse/
│   ├── schema/                 # DDL scripts tạo bảng
│   │   ├── fact_tables.sql
│   │   └── dim_tables.sql
│   └── queries/                # Analytical queries
│       ├── engagement_analysis.sql
│       ├── sentiment_trend.sql
│       └── competitor_benchmark.sql
│
├── 📂 dashboard/
│   ├── power_bi/               # File .pbix hoặc templates
│   ├── assets/                 # Hình ảnh, logo
│   └── screenshots/            # Ảnh chụp dashboard
│
├── 📂 docs/
│   ├── report/                 # Báo cáo bài tập lớn
│   ├── presentation/           # Slide thuyết trình
│   └── diagrams/               # Sơ đồ kiến trúc hệ thống
│
├── 📂 notebooks/               # Jupyter Notebooks phân tích
│   ├── 01_data_exploration.ipynb
│   ├── 02_sentiment_analysis.ipynb
│   └── 03_trend_analysis.ipynb
│
├── requirements.txt
├── config.example.yaml
└── README.md
```

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                   DATA SOURCES                          │
│  Facebook API | TikTok API | YouTube API | Instagram    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  ETL PIPELINE                           │
│   Extract → Transform (NLP/Sentiment) → Load            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│               DATA WAREHOUSE (Star Schema)              │
│  Fact: Posts, Interactions | Dim: Time, Platform, User  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            ANALYTICS & VISUALIZATION                    │
│         Power BI Dashboard | Python Charts              │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Các Phân Tích Chính

### 1. Phân Tích Hiệu Quả Nội Dung
- Reach, Impression, Engagement Rate theo từng loại bài đăng
- So sánh hiệu suất: video vs. ảnh vs. text
- Thời điểm đăng bài tối ưu (heatmap theo giờ/ngày)

### 2. Phân Tích Cảm Xúc (Sentiment Analysis)
- Phân loại bình luận: Tích cực / Trung tính / Tiêu cực
- Trend cảm xúc theo thời gian
- Cảnh báo khủng hoảng truyền thông

### 3. Phân Tích Đối Thủ (Competitor Benchmarking)
- So sánh chỉ số tăng trưởng followers
- Phân tích nội dung viral của đối thủ
- Gap analysis: điểm mạnh / điểm yếu

### 4. Phân Tích Xu Hướng & Hashtag
- Top hashtags theo ngành
- Trending topics theo tuần/tháng
- Dự báo xu hướng (forecasting)

### 5. Phân Tích Đối Tượng Khách Hàng
- Phân khúc demographics (tuổi, giới tính, địa lý)
- Giờ hoạt động của người dùng
- Hành vi tương tác

---

## 🛠️ Công Nghệ Sử Dụng

| Layer | Công cụ |
|-------|---------|
| Thu thập dữ liệu | Python, Facebook Graph API, YouTube Data API v3 |
| Xử lý & ETL | Apache Airflow / Python scripts |
| Phân tích NLP | PhoBERT / VADER / TextBlob |
| Lưu trữ | PostgreSQL / MySQL |
| Visualization | Power BI / Tableau / Matplotlib |
| Môi trường | Jupyter Notebook, VS Code |

---

## 🗄️ Data Warehouse Schema (Star Schema)

### Fact Tables
- **fact_post**: post_id, platform_id, time_id, reach, impressions, likes, comments, shares, engagement_rate
- **fact_sentiment**: comment_id, post_id, sentiment_score, sentiment_label, time_id

### Dimension Tables
- **dim_platform**: platform_id, platform_name, platform_type
- **dim_time**: time_id, date, hour, day_of_week, week, month, quarter, year
- **dim_content_type**: type_id, type_name (video/image/story/reel)
- **dim_page**: page_id, page_name, industry, competitor_flag

---

## 📈 KPIs Theo Dõi

| KPI | Định nghĩa | Mục tiêu |
|-----|-----------|---------|
| Engagement Rate | (Likes + Comments + Shares) / Reach × 100 | ≥ 3% |
| Sentiment Score | % bình luận tích cực | ≥ 70% |
| Reach Growth | % tăng trưởng reach theo tháng | ≥ 10% |
| Response Time | Thời gian phản hồi bình luận trung bình | ≤ 2 giờ |
| Share of Voice | % nhắc đến thương hiệu / tổng ngành | Benchmark |

---

## 🚀 Hướng Dẫn Cài Đặt

```bash
# 1. Clone repository
git clone https://github.com/your-username/social-media-bi.git
cd social-media-bi

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Cấu hình API keys
cp config.example.yaml config.yaml
# Điền API keys vào config.yaml

# 4. Chạy ETL pipeline
python etl/extract/facebook_crawler.py
python etl/transform/clean_data.py
python etl/load/load_to_dw.py

# 5. Mở notebook phân tích
jupyter notebook notebooks/
```

---

## 📋 requirements.txt

```
pandas==2.1.0
numpy==1.24.0
requests==2.31.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.7
transformers==4.33.0
torch==2.0.1
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.17.0
jupyter==1.0.0
python-dotenv==1.0.0
facebook-sdk==3.1.0
google-api-python-client==2.97.0
```

---

## 👥 Thành Viên Nhóm

| STT | Họ Tên | MSSV | Vai Trò |
|-----|--------|------|---------|
| 1 | Nguyễn Văn A | 2100XXXX | Leader, Data Warehouse |
| 2 | Trần Thị B | 2100XXXX | ETL Pipeline, NLP |
| 3 | Lê Văn C | 2100XXXX | Dashboard, Visualization |
| 4 | Phạm Thị D | 2100XXXX | Data Collection, Report |

---

## 📚 Tài Liệu Tham Khảo

- Facebook Graph API Documentation: https://developers.facebook.com/docs/graph-api
- YouTube Data API v3: https://developers.google.com/youtube/v3
- PhoBERT — Vietnamese NLP model: https://github.com/VinAIResearch/PhoBERT
- Kimball Group — Data Warehouse Design: https://www.kimballgroup.com

---

## 📄 Giấy Phép

Dự án này được thực hiện cho mục đích học tập tại trường đại học.  
© 2024 — Nhóm Dự Án BI — Môn Business Intelligence

---

> 💡 **Lưu ý**: Toàn bộ dữ liệu thu thập tuân thủ điều khoản sử dụng của từng nền tảng mạng xã hội và quy định về bảo vệ dữ liệu cá nhân (PDPD Việt Nam).
