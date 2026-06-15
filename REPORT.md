# BÁO CÁO CUỐI KỲ

## SocialLens BI - Hệ thống Business Intelligence phân tích mạng xã hội ngành F&B

**Dự án:** SocialLens BI - Hệ thống Business Intelligence phân tích hiệu quả truyền thông xã hội ngành F&B tại Việt Nam  
**Thương hiệu trọng tâm:** Highlands Coffee Vietnam  
**Nguồn dữ liệu vận hành:** YouTube Data API v3, PostgreSQL warehouse `social_dw`  
**Ngày snapshot báo cáo:** 2026-06-01, ảnh dashboard refresh ngày 2026-06-15  
**Phạm vi dashboard nộp:** PostgreSQL warehouse, SQL validation, CSV/JSON exports, Django API, Next.js web dashboard, screenshots

## Mục lục

1. Tóm tắt điều hành  
2. Chương 1 - Giới thiệu và mục tiêu  
3. Chương 2 - Phương pháp luận  
4. Chương 3 - Thu thập dữ liệu và ETL pipeline  
5. Chương 4 - Thiết kế Data Warehouse  
6. Chương 5 - Backend API và Web Dashboard  
7. Chương 6 - Kết quả phân tích và BI insights  
8. Chương 7 - Kiểm thử và đảm bảo chất lượng  
9. Chương 8 - Hạn chế và hướng phát triển  
10. Chương 9 - Kết luận  
11. Phụ lục  

## TÓM TẮT ĐIỀU HÀNH (Executive Summary)

SocialLens BI là một dự án Business Intelligence được xây dựng để trả lời một câu hỏi rất thực tế trong vận hành marketing ngành F&B: khi các thương hiệu liên tục đầu tư vào nội dung số, làm thế nào để chuyển các tín hiệu rời rạc trên mạng xã hội thành một hệ thống đo lường có cấu trúc, có thể kiểm định và đủ tin cậy để hỗ trợ ra quyết định? Nhóm chọn Highlands Coffee Vietnam làm thương hiệu trọng tâm và so sánh với một tập đối thủ trên YouTube gồm Trung Nguyên Legend, Phúc Long, Cộng Cà Phê, Cheese Coffee, KOI Thé Việt Nam, Gong Cha Vietnam và Starbucks Việt Nam.

Phiên bản cuối của dự án chủ động thu hẹp phạm vi từ ý tưởng đa nền tảng ban đầu xuống YouTube official-channel only. Đây không phải là sự cắt giảm tùy tiện. Trong quá trình triển khai, nhóm nhận thấy Facebook Graph API có rủi ro lớn về quyền truy cập, App Review và tính ổn định trong môi trường capstone. Dữ liệu query-search rộng cũng tạo ra nhiều nhiễu: batch query bị loại có 502 trang không chính thức mới và 98,76% reach không đến từ official pages. Thay vì cố giữ khối lượng dữ liệu lớn nhưng khó bảo vệ, nhóm quyết định ưu tiên chất lượng, tính truy vết và khả năng giải thích. Vì vậy, nguồn sự thật cuối cùng là PostgreSQL warehouse schema `social_dw`, chỉ chứa dữ liệu YouTube từ các kênh chính thức đã được duyệt.

Snapshot cuối ghi nhận 817 video/posts trong giai đoạn từ 2017-09-26 đến 2026-05-26, với 1.526 comments đã phân loại sentiment. Tổng reach/views proxy đạt 167.066.949, tổng engagement đạt 48.325, engagement rate trung bình đạt 1,9164%. Quality gate của warehouse có 43 dòng kiểm định, trong đó 26 PASS, 17 INFO và 0 FAIL. Các kiểm tra trọng yếu như duplicate natural keys, orphan facts, metric âm, generated KPI reconciliation, sentiment label validity, YouTube-only scope và approved official-channel scope đều đạt.

Về kết quả kinh doanh, Highlands Coffee đang chiếm ưu thế tuyệt đối về reach/views với 160,78 triệu views proxy và 96,24% reach-based share of voice trong tập dữ liệu. Tuy nhiên, Trung Nguyên Legend lại là thương hiệu có nhịp đăng và lượng tương tác nổi bật nhất: 600/817 video, 35.836 engagement và 1.258/1.526 comments. Điều này cho thấy Highlands mạnh về nhận diện ở các video có tính phủ rộng, còn Trung Nguyên Legend là benchmark đáng chú ý về cadence, storytelling và khả năng tạo thảo luận.

Hệ thống được triển khai theo kiến trúc batch analytics: Python ETL lấy dữ liệu từ YouTube Data API v3, lưu raw JSONL, chuẩn hóa, phân loại sentiment, kiểm định chất lượng, nạp vào PostgreSQL warehouse, sau đó phục vụ Django API, Next.js web dashboard và exports CSV/JSON. Dashboard web là evidence chính trong bản nộp này; Power BI Desktop được xem là hướng trình bày thủ công tùy chọn, vì môi trường hiện tại không tự động sinh `.pbix`. Các ảnh minh họa dashboard đã được refresh và lưu tại `dashboard/screenshots/`.

## CHƯƠNG 1 - GIỚI THIỆU VÀ MỤC TIÊU

### 1.1. Bối cảnh nghiên cứu

Ngành F&B tại Việt Nam là một thị trường có mật độ cạnh tranh cao, chu kỳ campaign ngắn và phụ thuộc mạnh vào cảm nhận thương hiệu. Những thương hiệu như Highlands Coffee, Phúc Long, Cộng Cà Phê hay Trung Nguyên Legend không chỉ cạnh tranh bằng số lượng cửa hàng, giá bán hoặc sản phẩm mới. Họ còn cạnh tranh bằng khả năng giữ sự hiện diện trong tâm trí khách hàng: câu chuyện thương hiệu, mùa vụ, ưu đãi, hình ảnh không gian, cảm xúc cộng đồng và các video campaign được lan truyền trên nền tảng số.

Trong thực tế, social media analytics thường bị chia nhỏ thành các báo cáo từng kênh, từng chiến dịch, từng file CSV hoặc từng dashboard nền tảng. Cách làm này đủ để xem nhanh một vài chỉ số, nhưng chưa đủ để trả lời các câu hỏi BI có tính so sánh: thương hiệu nào đang chiếm ưu thế về reach, thương hiệu nào tạo thảo luận tốt hơn, nội dung nào chuyển views thành engagement, sentiment có rủi ro xấu không, và dữ liệu có đủ sạch để đưa vào báo cáo quản trị hay không. SocialLens BI được xây dựng để biến những câu hỏi đó thành một workflow phân tích có cấu trúc.

Mục tiêu đầu tiên của dự án là xây dựng một pipeline dữ liệu có thể vận hành được từ nguồn thật. Đây là tiêu chí quan trọng, vì một dashboard đẹp nhưng dựa trên mock data sẽ không phản ánh được khó khăn cốt lõi của BI: dữ liệu thực thường thiếu trường, lệch định dạng, giới hạn API, trùng khóa, không đồng nhất timezone và có nhiễu từ nguồn không chính thức. Bản cuối của SocialLens BI dùng YouTube Data API v3 và PostgreSQL làm nguồn sự thật, không dùng static JSON hoặc sample data trong runtime dashboard.

Mục tiêu thứ hai là thiết kế một kho dữ liệu phù hợp cho phân tích. Thay vì để dashboard đọc trực tiếp file raw hoặc gọi API mạng xã hội mỗi lần mở trang, nhóm xây dựng schema `social_dw` theo mô hình sao. Facts lưu hiệu suất video và sentiment comment; dimensions chuẩn hóa thời gian, nền tảng, loại nội dung và trang/kênh. Tầng analytical views biến dữ liệu chi tiết thành các dataset sẵn sàng cho dashboard, API và export.

