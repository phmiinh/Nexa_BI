# SocialLens BI Insights

Nguon du lieu: PostgreSQL warehouse `social_dw` va export moi trong `dashboard/exports/*.csv`.
Cap nhat luc 2026-05-31. Pham vi phan tich: 2017-09-26 den 2026-05-31.

## 1. Baseline dieu hanh

**Key finding:** Dataset official-channel moi da tang manh ve comment coverage va du tot cho dashboard BI, nhung van nen trinh bay la YouTube-only.

**Supporting data:**
- Warehouse hien co 876 videos/posts va 1,692 comments.
- Tong reach dat 167.40M, tong engagement dat 53.85K.
- Avg engagement rate dat 1.8806%.

**Recommended action:** Dung snapshot moi lam source of truth cho dashboard, Power BI va bao cao; ghi ro day la YouTube-only va sample/mock khong con la runtime data source.

## 2. Hieu qua noi dung

**Key finding:** Highlands van chi phoi reach, nhung Trung Nguyen Legend da co mau lon hon va dong gop phan lon engagement trong competitor set.

**Supporting data:**
- Highlands Coffee Vietnam co 123 posts, 160.78M reach va 10.34K engagement.
- Trung Nguyen Legend co 600 posts, 5.79M reach, 35.84K engagement va avg engagement rate 2.2837%.
- Top post theo engagement hien thuoc Trung Nguyen Legend voi 4,532 engagements.

**Recommended action:** Tach khuyen nghi theo muc tieu: Highlands phu hop awareness/reach, Trung Nguyen Legend phu hop benchmark ve volume, creative cadence va engagement.

## 3. Khung gio dang bai

**Key finding:** Heatmap sau batch official co nhieu mau hon, nhung van can doc theo brand vi Trung Nguyen chiem ty trong post lon.

**Supporting data:**
- Friday 07:00 co 4 posts va avg engagement rate 3.4456%.
- Saturday 07:00 co 5 posts, 175 total engagement va avg engagement rate 3.0822%.
- Thursday 20:00 co 7 posts, 1,145 total engagement va avg engagement rate 3.0207%.

**Recommended action:** Test lich dang trong 4-6 tuan cho Friday 07:00, Saturday 07:00 va Thursday 20:00; khi bao cao Power BI nen them slicer brand de tranh ket luan chung qua muc.

## 4. Sentiment va brand health

**Key finding:** Sentiment coverage da tang len muc dung duoc cho demo, nhung phan lon comment van neutral nen day la directional signal.

**Supporting data:**
- 1,692 comments duoc classify sentiment.
- 377 positive, 1,286 neutral, 29 negative.
- Positive ratio dat 22.28%, negative ratio dat 1.71%.

**Recommended action:** Theo doi negative ratio theo ngay va theo brand; uu tien CTA trong video de tang positive comments thay vi chi toi uu view.

## 5. Competitor va share of voice

**Key finding:** Official competitor set da tot hon ve so luong, nhung reach SOV van bi Highlands chi phoi manh.

**Supporting data:**
- Competitor group co 8 pages, 696 posts, 6.29M reach, 37.99K engagement va 1,286 comments.
- Non-competitor group co 41 pages, 180 posts, 161.11M reach va 15.86K engagement.
- Trung Nguyen Legend la competitor co mau tot nhat: 600 posts va 1,258 comments.

**Recommended action:** Bao cao SOV theo official brand pages; khong load broad curated query vao warehouse chinh vi probe query bi reject do 502 new non-official pages va 98.76% non-official reach.

## 6. Chat luong du lieu BI

**Key finding:** Lop warehouse sau batch official sach ve khoa tu nhien, quan he fact va KPI reconciliation.

**Supporting data:**
- Dashboard validation co 42 rows: 25 PASS, 17 INFO, 0 FAIL.
- `fact_post` co 876 rows, `fact_sentiment` co 1,692 rows.
- API/FE khong con static mock fallback; PostgreSQL la single source of truth.

**Recommended action:** Giu `python -m etl.cli quality --database-url $env:DATABASE_URL` la gate bat buoc truoc moi lan refresh exports va screenshot.
