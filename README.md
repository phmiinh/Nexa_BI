# SocialLens BI

Hệ thống Business Intelligence phân tích hiệu quả truyền thông xã hội ngành F&B, lấy Highlands Coffee Vietnam làm thương hiệu trọng tâm và so sánh với các đối thủ trên YouTube official channels.

## Tổng Quan

SocialLens BI là bài tập lớn môn Business Intelligence với mục tiêu xây dựng một pipeline BI end-to-end từ dữ liệu thật đến dashboard và báo cáo. Hệ thống thu thập dữ liệu từ YouTube Data API v3, xử lý bằng Python ETL, nạp vào PostgreSQL warehouse schema `social_dw`, phục vụ dữ liệu qua Django API và hiển thị bằng Next.js web dashboard.

Phiên bản nộp cuối chọn phạm vi **YouTube official-channel only**. Quyết định này giúp dữ liệu sạch, có thể truy vết và tránh nhiễu từ search/query batch không chính thức. Power BI `.pbix` không bắt buộc trong bản nộp hiện tại; bằng chứng chính gồm warehouse, exports, API, web dashboard, screenshots và file báo cáo PDF.

## Artifact Nộp Bài

| Artifact | Mô tả |
| --- | --- |
| `Report Business Intelligence.pdf` | Báo cáo học thuật cuối kỳ |
| `README.md` | Tổng quan hệ thống, cách vận hành và trạng thái cuối |
| `dashboard/exports/` | CSV/JSON export từ 7 analytical views |
| `backend/`, `etl/`, `warehouse/`, `frontend/` | Source code hệ thống BI |
| `tests/` | Regression tests và contract checks |

## Phạm Vi Phân Tích

| Hạng mục | Giá trị |
| --- | --- |
| Thương hiệu chính | Highlands Coffee Vietnam |
| Nền tảng | YouTube official channels |
| Competitors | Trung Nguyên Legend, Phúc Long, Cộng Cà Phê, Cheese Coffee, KOI Thé Việt Nam, Gong Cha Vietnam, Starbucks Việt Nam |
| Source of truth | PostgreSQL schema `social_dw` |
| Runtime mock data | Không dùng mock/fallback JSON trong dashboard |
| Kiểu cập nhật | Batch ETL, không realtime |

The Coffee House không có trong warehouse cuối vì chưa xác định được official YouTube channel ID đủ tin cậy. Đây là giới hạn có chủ đích để bảo vệ chất lượng benchmark.

## Snapshot Dữ Liệu Cuối

Snapshot warehouse sau cleanup official-only:

| Metric | Value |
| --- | ---: |
| Fact posts | 817 |
| Fact sentiment comments | 1,526 |
| Active official pages | 8 |
| Date range | 2017-09-26 đến 2026-05-26 |
| Total reach/views proxy | 167,066,949 |
| Total engagement | 48,325 |
| Average engagement rate | 1.9164% |
| Average virality score | 0.0000% |
| Quality gate | 26 PASS, 17 INFO, 0 FAIL |

Ghi chú:

- `reach` là proxy từ YouTube views/impressions, không phải unique reach.
- `virality_score` bằng 0 vì YouTube Data API v3 không cung cấp share count trong pipeline hiện tại.
- Sentiment dùng lightweight Vietnamese rule-based fallback, phù hợp làm tín hiệu định hướng, không phải NLP benchmark đã validate bằng human labels.

## Câu Hỏi BI Chính

1. Nội dung nào hiệu quả nhất cho Highlands Coffee và các đối thủ trên YouTube?
2. Khán giả phản hồi ra sao qua phân bố sentiment trong bình luận?
3. Highlands đang đứng ở đâu so với đối thủ về reach, engagement, engagement rate và share of voice?

## KPI Chính

| KPI | Công thức | Ý nghĩa |
| --- | --- | --- |
| `engagement_count` | `likes + comments + shares + saves` | Tổng tương tác khả dụng |
| `engagement_rate` | `engagement_count / reach * 100` | Chuẩn hóa engagement theo quy mô views/reach |
| `virality_score` | `shares / reach * 100` | Thiết kế sẵn cho share data, hiện bằng 0 |
| `sentiment_ratio` | `positive_comments / total_comments * 100` | Tín hiệu sức khỏe cảm xúc qua comments |
| `share_of_voice` | `page reach / total scoped reach * 100` | Reach-based SOV trong official-channel scope |

## Kiến Trúc Hệ Thống

```text
YouTube Data API v3
        |
        v
Python ETL: extract -> raw JSONL -> normalize -> sentiment -> quality -> load
        |
        v
PostgreSQL Warehouse: social_dw
        |
        +--> Analytical Views -> dashboard/exports CSV/JSON
        |
        +--> Django API -> Next.js Web Dashboard
```

## Data Warehouse

Warehouse dùng star schema trong PostgreSQL:

| Loại | Bảng/View | Grain/Vai trò |
| --- | --- | --- |
| Dimension | `dim_time` | Thời gian phân tích theo ngày, giờ, tuần, tháng |
| Dimension | `dim_platform` | Platform lookup, final data là YouTube |
| Dimension | `dim_content_type` | Content type lookup |
| Dimension | `dim_page` | Brand/channel/competitor lookup |
| Fact | `fact_post` | Một YouTube video/post |
| Fact | `fact_sentiment` | Một comment đã phân loại sentiment |
| Audit | `etl_runs` | Lịch sử batch ETL và sync status |