Mục tiêu thứ ba là tạo ra insight có giá trị kinh doanh. Dự án không dừng ở việc đếm số bài đăng. Báo cáo cần chỉ ra điều gì có thể hành động được: Highlands có reach lớn nhưng engagement chưa tương xứng; Trung Nguyên Legend là benchmark tốt về nhịp nội dung; sentiment tổng thể an toàn nhưng chủ yếu neutral; heatmap thời điểm đăng cần được đọc theo volume và theo engagement rate; một số thương hiệu có mẫu comment quá nhỏ nên không nên diễn giải sentiment sâu.

### 1.2. Câu hỏi kinh doanh (Business Questions)

Dự án được chốt quanh ba câu hỏi kinh doanh chính. Các câu hỏi này đủ cụ thể để chuyển thành KPI, view và dashboard page, nhưng vẫn đủ rộng để dẫn đến đề xuất quản trị nội dung:

1. **Nội dung nào hiệu quả?** Loại video, thông điệp, thời điểm đăng và nhóm nội dung nào đang tạo engagement tốt nhất cho Highlands Coffee và các đối thủ?
2. **Khán giả đang phản hồi ra sao?** Sentiment trong bình luận có xu hướng tích cực, trung tính hay tiêu cực; có dấu hiệu rủi ro nào đủ lớn để cần theo dõi không?
3. **Highlands đang ở đâu so với đối thủ?** Share of voice, engagement rate, post volume và comment coverage của Highlands khác gì so với Trung Nguyên Legend, Phúc Long, Cộng Cà Phê và các thương hiệu còn lại?

Từ ba câu hỏi trên, dashboard triển khai các câu hỏi vận hành cụ thể hơn: reach/views, engagement, engagement rate và share of voice kể câu chuyện gì khác nhau; video nào tạo tương tác nổi bật; khung giờ đăng nào nên thử nghiệm tiếp; và dữ liệu có đủ sạch, đủ truy vết để dùng trong báo cáo cuối kỳ hay không.

### 1.3. KPI được chọn và lý do

Các KPI được chọn xoay quanh bốn nhóm: hiệu quả nhận diện, hiệu quả tương tác, sức khỏe sentiment và vị thế cạnh tranh. `reach` trong báo cáo này là proxy từ YouTube views/impressions, không phải unique reach. `share_of_voice` là reach-based trong tập kênh chính thức, không phải mention-based trên toàn thị trường. Việc ghi rõ định nghĩa này là bắt buộc, vì cùng một tên KPI có thể mang ý nghĩa khác nhau tùy nguồn dữ liệu.

| KPI | Công thức | Lý do chọn | Ghi chú phạm vi |
| --- | --- | --- | --- |
| `engagement_count` | `likes + comments + shares + saves` | Đo tổng tương tác khả dụng ở mức video | Với YouTube final data, `shares` và `saves` không có nên bằng 0 |
| `engagement_rate` | `engagement_count / reach * 100` | Chuẩn hóa tương tác theo quy mô reach/views | Dùng để so sánh giữa kênh lớn và nhỏ |
| `virality_score` | `shares / reach * 100` | Đo khả năng lan truyền nếu có share data | Bằng 0 trong snapshot vì YouTube API không expose share count |
| `sentiment_ratio` | `positive_comments / total_comments * 100` | Theo dõi sức khỏe cảm xúc qua bình luận | Chỉ đọc sâu khi sample comment đủ lớn |
| `share_of_voice` | `page reach / total scoped reach * 100` | Đo vị thế cạnh tranh trong tập official channels | Là reach-based SOV, không phải mention-based SOV toàn thị trường |

### 1.4. Phạm vi và giới hạn có chủ đích

Phạm vi cuối của dự án là YouTube official channels của 8 thương hiệu F&B, dữ liệu trong giai đoạn 2017-09-26 đến 2026-05-26. Phạm vi này loại Facebook, TikTok, Instagram và earned media vì các nguồn đó hoặc có rủi ro quyền API, hoặc chưa có cơ chế xác minh official source đủ chắc trong thời gian capstone. The Coffee House cũng không được đưa vào warehouse sạch vì chưa xác định được official YouTube channel ID đáng tin cậy.

Đây là giới hạn có chủ đích, không phải thiếu sót bị che giấu. Dự án ưu tiên một pipeline nhỏ hơn nhưng sạch, có natural key, có quality gate và có thể giải thích. Với BI, một benchmark ít nguồn nhưng đúng định nghĩa thường đáng tin hơn một dashboard nhiều nguồn nhưng trộn lẫn official content, user-generated content và dữ liệu search nhiễu.

## CHƯƠNG 2 - PHƯƠNG PHÁP LUẬN

### 2.1. Dimensional Modeling - Lý thuyết Kimball

Business Intelligence không chỉ là trực quan hóa. Một hệ thống BI tốt phải trả lời được ba tầng câu hỏi. Tầng đầu tiên là "đã xảy ra điều gì": số bài đăng, số views, số engagement, sentiment distribution. Tầng thứ hai là "vì sao đáng chú ý": reach cao nhưng engagement thấp, content volume lớn nhưng share of voice nhỏ, sentiment neutral áp đảo positive. Tầng thứ ba là "nên làm gì tiếp": tách KPI awareness và engagement, thử nghiệm khung giờ, ưu tiên CTA để tăng positive comments, không mở rộng nguồn dữ liệu khi chưa kiểm soát source confidence.

Nhóm chọn cách tiếp cận warehouse-first. Tức là dữ liệu sau khi extract không đi thẳng lên dashboard, mà đi qua một tầng chuẩn hóa và kiểm định. Cách này có thêm chi phí thiết kế ban đầu, nhưng đổi lại báo cáo cuối có thể bảo vệ được nguồn số liệu. Khi dashboard nói tổng post là 817, con số đó không phải kết quả tạm thời của một API call, mà là số đã nằm trong fact table, đã qua quality gate và đã reconcile với analytical view.

Về lý thuyết, mô hình Kimball nhấn mạnh việc tổ chức dữ liệu quanh các business process và thiết kế theo grain rõ ràng. Trong dự án này, business process chính là hoạt động đăng video và phản hồi comment trên official YouTube channels. Từ đó, nhóm xác định hai fact table:

- `fact_post`: grain là một video/post trên một platform.
- `fact_sentiment`: grain là một comment đã được phân tích sentiment.

Các dimension được thiết kế để phục vụ slicing/dicing: `dim_time` cho phân tích theo ngày, giờ, tuần, tháng; `dim_platform` cho nền tảng; `dim_content_type` cho loại nội dung; `dim_page` cho thương hiệu/đối thủ. Cách thiết kế này phù hợp với BI hơn một bảng phẳng duy nhất, vì dashboard thường cần so sánh theo page, theo thời gian, theo content type và theo competitor flag.

Một điểm quan trọng của dimensional modeling là grain phải được giữ nhất quán. Nếu `fact_post` là một video, thì các metric như reach, likes, comments, engagement_count cần được hiểu ở mức video. Nếu `fact_sentiment` là một comment, thì sentiment ratio không nên lưu trực tiếp ở fact comment mà nên được aggregate lên view. Thiết kế trong `social_dw` đi theo nguyên tắc đó.

### 2.2. ETL Pipeline - Khái niệm và ứng dụng

ETL trong dự án được hiểu là Extract - Transform - Load theo đúng nghĩa thực thi. Extract gọi YouTube Data API v3 và lưu raw JSONL để giữ bằng chứng nguồn. Transform chuẩn hóa payload, quy đổi timestamp, map content type, tính sentiment và tạo bảng processed CSV. Load nạp dữ liệu vào PostgreSQL bằng upsert, đảm bảo batch có thể chạy lại mà không tạo duplicate rows.

Điểm khác biệt giữa bài tập ETL toy và ETL thực tế nằm ở những thứ không đẹp: API bị quota, comment bị 403, channel chính thức khó xác minh, query-search trả về dữ liệu nhiễu, timestamp cần timezone, metric thiếu cần quy ước, và sample fallback có thể vô tình làm báo cáo sai. Vì vậy nhóm chọn fail rõ khi production config/API không khả dụng, thay vì tự động thay bằng sample data. Đó là một quyết định thiên về tính đúng đắn của BI.

