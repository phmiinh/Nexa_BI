# SocialLens BI Insights

Nguon du lieu: export YouTube hien tai trong `dashboard/exports/*.csv` va `data/processed/*.csv`, cap nhat luc 2026-05-24. Pham vi phan tich: 2023-01-01 den 2026-05-19.

## 1. Baseline dieu hanh

**Key finding:** YouTube da co baseline du dung cho dashboard dieu hanh, nhung engagement rate trung binh con thap so voi muc can co de tao tang truong huu co.

**Supporting data:**
- 65 posts/video trong giai doan 2023-01-01 den 2026-05-19.
- Tong reach dat 6.24M va tong engagement dat 1.15K.
- Avg engagement rate tu export dieu hanh la 0.7435%.

**Recommended action:** Dung baseline nay lam moc sau moi lan refresh; uu tien muc tieu tang engagement rate truoc khi mo rong them kenh hoac tang tan suat dang.

## 2. Hieu qua noi dung

**Key finding:** Hieu qua noi dung dang bi chi phoi boi mot so video reach lon, trong khi noi dung Highlands co tin hieu engagement rate tot o mot vai video san pham.

**Supporting data:**
- Top video toan tap dat 9,736 reach va 319 engagements.
- Video Highlands tot nhat la "KHOE SAC THANG HUONG - TRA SEN VANG" voi 9,736 reach va 3.2765% engagement rate.
- Nhom non-competitor trong export co 40 video, 6.22M reach va 1.10K engagements.

**Recommended action:** Tach benchmark giua owned brand va creator/industry video; voi Highlands, nhan rong motif san pham/co CTA cua cac video co engagement rate cao.

## 3. Khung gio dang bai

**Key finding:** Khung gio co engagement rate cao nhat khac voi khung gio tao tong engagement cao nhat, nen can tach muc tieu "chat luong tuong tac" va "volume tuong tac".

**Supporting data:**
- Wednesday 12:00 dat 3.2765% engagement rate va 319 engagements.
- Thursday 09:00 tao 261 engagements tu 1 post.
- Saturday 22:00 dat 1.9496% engagement rate va 48 engagements.

**Recommended action:** Chay test lich dang 4 tuan: Wednesday noon cho ca muc tieu volume va engagement rate, dong thoi thu them Thursday morning; chi ket luan sau khi moi slot co them du mau.

## 4. Sentiment va brand health

**Key finding:** Sentiment hien nghieng manh ve neutral; negative thap nhung co mot diem can xu ly rieng ve trai nghiem cua hang.

**Supporting data:**
- 15 comments, gom 3 positive, 11 neutral va 1 negative.
- Positive ratio dat 20.00%; negative ratio dat 6.67%.
- Negative spike xuat hien ngay 2026-04-27 tren Highlands Coffee Vietnam voi 1 negative comment.

**Recommended action:** Tang cau hoi mo va CTA trong caption/video de keo positive comments; dong thoi phan hoi comment negative ngay 2026-04-27 va ghi nhan van de van hanh neu lien quan o cam/trai nghiem tai quan.

## 5. Competitor va share of voice

**Key finding:** Highlands dan dau share of voice theo reach trong tap du lieu hien tai, nhung engagement SOV van thap hon nhieu so voi reach SOV.

**Supporting data:**
- Highlands Coffee Vietnam co 25 posts va 6.20M reach.
- Highlands reach SOV dat 99.40% va engagement SOV dat 82.02%.
- Nhom competitor flag co 25 posts nhung chi 12.57K reach va 50 engagements.

**Recommended action:** Khong danh gia doi thu chi bang so luong post; can theo doi engagement SOV rieng cho owned brand, competitor chinh va creator/industry de co benchmark canh tranh dung hon.

## 6. Chat luong du lieu BI

**Key finding:** Lop du lieu processed/export hien du sach de dung cho dashboard va notebook, nhung can tiep tuc kiem tra missing value sau moi lan ETL.

**Supporting data:**
- 0 duplicate post natural keys va 0 duplicate comment natural keys.
- 0 metric am trong cac cot reach, impressions, likes, comments, shares, engagement rate va virality score.
- Processed layer co 65 posts, 15 comments va 11 page names.

**Recommended action:** Giu data quality notebook la buoc bat buoc truoc khi cong bo report; neu refresh moi co duplicate, metric am hoac sentiment label khong hop le thi dung cap nhat dashboard cho den khi ETL duoc sua.