7 analytical views phục vụ dashboard và exports:

| View | Mục đích |
| --- | --- |
| `vw_executive_overview` | KPI tổng quan |
| `vw_daily_engagement` | Time series reach/engagement |
| `vw_sentiment_trend` | Xu hướng sentiment |
| `vw_content_performance` | Hiệu suất theo content type |
| `vw_competitor_benchmark` | Benchmark giữa các thương hiệu |
| `vw_posting_time_heatmap` | Heatmap ngày/giờ đăng |
| `vw_viral_posts` | Top videos/posts |

## Backend API

Chạy Django API:

```powershell
python backend\manage.py runserver 127.0.0.1:8000
```

Endpoints chính:

```text
GET /health/
GET /api/v1/posts/
GET /api/v1/posts/{post_id}/
GET /api/v1/analytics/overview/
GET /api/v1/analytics/engagement/
GET /api/v1/analytics/sentiment/
GET /api/v1/analytics/top-posts/
GET /api/v1/analytics/content-performance/
GET /api/v1/analytics/heatmap/
GET /api/v1/analytics/competitors/
GET /api/v1/analytics/insights/
GET /api/v1/sync/status/
```

API trả dữ liệu từ PostgreSQL warehouse. Khi database lỗi, response được sanitize để không lộ connection string hoặc stack trace.

## Web Dashboard

Chạy dashboard:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Routes chính:

```text
http://localhost:3000/dashboard
http://localhost:3000/content
http://localhost:3000/sentiment
http://localhost:3000/competitors
http://localhost:3000/posts
http://localhost:3000/data-health
```

Dashboard screenshots đã được nhúng trực tiếp trong `Report Business Intelligence.pdf`. Các file ảnh screenshot sinh ra cục bộ không được track trong Git để giữ repository gọn.

## Cài Đặt Môi Trường

Tạo `.env` từ `.env.example`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
SOCIALENS_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_IDS=...
YOUTUBE_QUERIES=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Load `.env` trong PowerShell:

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
```

Cài Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Cài frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

## Vận Hành ETL

Chạy official-channel ETL khi có YouTube API key/quota:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
```

Chạy quality gate:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

Export warehouse views:

```powershell
python -m etl.cli export --database-url $env:DATABASE_URL
```

## Kiểm Thử

Kết quả kiểm thử cuối:

| Hạng mục | Lệnh | Kết quả |
| --- | --- | --- |
| Python regression + coverage | `python -m pytest -q` | 59 passed, 1 skipped, coverage 70.59% |
| Django config | `python backend\manage.py check` | Pass |
| Warehouse quality | `python -m etl.cli quality --database-url $env:DATABASE_URL` | 26 PASS, 17 INFO, 0 FAIL |
| Frontend tests | `npm test -- --runInBand` | 7 passed |
| Frontend build | `npm run build` | Pass |
| Frontend lint | `npm run lint` | Pass |
| Production audit | `npm audit --omit=dev --audit-level=moderate` | 0 vulnerabilities |

Optional live YouTube contract test:

```powershell
$env:RUN_YOUTUBE_LIVE_TESTS="1"
python -m pytest tests/test_youtube_live_contract.py -q
```

Test này được skip khi không có YouTube API key/quota.

## Insight Chính

- Highlands Coffee chiếm 96.24% reach-based share of voice trong tập official YouTube channels, nhưng engagement rate thấp hơn Trung Nguyên Legend.
- Trung Nguyên Legend là benchmark tốt nhất về cadence và comment coverage với 600/817 posts và 1,258/1,526 comments.
- Sentiment tổng thể an toàn: 351 positive, 1,148 neutral, 27 negative; tuy nhiên neutral chiếm đa số nên không nên diễn giải thành brand love mạnh.
- Posting heatmap nên được đọc theo cả volume và efficiency; slot có engagement rate cao nhưng sample quá nhỏ chỉ nên dùng làm giả thuyết thử nghiệm.
- Data quality là một kết quả quan trọng của dự án: batch query-search nhiễu đã bị loại, warehouse final đạt 0 FAIL.

## Hạn Chế

- Kết luận chỉ áp dụng cho YouTube official channels, không đại diện toàn bộ social footprint của ngành F&B.
- Không có unique reach, watch time, subscriber gain hoặc CTR vì pipeline dùng YouTube Data API v3, không dùng YouTube Analytics API nội bộ.
- `virality_score` chưa có giá trị phân tích vì thiếu share count.
- Sentiment là rule-based directional signal, chưa phải mô hình PhoBERT/ViSoBERT có validation set.
- Không có `.pbix` bắt buộc; dashboard web và báo cáo PDF là artifact trình bày chính trong bản nộp này.

## Cấu Trúc Repo

```text
backend/                 Django API
etl/                     Python ETL package and CLI
warehouse/schema/        PostgreSQL schema, indexes, views
warehouse/queries/       Validation and analytical SQL
frontend/                Next.js web dashboard
dashboard/exports/       CSV/JSON exports from warehouse views
data/processed/          Processed post/comment CSV snapshots
tests/                   Regression and contract tests
```

## License

Academic project for Business Intelligence coursework.