### 2.3. Sentiment Analysis trong NLP tiếng Việt

Sentiment analysis là một bài toán NLP khó hơn so với việc đếm likes hoặc views. Với tiếng Việt, thách thức tăng lên vì từ lóng, thiếu dấu, code-switching, emoji, sarcasm và ngữ cảnh sản phẩm. Thiết kế lý tưởng có thể dùng PhoBERT hoặc một mô hình transformer đã fine-tune trên dữ liệu sentiment tiếng Việt. Tuy nhiên, trong phạm vi capstone, nhóm chọn lightweight Vietnamese rule fallback.

Quyết định này có trade-off rõ. Ưu điểm là triển khai nhẹ, chạy ổn định, không cần tải mô hình lớn, phù hợp môi trường demo và CI. Nhược điểm là độ chính xác không thể so với mô hình được huấn luyện và đánh giá trên tập gán nhãn thủ công. Vì vậy, báo cáo không diễn giải sentiment như một kết luận tuyệt đối về cảm xúc khách hàng. Nó được dùng như directional signal: negative có cao bất thường không, positive ratio thay đổi ra sao, brand nào có mẫu comment đủ lớn để đọc xu hướng.

### 2.4. Quyết định thiết kế tổng thể

Thiết kế ban đầu có định hướng rộng hơn, bao gồm nhiều nền tảng và một backend đầy đủ hơn. Nhưng khi triển khai, nhóm quyết định thu hẹp. Đây là một bài học quan trọng của data engineering: phạm vi rộng không đồng nghĩa với hệ thống tốt hơn. Nếu dữ liệu Facebook chưa có quyền API ổn định, nếu The Coffee House chưa xác định được official channel ID đáng tin cậy, nếu query-search đưa dữ liệu không chính thức vào warehouse, thì mở rộng sẽ làm giảm chất lượng insight.

Vì vậy, bản final chọn YouTube official channels làm phạm vi sạch. Một dataset nhỏ hơn nhưng có nguồn rõ ràng, khóa tự nhiên sạch và quality gate pass có giá trị hơn một dataset lớn nhưng không giải thích được nguồn gốc.

## CHƯƠNG 3 - THU THẬP DỮ LIỆU VÀ ETL PIPELINE

### 3.1. Nguồn dữ liệu và chiến lược khai thác

Nguồn dữ liệu chính của SocialLens BI là YouTube Data API v3. Phạm vi active pages gồm 8 kênh chính thức:

| Kênh | Vai trò trong báo cáo |
| --- | --- |
| Highlands Coffee Vietnam | Thương hiệu trọng tâm |
| Trung Nguyên Legend | Đối thủ/benchmark chính về volume và engagement |
| Phúc Long | Đối thủ F&B |
| Cộng Cà Phê | Đối thủ F&B |
| Cheese Coffee | Đối thủ F&B |
| KOI Thé Việt Nam | Đối thủ F&B |
| Gong Cha Vietnam | Đối thủ F&B |
| Starbucks Việt Nam | Đối thủ F&B |

The Coffee House không có mặt trong warehouse cuối vì nhóm chưa xác định được official YouTube channel ID đủ tin cậy. Đây là một giới hạn, nhưng là giới hạn có chủ đích. Trong BI, một dòng dữ liệu không đáng tin có thể làm sai toàn bộ diễn giải, đặc biệt khi dùng share of voice hoặc competitor benchmark.

### 3.1.1. Chiến lược extract official channel

Pipeline sử dụng chuỗi YouTube API:

```text
channels.list -> uploads playlist -> playlistItems.list -> videos.list
```

Cách này tốt hơn search query vì nó bắt đầu từ kênh chính thức. Query-search có thể tìm được nhiều video liên quan đến thương hiệu, nhưng trong số đó có review, reaction, re-upload, video tin tức, video của KOL hoặc nội dung không thuộc quyền kiểm soát của thương hiệu. Những dữ liệu đó có thể hữu ích cho social listening mở rộng, nhưng không phù hợp làm nguồn sự thật cho dashboard official-channel performance.

Chi tiết về quyết định loại batch query-search được trình bày riêng ở mục 3.6, vì đây là một quyết định data quality quan trọng của dự án.

### 3.2. Raw Data Storage

Dữ liệu raw được lưu dưới dạng JSONL trong `data/raw/`. Raw storage có hai vai trò. Thứ nhất, nó cho phép audit: khi một record có metric bất thường, nhóm có thể quay lại payload nguồn. Thứ hai, nó tách extract khỏi transform: nếu cần điều chỉnh logic normalize hoặc sentiment, có thể dùng lại raw data mà không nhất thiết gọi API lại ngay.

Raw data không được dùng trực tiếp cho dashboard. Nó là lớp bằng chứng nguồn, phục vụ audit và tái xử lý. Cách làm này đặc biệt quan trọng với API bên ngoài vì dữ liệu có thể thay đổi theo thời gian, comment có thể bị xóa và quota không cho phép gọi lại vô hạn.

### 3.3. Transform - Làm sạch và chuẩn hóa

Sau extract, payload được chuẩn hóa thành hai nhóm dữ liệu processed:

- `data/processed/posts.csv`
- `data/processed/comments.csv`

Các trường thời gian được parse và quy đổi sang báo cáo theo Asia/Ho_Chi_Minh. Các trường metric như views, likes, comments được ép kiểu số và xử lý missing theo semantics API. Content type được chuẩn hóa; với dữ liệu final, toàn bộ active content là YouTube video. Các chỉ số dẫn xuất như `engagement_count`, `engagement_rate` và `virality_score` được thống nhất công thức ở tầng warehouse để API, export và dashboard không tự tính lệch nhau.

### 3.4. Sentiment Analysis Pipeline

Comment được phân loại sentiment thành `positive`, `neutral`, `negative`, kèm sentiment score. Luồng xử lý gồm lấy comment từ YouTube API, làm sạch text ở mức tối thiểu, áp rule-based Vietnamese sentiment fallback, sau đó nạp kết quả vào `fact_sentiment`. Output sentiment có vai trò bổ sung ngữ cảnh cho dashboard, không được xem là mô hình NLP benchmark.

Pipeline cũng ghi nhận các giới hạn vận hành của YouTube comment fetch. Một số video có thể không trả comment vì bị tắt bình luận, giới hạn quyền truy cập hoặc trả lỗi 403. Những trường hợp này không được xem là blocker nếu post metadata vẫn hợp lệ; chúng được phản ánh gián tiếp qua comment coverage thấp.

### 3.5. Deduplication và Upsert

Một yêu cầu cơ bản của batch ETL là chạy lại không được nhân đôi dữ liệu. Dự án xử lý điều này bằng natural key:

- Posts deduplicate theo `(platform_id, external_post_id)`.
- Comments deduplicate theo `(platform_id, external_comment_id)`.
- Pages deduplicate theo `(platform_id, external_page_id)` khi có source ID, hoặc `(platform_id, page_name)` trong tình huống cần fallback.

Loader dùng upsert vào PostgreSQL thay vì blind insert. Nhờ đó, cùng một batch có thể refresh metadata hoặc cập nhật comment mới mà không phá vỡ fact table. SQL validation cuối xác nhận duplicate post natural keys và duplicate comment natural keys đều bằng 0.

### 3.6. Quyết định loại query-search batch

Batch query-search từng được thử nghiệm để mở rộng độ phủ ngoài official channels. Sau kiểm tra, batch này bị loại khỏi warehouse chính: cleanup ngày 2026-06-01 đã xóa 59 lower-confidence query residual posts, 166 comments gắn với các post đó và 41 orphan pages. Vấn đề lớn nhất là 98,76% reach trong batch này không đến từ official pages, nên nếu giữ lại sẽ làm sai định nghĩa của share of voice và competitor benchmark.

