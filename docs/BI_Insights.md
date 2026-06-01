# SocialLens BI Insights

Nguon du lieu: PostgreSQL warehouse `social_dw` va export moi trong `dashboard/exports/*.csv`.
Cap nhat luc 2026-06-01. Pham vi phan tich: 2017-09-26 den 2026-05-26.

## 1. Baseline dieu hanh

**Key finding:** Dataset official-channel da du tot cho dashboard BI F&B, voi Highlands Coffee chi phoi reach va Trung Nguyen Legend chi phoi volume post/comment.

**Supporting data:**
- Warehouse hien co 817 videos/posts va 1,526 comments.
- Tong reach/views proxy dat 167.07M, tong engagement dat 48.33K.
- Avg engagement rate dat 1.9164%.
- Active BI views chi con 8 official pages sau cleanup ngay 2026-06-01.

**Recommended action:** Dung snapshot official-channel nay lam source of truth cho dashboard, Power BI va bao cao. Ghi ro day la YouTube-only va sample/mock khong con la runtime data source.

## 2. Hieu qua noi dung

**Key finding:** Highlands tao awareness lon nhat, trong khi Trung Nguyen Legend co mau noi dung rong hon va dong gop phan lon engagement trong competitor set.

**Supporting data:**
- Highlands Coffee Vietnam co 123 posts, 160.78M reach/views proxy va 10.34K engagement.
- Trung Nguyen Legend co 600 posts, 5.79M reach/views proxy, 35.84K engagement va 1,258 comments.
- Phuc Long, Cong Caphe va Cheese Coffee co volume nho hon nhung van du de dung trong benchmark official-channel.

**Recommended action:** Tach khuyen nghi theo muc tieu: Highlands phu hop awareness/reach, Trung Nguyen Legend phu hop benchmark ve cadence, creative pattern va engagement.

## 3. Khung gio dang bai

**Key finding:** Heatmap sau cleanup official-only co mau sach hon, nhung van can doc theo brand vi Trung Nguyen Legend chiem ty trong post lon.

**Supporting data:**
- `vw_posting_time_heatmap` co 122 cells.
- Dataset co 568 ngay/platform rows trong `vw_daily_engagement`.
- Moi active content row deu la YouTube video; khong nen ket luan ve image/story/reel trong MVP nay.

**Recommended action:** Trong Power BI, them slicer brand/page cho heatmap. Thu nghiem khung gio top trong 4-6 tuan truoc khi chuyen thanh lich dang mac dinh.

## 4. Sentiment va brand health

**Key finding:** Sentiment coverage du dung cho demo BI, nhung nen xem la directional signal vi pipeline dang dung lightweight Vietnamese rule fallback.

**Supporting data:**
- 1,526 comments duoc classify sentiment.
- 351 positive, 1,148 neutral, 27 negative.
- Positive ratio dat 23.00%, negative ratio dat 1.77%.

**Recommended action:** Theo doi negative ratio theo ngay va theo brand; uu tien CTA trong video de tang positive comments thay vi chi toi uu view.

## 5. Competitor va share of voice

**Key finding:** Sau cleanup, benchmark chi con official pages nen share of voice de giai thich hon, nhung SOV van la reach/views share thay vi mention share.

**Supporting data:**
- Active competitor/brand pages: 8.
- Trung Nguyen Legend la competitor co mau tot nhat: 600 posts va 1,258 comments.
- Highlands Coffee Vietnam co reach/views proxy lon nhat: 160.78M.

**Recommended action:** Bao cao SOV la reach-based share of voice. Khong load broad curated query vao warehouse chinh vi probe query bi reject do 502 new non-official pages va 98.76% non-official reach.

## 6. Chat luong du lieu BI

**Key finding:** Lop warehouse sau cleanup official-only sach ve khoa tu nhien, quan he fact va KPI reconciliation.

**Supporting data:**
- Dashboard validation co 43 rows: 26 PASS, 17 INFO, 0 FAIL.
- `fact_post` co 817 rows, `fact_sentiment` co 1,526 rows.
- `vw_competitor_benchmark` co 8 pages, khop active official-channel scope.
- API/FE khong con static mock fallback; PostgreSQL la single source of truth.

**Recommended action:** Giu `python -m etl.cli quality --database-url $env:DATABASE_URL` la gate bat buoc truoc moi lan refresh exports va screenshot.