Quyết định loại batch query-search thể hiện nguyên tắc ưu tiên data quality hơn data volume. Những dữ liệu này có thể hữu ích cho bài toán social listening hoặc earned media trong tương lai, nhưng không phù hợp với dashboard official-channel performance hiện tại. Vì vậy chúng được archive dưới `data/processed_archive/official_cleanup_20260601_233646/` thay vì nạp vào `social_dw`.

### 3.7. Batch vận hành

Lệnh batch production được chuẩn hóa như sau:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```

Dự án hiện không realtime. Dashboard đọc dữ liệu thật từ warehouse, nhưng warehouse chỉ thay đổi khi chạy batch ETL/load/export. Điều này phù hợp với bài toán BI capstone: mục tiêu là refresh định kỳ, kiểm định chất lượng và báo cáo theo snapshot, không phải streaming analytics.

## CHƯƠNG 4 - THIẾT KẾ DATA WAREHOUSE

### 4.1. Star Schema - Tổng quan schema `social_dw`

Warehouse `social_dw` được thiết kế theo star schema. Đây là lựa chọn hợp lý cho dashboard BI vì phần lớn câu hỏi phân tích là aggregate theo dimension: theo ngày, theo page, theo platform, theo content type, theo competitor flag. Thiết kế này cũng làm rõ ranh giới giữa raw/processed data và data mart phục vụ báo cáo.

Sơ đồ logic có thể mô tả bằng text:

```text
dim_time         dim_platform        dim_content_type       dim_page
   |                  |                    |                   |
   +------------------+--------------------+-------------------+
                              |
                          fact_post
                              |
                       fact_sentiment
```

`fact_post` là fact trung tâm cho hiệu suất video. `fact_sentiment` nối về `fact_post` để phân tích bình luận theo video, page và thời gian.

### 4.2. Fact Tables

`fact_post` có grain một video/post. Các trường chính gồm external post ID, platform, time, content type, page, caption, URL, reach, impressions, likes, comments, shares, saves. Các KPI như `engagement_count`, `engagement_rate`, `virality_score` được generated trong PostgreSQL. Việc để PostgreSQL sinh KPI giúp toàn bộ API, export và dashboard dùng cùng công thức, tránh lệch logic giữa frontend và backend.

`fact_sentiment` có grain một comment. Bảng lưu external comment ID, post ID, platform, time, sentiment label, sentiment score và comment text. Bảng này không trực tiếp lưu `sentiment_ratio`, vì ratio là aggregate theo post/page/date, được tính ở analytical views.

### 4.3. Dimension Tables

`dim_time` lưu các thuộc tính thời gian: `full_date`, `full_timestamp`, `hour_of_day`, `day_of_week`, `day_name`, `week_of_year`, `month_of_year`, `quarter_of_year`, `calendar_year`, `is_weekend`. Tầng này giúp heatmap và time-series không phải parse timestamp lại ở dashboard.

`dim_platform` chuẩn hóa nền tảng. Bản final chỉ có fact rows YouTube, nhưng bảng vẫn giữ thiết kế mở để sau này có thể thêm Facebook, TikTok hoặc Instagram nếu quyền API ổn định.

`dim_content_type` chuẩn hóa định dạng nội dung. Trong snapshot final, content active là YouTube video. Việc vẫn có dimension riêng giúp thiết kế không bị khóa cứng vào YouTube nếu mở rộng.

`dim_page` lưu thông tin thương hiệu/kênh: external page ID, page name, industry, country code, competitor flag và follower_count nếu có. Đây là dimension quan trọng nhất cho competitor benchmarking.

### 4.4. KPI Definitions trong warehouse

Các KPI cuối được định nghĩa như sau:

| KPI | Công thức | Ghi chú |
| --- | --- | --- |
| `engagement_count` | `likes + comments + shares + saves` | Tổng tương tác khả dụng |
| `engagement_rate` | `engagement_count / reach * 100` | `reach` là views/impressions proxy |
| `virality_score` | `shares / reach * 100` | Bằng 0 trong snapshot vì YouTube không cung cấp share count |
| `sentiment_ratio` | `positive_comments / total_comments * 100` | Chỉ đọc sâu khi mẫu comment đủ lớn |
| `share_of_voice` | `page reach / total scoped reach * 100` | Reach-based SOV trong official-channel scope |

Điểm đáng chú ý là `share_of_voice` ở đây không phải mention-based SOV trên toàn ngành. Nó trả lời câu hỏi hẹp hơn: trong tập official YouTube channels đã duyệt, thương hiệu nào chiếm phần lớn views proxy.

### 4.5. Analytical Views - 7 views phục vụ Dashboard

Bảy final views phục vụ dashboard và exports:

| View | Vai trò |
| --- | --- |
| `vw_executive_overview` | Snapshot KPI tổng: posts, reach, engagement, average rates, date range |
| `vw_daily_engagement` | Time-series reach/engagement theo ngày và platform |
| `vw_sentiment_trend` | Sentiment theo ngày, platform và page |
| `vw_content_performance` | Hiệu suất theo content type và competitor flag |
| `vw_competitor_benchmark` | Benchmark page/brand, SOV, engagement, sentiment |
| `vw_posting_time_heatmap` | Hiệu suất theo thứ và giờ đăng |
| `vw_viral_posts` | Danh sách video/top posts theo virality và engagement |

Các view này làm dashboard nhẹ hơn. Frontend và API không cần viết lại logic aggregate phức tạp; chúng đọc dữ liệu đã được chuẩn bị ở warehouse.

### 4.6. ETL Run Logging

Warehouse có bảng `etl_runs` để ghi lại lịch sử vận hành pipeline. Mỗi run lưu `source`, `started_at`, `finished_at`, `status`, số posts/comments extract và load, cùng `error_message` nếu có lỗi. Bảng này phục vụ audit trail và endpoint `GET /api/v1/sync/status/`, giúp dashboard hiển thị freshness thay vì chỉ hiển thị biểu đồ tách rời khỏi trạng thái dữ liệu.

Ở snapshot cuối, latest sync status được ghi nhận từ nguồn `maintenance:official-only-cleanup`, phản ánh quyết định khóa dữ liệu theo official-channel scope. Đây là bằng chứng vận hành quan trọng: không chỉ có dữ liệu trong fact tables, mà còn có metadata giải thích batch cuối cùng đã làm gì.

### 4.7. Quality Gate - 43 validation rows

Validation cuối có 43 rows: 26 PASS, 17 INFO, 0 FAIL. Các row INFO dùng để hiển thị count và snapshot; các row PASS kiểm định điều kiện bắt buộc. Một vài kiểm tra quan trọng:

- Duplicate post natural keys: 0.
- Duplicate comment natural keys: 0.
- Orphan sentiments: 0.
- Invalid sentiment labels: 0.
- Sentiment scores ngoài [-1, 1]: 0.
- Non-YouTube fact rows: 0.
- Non-approved official channel fact rows: 0.
- `vw_executive_overview` reconciles to `fact_post`: PASS.

Đây là phần nhóm xem như điều kiện "khóa số liệu" trước khi viết báo cáo. Nếu quality gate fail, dashboard vẫn có thể hiển thị, nhưng báo cáo không nên dùng.

## CHƯƠNG 5 - BACKEND API VÀ WEB DASHBOARD

### 5.1. Django API - Vai trò và thiết kế

Django API đóng vai trò lớp phục vụ dữ liệu cho dashboard. Thay vì để Next.js kết nối thẳng PostgreSQL hoặc đọc CSV, API cung cấp một contract JSON ổn định. Điều này có ba lợi ích. Thứ nhất, frontend không cần biết schema vật lý của warehouse. Thứ hai, lỗi warehouse có thể được sanitize trước khi trả về client. Thứ ba, cùng một API có thể phục vụ web dashboard, smoke test và demo.

Backend dùng lightweight `JsonResponse`, không dùng Django REST Framework. Nếu đây là sản phẩm production dài hạn, DRF có thể hữu ích cho serializer, pagination, schema generation và auth. Tuy nhiên, trong phạm vi capstone, nhóm cần một API nhỏ, rõ, dễ kiểm thử, chủ yếu đọc analytical views. Vì vậy, `JsonResponse` là lựa chọn thực dụng. Quyết định này giảm độ phức tạp mà không làm thay đổi data contract cuối.

### 5.2. Endpoint design

Các endpoint chính:

| Endpoint | Mục đích | Nguồn dữ liệu chính |
| --- | --- | --- |
| `GET /health/` | Health check cho API | Runtime status |
| `GET /api/v1/posts/` | Danh sách posts có phân trang/limit | `fact_post` + dimensions |
| `GET /api/v1/posts/{post_id}/` | Chi tiết một post/video | `fact_post` |
| `GET /api/v1/analytics/overview/` | KPI tổng quan | `vw_executive_overview` |
| `GET /api/v1/analytics/engagement/` | Time-series engagement | `vw_daily_engagement` |
| `GET /api/v1/analytics/sentiment/` | Sentiment trend | `vw_sentiment_trend` |
| `GET /api/v1/analytics/top-posts/` | Top posts/videos | `vw_viral_posts` |
| `GET /api/v1/analytics/content-performance/` | Content performance | `vw_content_performance` |
| `GET /api/v1/analytics/heatmap/` | Posting time heatmap | `vw_posting_time_heatmap` |
| `GET /api/v1/analytics/competitors/` | Competitor benchmark | `vw_competitor_benchmark` |
| `GET /api/v1/analytics/insights/` | Tóm tắt insight và freshness metadata | Analytical views + sync metadata |
| `GET /api/v1/sync/status/` | Trạng thái warehouse và ETL run gần nhất | `etl_runs` + fact counts |

Các endpoint time-series và posts có bounded `limit` để tránh payload quá lớn. Khi warehouse không khả dụng, API trả lỗi dạng `{detail, source_type, error_code}` thay vì để lộ connection string, host hoặc stack trace. Smoke test ngày 2026-06-15 xác nhận `/api/v1/analytics/overview/` trả `total_posts=817`, `total_reach=167066949`, `source=warehouse`.

### 5.3. Next.js web dashboard

Web dashboard dùng Next.js App Router. Các route chính:

- `/dashboard`: executive overview và time-series tổng quan.
- `/content`: phân tích hiệu suất nội dung.
- `/sentiment`: sentiment trend và phân bố cảm xúc.
- `/competitors`: benchmark giữa Highlands và đối thủ.
- `/posts`: bảng top posts/videos.
- `/data-health`: trạng thái sync, freshness và data quality.

Frontend gọi API qua `NEXT_PUBLIC_API_BASE_URL`. Static mock JSON đã được loại khỏi runtime; repo có test guard để đảm bảo frontend không import `frontend/src/data/*.json`. Dashboard có loading/error states và hỗ trợ nhãn song ngữ qua local i18n dictionary.

### 5.4. Dashboard evidence và Power BI optional

Ảnh dashboard đã được chụp lại từ web dashboard đang chạy với dữ liệu warehouse thật. Khi đưa vào Word hoặc file nộp, có thể chèn ảnh từ các đường dẫn sau:

| Trang | Đường dẫn ảnh |
| --- | --- |
| Executive dashboard | `dashboard/screenshots/dashboard.png` |
| Content performance | `dashboard/screenshots/content.png` |
| Sentiment analysis | `dashboard/screenshots/sentiment.png` |
| Competitor benchmarking | `dashboard/screenshots/competitors.png` |
| Posts/top videos | `dashboard/screenshots/posts.png` |
| Data health | `dashboard/screenshots/data-health.png` |

Trong bản nộp này, `.pbix` không được xem là bắt buộc. Power BI Desktop vẫn có thể dùng CSV/JSON exports hoặc kết nối trực tiếp PostgreSQL để tạo report thủ công, nhưng evidence chính là warehouse, SQL validation, API-backed web dashboard và screenshots đã refresh.

## CHƯƠNG 6 - KẾT QUẢ PHÂN TÍCH VÀ BI INSIGHTS

### 6.1. Tổng quan dữ liệu

Snapshot cuối có 817 video/posts, 1.526 sentiment comments, 8 official YouTube pages, dữ liệu trải dài từ 2017-09-26 đến 2026-05-26. Tổng reach/views proxy là 167.066.949, tổng engagement là 48.325, average engagement rate là 1,9164%. Đây không phải một dataset quá lớn nếu so với big data production, nhưng đủ tốt cho BI capstone vì nó có độ dài lịch sử gần 9 năm, có đủ thương hiệu để so sánh và đã qua quality gate.

Một điểm cần nhấn mạnh: toàn bộ active content row là YouTube video. Vì vậy, các kết luận trong báo cáo này không áp dụng cho image, story, reel Facebook hay short-form TikTok. Dự án phân tích official YouTube channel performance, không phân tích toàn bộ social media footprint.

### 6.2. Insight 1: Bất cân xứng nghiêm trọng trong tập dữ liệu

Tập dữ liệu không cân bằng giữa các thương hiệu. Trung Nguyên Legend có 600/817 posts, tương đương 73,44% số video, và 1.258/1.526 comments, tương đương 82,44% comment sentiment. Highlands Coffee có 123 posts, chiếm khoảng 15,06% số video. Các thương hiệu còn lại có volume nhỏ hơn nhiều: Phúc Long 35 posts, Cộng Cà Phê 31 posts, Cheese Coffee 22 posts, KOI Thé 3 posts, Gong Cha 2 posts và Starbucks Việt Nam 1 post.

Mất cân bằng này không làm dataset vô dụng, nhưng nó quyết định cách đọc kết quả. Các chỉ số tuyệt đối như post count, total engagement và total comments sẽ nghiêng mạnh về Trung Nguyên. Các thương hiệu có sample quá nhỏ không nên được xếp hạng sentiment sâu. Vì vậy, báo cáo ưu tiên rate, share, confidence caveat và benchmark theo từng bối cảnh thay vì chỉ so sánh tổng số.

### 6.3. Insight 2: Engagement rate không tỷ lệ thuận với quy mô reach

Highlands Coffee Vietnam có 123 video nhưng tạo ra 160.778.238 reach/views proxy, tương đương 96,24% reach-based share of voice trong tập official channels. Con số này rất lớn. Nó cho thấy các video của Highlands, nhiều khả năng bao gồm TVC/campaign awareness, có sức phủ vượt xa phần còn lại của dataset.

Tuy nhiên, engagement của Highlands chỉ là 10.339, thấp hơn nhiều so với Trung Nguyên Legend ở mức 35.836. Average engagement rate của Highlands là 0,6512%, trong khi Trung Nguyên Legend đạt 2,2837%. Điều này không có nghĩa Highlands làm kém. Nó cho thấy Highlands và Trung Nguyên đang thắng ở hai kiểu KPI khác nhau. Highlands thắng ở awareness, Trung Nguyên thắng ở nhịp tương tác và comment volume.

Với quản trị marketing, đây là một insight quan trọng. Nếu chỉ nhìn views, Highlands vượt trội tuyệt đối. Nếu nhìn engagement, câu chuyện đổi chiều. Vì vậy, nhóm đề xuất tách dashboard và báo cáo thành hai lớp KPI: awareness KPI cho video phủ rộng, và engagement KPI cho nội dung cần đối thoại. Một TVC đạt hàng chục triệu views không nên bị đánh giá bằng cùng tiêu chuẩn engagement rate với một video cộng đồng có reach nhỏ hơn.

### 6.4. Insight 3: Share of Voice cần đọc đúng định nghĩa

Trong phạm vi official YouTube channels, Highlands Coffee chiếm 96,24% reach-based share of voice. Trung Nguyên Legend đứng sau với 3,46%, các thương hiệu còn lại cộng lại dưới 1%. Nếu chỉ xem biểu đồ SOV, Highlands có vẻ áp đảo hoàn toàn.

Tuy nhiên, SOV ở đây là SOV theo views proxy, không phải SOV theo số lượng nhắc đến trên toàn thị trường. Nó không bao gồm Facebook, TikTok, KOL content, báo chí, user-generated content hoặc bình luận ngoài official channels. Vì vậy, insight đúng là: trong tập video YouTube official đã duyệt, Highlands có sức phủ rất lớn; không nên diễn giải thành "Highlands chiếm 96,24% toàn bộ thảo luận F&B".

### 6.5. Insight 4: Trung Nguyên Legend là benchmark tốt nhất về cadence và thảo luận

Trung Nguyên Legend có 600/817 video, tương đương khoảng 73,44% số post trong warehouse. Kênh này cũng có 1.258/1.526 comments, tức khoảng 82,44% comment sentiment. Đây là brand duy nhất trong tập dữ liệu vừa có volume lớn, vừa có comment coverage đủ tốt để đọc sentiment và engagement pattern.

Các video top engagement cũng nghiêng mạnh về Trung Nguyên Legend. Video "The Tao of Coffee - Cà Phê Đạo | Bản Full VietSub" đạt 4.532 engagement; "VŨ TRỤ TỈNH THỨC | TRUNG NGUYÊN LEGEND | OFFICIAL MV" đạt 4.053 engagement; một số video mùa vụ như G7 Gold Tết cũng có engagement rate cao. Nội dung của Trung Nguyên có xu hướng gắn với văn hóa cà phê, narrative thương hiệu và thông điệp tinh thần, không chỉ giới thiệu sản phẩm.

Với Highlands, điều đáng học không nhất thiết là copy concept của Trung Nguyên. Điểm đáng học là cấu trúc nội dung có chiều sâu hơn: storytelling, campaign có chủ đề rõ, nội dung mùa vụ và lời kêu gọi tương tác. Highlands có lợi thế reach; nếu kết hợp được reach đó với format kích hoạt thảo luận tốt hơn, hiệu quả tổng thể sẽ mạnh hơn.

### 6.6. Insight 5: Virality Score = 0% là hạn chế dữ liệu

`virality_score` được định nghĩa là `shares / reach * 100`, nhưng YouTube Data API v3 không cung cấp share count trong response chuẩn mà pipeline đang dùng. Vì vậy, toàn bộ snapshot có average virality score bằng 0,0000%. Đây không phải bằng chứng rằng video không được chia sẻ; nó chỉ cho biết dữ liệu share không tồn tại trong nguồn hiện tại.

Trong báo cáo, virality score nên được giữ như một KPI có định nghĩa nhưng phải gắn caveat rõ. Việc giữ metric này vẫn có ích về mặt thiết kế vì schema và dashboard đã sẵn sàng nếu sau này có nguồn share/referral đáng tin, ví dụ YouTube Analytics API với quyền sở hữu kênh hoặc social listening tool bên thứ ba. Ở phiên bản hiện tại, không nên dùng virality score để xếp hạng nội dung.

### 6.7. Insight 6: Sentiment an toàn nhưng chưa thật sự tích cực

Tổng cộng có 1.526 comments được phân loại sentiment, gồm 351 positive, 1.148 neutral và 27 negative. Positive ratio là 23,00%, negative ratio là 1,77%. Ở góc độ risk monitoring, đây là tín hiệu khá an toàn. Negative không cao và không cho thấy khủng hoảng sentiment trong snapshot.

Nhưng ở góc độ brand health, tỷ lệ neutral quá lớn cũng cho thấy phần lớn bình luận chưa thể hiện cảm xúc tích cực mạnh. Người xem có thể chỉ bình luận thông tin, tag bạn bè, hỏi đáp hoặc phản hồi ngắn. Với một thương hiệu F&B, nơi trải nghiệm cảm xúc và thói quen tiêu dùng đóng vai trò quan trọng, mục tiêu không chỉ là giảm negative mà còn là tăng positive comments.

Highlands có sentiment ratio 28,75%, cao hơn Trung Nguyên Legend 22,02%, nhưng Highlands chỉ có 240 comments. Cộng Cà Phê có sentiment ratio 33,33% nhưng chỉ 12 comments. KOI Thé có 0 comments, Gong Cha 4 comments, Starbucks 1 comment. Vì vậy, báo cáo không nên xếp hạng sentiment sâu cho các brand mẫu nhỏ. Cách đọc đúng là: sentiment tổng thể an toàn; Highlands và Trung Nguyên đủ dữ liệu hơn để theo dõi; các brand nhỏ cần thêm dữ liệu trước khi kết luận.

### 6.8. Insight 7: Video reach cao và video engagement cao không phải cùng một nhóm

Các video top engagement trong export gồm:

| Video | Page | Engagement | Engagement rate |
| --- | --- | ---: | ---: |
| The Tao of Coffee - Cà Phê Đạo | Trung Nguyên Legend | 4.532 | 1,8160% |
| VŨ TRỤ TỈNH THỨC | Trung Nguyên Legend | 4.053 | 0,7345% |
| HIGHLANDS COFFEE X HUỲNH LẬP | Highlands Coffee Vietnam | 4.006 | 1,4513% |
| Cà phê G7 Gold | Trung Nguyên Legend | 2.183 | 3,0674% |
| Bloomberg: Trung Nguyên Legend's Vision | Trung Nguyên Legend | 1.541 | 0,8875% |

Trong khi đó, một số video reach rất cao của Highlands đạt hàng chục triệu views proxy nhưng engagement rate rất thấp. Đây là hiện tượng thường gặp với video awareness hoặc paid/boosted content: mẫu số reach quá lớn làm engagement rate nhỏ, nhưng giá trị truyền thông vẫn có thể cao nếu mục tiêu là phủ nhận diện.

Điều này dẫn đến một khuyến nghị kỹ thuật cho dashboard: top posts không nên chỉ có một ranking. Nên có ít nhất hai góc nhìn: top by reach và top by engagement/engagement rate. Nếu chỉ dùng engagement rate, video reach nhỏ có thể đứng quá cao. Nếu chỉ dùng reach, video có tương tác cộng đồng tốt có thể bị che mất.

### 6.9. Insight 8: Posting Heatmap cần đọc theo cả volume và efficiency

`vw_posting_time_heatmap` có 122 ô ngày/giờ. Nếu xét tổng engagement, một số khung giờ nổi bật là Monday 10:00 với 5.010 engagement từ 19 posts, Wednesday 20:00 với 4.297 engagement từ 14 posts, Thursday 19:00 với 4.272 engagement từ 7 posts. Đây là các slot có volume đủ hơn và tổng engagement cao, đáng đưa vào danh sách thử nghiệm.

Nếu xét average engagement rate thuần túy, có các slot rất cao như Friday 23:00 đạt 6,5477%, nhưng chỉ từ 2 posts; Sunday 21:00 đạt 5,7554% nhưng chỉ 1 post. Những slot này thú vị nhưng không đủ chắc để biến thành quy tắc lịch đăng. Chúng phù hợp để tạo giả thuyết, không phù hợp để kết luận.

Vì vậy, lịch đăng nên được thử nghiệm trong 4-6 tuần theo từng brand/page, thay vì lấy heatmap hiện tại làm lịch cố định. Với Highlands, nhóm đề xuất ưu tiên các slot có cả volume và tổng engagement đáng kể như Monday 10:00, Wednesday 20:00 và Thursday 19:00/20:00, sau đó đo lại engagement rate và comment quality.

### 6.10. Insight 9: Chất lượng dữ liệu là một kết quả của dự án, không chỉ là bước phụ

Một điểm dễ bị bỏ qua trong báo cáo BI là data quality. Với SocialLens BI, chất lượng dữ liệu chính là một kết quả đáng trình bày. Batch query bị loại vì 98,76% reach không phải official pages. Warehouse sau cleanup giữ lại 817 posts và 1.526 comments chính thức. Quality validation có 0 FAIL. Frontend không còn fallback JSON. API và dashboard đọc từ PostgreSQL.

Điều này có giá trị thực tế. Nếu dashboard đưa ra insight "Highlands chiếm 96,24% share of voice", người đọc có thể hỏi: share of voice của tập nào? Nguồn có bị lẫn video không chính thức không? Có duplicate không? Có orphan comment không? Báo cáo có thể trả lời các câu hỏi đó bằng schema, validation SQL và cleanup evidence.

### 6.11. Dashboard và trực quan hóa insight

Dashboard được thiết kế theo hướng phục vụ người đọc nhanh nhưng vẫn giữ khả năng truy vết. Executive page hiển thị KPI tổng quan: total posts, total reach, total engagement, average engagement rate, date range và data source. Đây là trang dành cho quản lý cần nắm tình hình trong vài phút.

Content performance page tập trung vào câu hỏi định dạng/nội dung nào hiệu quả. Trong snapshot này, toàn bộ content là video, nên trang này chủ yếu so sánh brand chính và competitor group. Khi mở rộng đa nền tảng, view này có thể dùng để so sánh video, reel, image, story hoặc livestream.

Sentiment page hiển thị positive, neutral, negative theo thời gian và page. Vì sentiment là rule-based fallback, dashboard nên trình bày nó như tín hiệu định hướng. Các biểu đồ sentiment không nên được dùng như bằng chứng duy nhất để kết luận brand love hoặc customer satisfaction.

Competitors page là trang quan trọng nhất cho câu hỏi chiến lược. Nó cho thấy Highlands chiếm reach vượt trội nhưng Trung Nguyên chiếm volume và engagement. Chart phù hợp ở đây là bar chart cho share of voice, engagement, post count; bảng benchmark chi tiết cho page-level metrics.

Posts page cho phép xem các video cụ thể đứng đầu theo engagement/virality order. Đây là nơi chuyển từ KPI aggregate sang nội dung thật. Khi viết báo cáo hoặc đề xuất marketing, nhóm có thể lấy một vài video top engagement để phân tích format, thông điệp và context.

Data health page thể hiện nguồn dữ liệu, freshness, counts và sync status. Với một dự án BI, trang này rất quan trọng vì nó nói cho người xem biết dashboard có đang đọc dữ liệu thật hay không. Trong smoke test ngày 2026-06-15, API overview trả `source=warehouse`, `total_posts=817`; sync status đọc latest source `maintenance:official-only-cleanup`.

Các ảnh minh họa cần chèn thủ công vào báo cáo Word:

```text
dashboard/screenshots/dashboard.png
dashboard/screenshots/content.png
dashboard/screenshots/sentiment.png
dashboard/screenshots/competitors.png
dashboard/screenshots/posts.png
dashboard/screenshots/data-health.png
```

## CHƯƠNG 7 - KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG

### 7.1. Chiến lược kiểm thử đa tầng và warehouse validation

Warehouse validation là lớp quan trọng nhất. SQL validation trong `warehouse/queries/dashboard_validation.sql` kiểm tra cả count, khóa tự nhiên, quan hệ fact-dimension, domain values và KPI reconciliation. Kết quả cuối: 43 validation rows, 26 PASS, 17 INFO, 0 FAIL.

Các kiểm tra này bắt các lỗi mà dashboard rất khó phát hiện. Ví dụ, dashboard có thể vẫn hiển thị nếu có duplicate posts, nhưng total engagement sẽ bị phóng đại. Dashboard có thể vẫn vẽ sentiment nếu có orphan comments, nhưng benchmark theo page sẽ sai. Vì vậy, warehouse validation được chạy trước export và screenshot.

### 7.2. Python regression tests

Python tests kiểm tra ETL pipeline, extractors, normalization, quality checks, API endpoints, warehouse SQL và final delivery artifacts. Sau khi bổ sung coverage gate, `python -m pytest -q` đạt 59 passed, 1 skipped, total coverage 70,59%, vượt threshold 60%. Optional live YouTube test chỉ chạy khi có API key/quota.

Coverage không được hiểu là bảo đảm tuyệt đối, nhưng nó giúp phát hiện regression ở các phần lõi. Đặc biệt, tests API xác nhận response shape lightweight theo `SPEC.md`, tests final delivery xác nhận exports tồn tại và Data Dictionary ghi đủ final views.

### 7.3. Frontend tests, lint và build

Frontend có Jest/React Testing Library tests, lint bằng ESLint flat config và build Next.js. Kết quả hiện tại:

- `npm run lint`: pass.
- `npm test -- --runInBand`: 7 tests pass, coverage baseline pass.
- `npm run build`: pass.
- `npm audit --omit=dev --audit-level=moderate`: 0 vulnerabilities.

Ngoài ra, repo có static guard để đảm bảo frontend runtime không import mock JSON. Đây là test nhỏ nhưng quan trọng, vì một dashboard trông đúng nhưng đọc fallback data là lỗi nghiêm trọng trong BI.

### 7.4. API smoke test

API smoke test kiểm tra endpoint `/health/`, `/api/v1/analytics/overview/` và `/api/v1/sync/status/`. Khi bật project ngày 2026-06-15, API trả:

- Health: 200 OK.
- Overview: `total_posts=817`, `total_reach=167066949`, `source=warehouse`.
- Sync status: warehouse counts `posts=817`, `comments=1526`.

Các route dashboard `/dashboard`, `/content`, `/sentiment`, `/competitors`, `/posts`, `/data-health` đều trả 200.

## CHƯƠNG 8 - HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

### 8.1. YouTube-only Scope

Hạn chế lớn nhất là phạm vi YouTube-only. Kết luận trong báo cáo chỉ đại diện cho official YouTube channels, không đại diện cho toàn bộ social media performance của Highlands hoặc ngành F&B. Facebook, Instagram, TikTok, earned media, KOL content và website campaign data đều nằm ngoài snapshot hiện tại.

Hướng phát triển không nên đơn giản là "thêm mọi nguồn". Cách đúng là mở rộng có kiểm soát: mỗi nguồn mới cần source confidence, official/non-official flag, natural key rõ ràng và quality gate riêng. Nếu không, warehouse sẽ lặp lại vấn đề của query-search batch.

### 8.2. Reach là proxy

YouTube API trong pipeline cung cấp views/impressions proxy, không cung cấp unique reach theo nghĩa marketing platform. Vì vậy, báo cáo dùng từ `reach/views proxy`. Khi trình bày cho người không kỹ thuật, cần nói rõ "reach" ở dashboard là số lượt xem/proxy, không phải số người duy nhất.

Trong tương lai, nếu có quyền truy cập YouTube Analytics API hoặc dữ liệu nội bộ của brand, có thể bổ sung watch time, average view duration, subscriber gain, impressions click-through rate và unique viewers. Những chỉ số này sẽ làm dashboard YouTube sâu hơn nhiều so với views/likes/comments hiện tại.

### 8.3. Virality Score bằng 0

`virality_score = shares / reach * 100`, nhưng YouTube API hiện không expose share count trong pipeline. Vì vậy virality score trong snapshot cuối là 0,0000%. Đây là hạn chế dữ liệu, không phải kết luận rằng video không lan truyền. Báo cáo nên tránh diễn giải sâu chỉ số này cho đến khi có nguồn share/referral/share URL analytics đáng tin.

### 8.4. Sentiment rule-based

Sentiment hiện là lightweight Vietnamese rule fallback. Ưu điểm là nhẹ, ổn định, chạy được trong môi trường capstone. Nhược điểm là chưa đủ tốt để thay thế mô hình NLP tiếng Việt có đánh giá chuẩn. Hướng phát triển cụ thể là xây dựng một tập comment gán nhãn thủ công, fine-tune hoặc benchmark PhoBERT/ViSoBERT, sau đó so sánh precision/recall theo từng nhãn.

Ngoài sentiment polarity, dự án có thể thêm topic extraction: sản phẩm, giá, không gian, dịch vụ, khuyến mãi, delivery, trải nghiệm cửa hàng. Đây mới là tầng insight có giá trị cao cho F&B, vì negative sentiment chỉ hữu ích khi biết negative về điều gì.

### 8.5. Thiếu The Coffee House

The Coffee House không có trong warehouse sạch vì chưa xác định được official YouTube channel ID đủ tin cậy. Đây là một thiếu hụt trong competitor set, nhưng quyết định loại bỏ là hợp lý. Trong BI, một competitor sai nguồn có thể làm benchmark sai hơn là không có competitor đó.

Hướng phát triển là xác minh official channel qua website chính thức, social links hoặc tài liệu thương hiệu. Chỉ khi channel ID đủ tin cậy mới thêm vào `YOUTUBE_CHANNEL_IDS` và load vào warehouse.

### 8.6. Power BI `.pbix` là optional

Prompt thiết kế ban đầu xem Power BI là artifact dashboard chính. Trong bản nộp hiện tại, nhóm quyết định không bắt buộc `.pbix` vì việc tự động sinh file Power BI Desktop trong môi trường repo là không thực tế. Thay vào đó, gói evidence chính gồm PostgreSQL warehouse, SQL validation, CSV/JSON exports, API-backed web dashboard và screenshots. Power BI vẫn có thể được build thủ công từ `dashboard/exports/` hoặc kết nối PostgreSQL `social_dw`.

## CHƯƠNG 9 - KẾT LUẬN

### 9.1. Nhìn lại câu hỏi kinh doanh ban đầu

SocialLens BI đã trả lời được phần lớn câu hỏi ban đầu trong phạm vi đã chốt. Dự án xây dựng được một pipeline từ dữ liệu thật của YouTube official channels đến warehouse PostgreSQL, có quality gate, có API, có dashboard web và có exports phục vụ báo cáo. Quan trọng hơn, dự án không chỉ tạo dashboard mà còn tạo được một logic dữ liệu có thể bảo vệ: vì sao chọn nguồn này, vì sao loại nguồn kia, KPI được tính thế nào, dữ liệu có duplicate không, view có reconcile với fact không.

Về mặt kinh doanh, báo cáo chỉ ra một nghịch lý đáng chú ý: Highlands Coffee thắng rất lớn về reach/views, nhưng Trung Nguyên Legend lại mạnh hơn về volume nội dung, engagement và comment coverage. Điều này giúp tránh một kết luận đơn giản rằng thương hiệu có nhiều views nhất là thương hiệu làm social tốt nhất. Trong YouTube official-channel BI, awareness và engagement cần được đo bằng hai nhóm KPI khác nhau.

### 9.2. Giá trị học thuật và kỹ thuật của quá trình

Dự án cũng cho thấy vai trò của data engineering trong BI. Nếu không có official-channel extraction, deduplication, star schema, generated KPI, validation SQL và cleanup batch, dashboard sẽ dễ trở thành một lớp trình bày đẹp trên dữ liệu nhiễu. Nhóm đã chọn hướng ngược lại: dataset nhỏ hơn, nhưng sạch hơn và dễ giải thích hơn.

Về mặt học thuật, dự án chứng minh các khái niệm trong môn BI không tách rời triển khai thực tế. Grain của fact table quyết định cách aggregate; source confidence quyết định độ tin cậy của benchmark; quality gate quyết định số liệu có thể khóa hay chưa; và dashboard chỉ có giá trị khi người đọc hiểu được định nghĩa KPI phía sau.

### 9.3. Đề xuất tiếp theo nếu dự án tiếp tục

Những câu hỏi chưa trả lời được cũng rõ ràng. Dự án chưa đại diện cho toàn bộ social media vì thiếu Facebook/TikTok/Instagram. Sentiment chưa phải mô hình NLP mạnh. Virality score chưa có ý nghĩa vì thiếu share count. The Coffee House chưa được đưa vào benchmark. Nhưng các giới hạn này được ghi rõ, có lý do kỹ thuật và có hướng cải thiện cụ thể. Với phạm vi capstone, SocialLens BI đạt mục tiêu chính: xây dựng một hệ thống BI end-to-end từ dữ liệu thật, có kiểm định, có dashboard và có insight đủ sâu để hỗ trợ thảo luận chiến lược nội dung cho Highlands Coffee trong bối cảnh cạnh tranh F&B trên YouTube.

## PHỤ LỤC

### A. Data Dictionary rút gọn

| Bảng/View | Grain | Vai trò |
| --- | --- | --- |
| `dim_time` | Một timestamp báo cáo | Phân tích theo ngày, giờ, tuần, tháng |
| `dim_platform` | Một nền tảng | Chuẩn hóa platform, final data là YouTube |
| `dim_content_type` | Một loại nội dung | Chuẩn hóa video/reel/livestream/... |
| `dim_page` | Một official page/channel | Brand/competitor lookup |
| `fact_post` | Một video/post | Hiệu suất video: reach, engagement, KPI |
| `fact_sentiment` | Một comment | Sentiment label/score của comment |
| `vw_executive_overview` | Một snapshot | KPI tổng quan |
| `vw_daily_engagement` | Date + platform | Time-series engagement |
| `vw_sentiment_trend` | Date + platform + page | Sentiment trend |
| `vw_content_performance` | Platform + content type + competitor flag | Hiệu suất nội dung |
| `vw_competitor_benchmark` | Platform + page | Benchmark thương hiệu |
| `vw_posting_time_heatmap` | Day + hour + platform | Heatmap thời điểm đăng |
| `vw_viral_posts` | Một video/post | Top video/post table |

### B. Danh sách API endpoints

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

### C. Kết quả kiểm thử tổng hợp

| Hạng mục | Lệnh kiểm tra | Kết quả cuối |
| --- | --- | --- |
| Python tests + coverage | `python -m pytest -q` | 59 passed, 1 skipped, coverage 70,59% |
| Django configuration | `python backend\manage.py check` | Pass, no issues |
| Warehouse quality gate | `python -m etl.cli quality --database-url $env:DATABASE_URL` | 43 rows, 26 PASS, 17 INFO, 0 FAIL |
| Frontend tests | `npm test -- --runInBand` | 7 passed |
| Frontend production build | `npm run build` | Pass |
| Frontend lint | `npm run lint` | Pass |
| Production dependency audit | `npm audit --omit=dev --audit-level=moderate` | 0 vulnerabilities |
| API smoke | `/health/`, `/analytics/overview/`, `/sync/status/` | 200 OK, source=`warehouse` |

### D. Lệnh vận hành chính

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}

python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
python backend\manage.py runserver 127.0.0.1:8000
```

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

### E. Screenshot paths để chèn vào báo cáo Word

```text
dashboard/screenshots/dashboard.png
dashboard/screenshots/content.png
dashboard/screenshots/sentiment.png
dashboard/screenshots/competitors.png
dashboard/screenshots/posts.png
dashboard/screenshots/data-health.png
```

### F. Validation summary và snapshot dữ liệu cuối

| Hạng mục | Kết quả |
| --- | --- |
| Warehouse validation rows | 43 |
| PASS | 26 |
| INFO | 17 |
| FAIL | 0 |
| Fact posts | 817 |
| Fact sentiment comments | 1.526 |
| Active pages | 8 |
| Date range | 2017-09-26 đến 2026-05-26 |
| Total reach/views proxy | 167.066.949 |
| Total engagement | 48.325 |
| Average engagement rate | 1,9164% |
| Average virality score | 0,0000% |

### G. Ghi chú về phạm vi nộp

Bản nộp hiện tại không yêu cầu `.pbix`. Nếu cần Power BI, có thể build thủ công từ PostgreSQL `social_dw` hoặc từ `dashboard/exports/*.csv`. Gói bằng chứng chính gồm: source code, PostgreSQL warehouse, SQL validation, CSV/JSON exports, Django API, Next.js web dashboard và screenshots đã refresh.
