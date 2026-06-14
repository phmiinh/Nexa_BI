# Final Technical Delivery Checklist

Use this checklist for the final SocialLens BI technical handoff.

## Environment

- [x] `.env` exists locally and is not committed.
- [x] `DATABASE_URL` points to the remote PostgreSQL database.
- [x] `SOCIALENS_DATABASE_URL` points to the same remote warehouse for the Django API.
- [x] `YOUTUBE_API_KEY` is set.
- [x] `YOUTUBE_CHANNEL_IDS` is set for the final official-channel YouTube scope.
- [x] `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` is set for the dashboard demo.

## Final ETL

- [x] Ran real YouTube ETL:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
```

- [x] Confirmed the run did not use sample data.
- [x] Confirmed PostgreSQL schema `social_dw` exists in the remote database.
- [x] Confirmed final warehouse views exist.

Note: `etl_probe_extra_official` failed with YouTube `403 Forbidden` and is treated as an
out-of-scope probe. The accepted final scope is the 8 approved official YouTube channels
documented in `SPEC.md` and `STATUS.md`.

## Quality and Exports

- [x] Ran quality checks:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

- [x] Exported dashboard views:

```powershell
python -m etl.cli export --database-url $env:DATABASE_URL
```

- [x] Confirmed CSV and JSON files exist in `dashboard/exports/`.
- [ ] Spot-checked exported metrics against Power BI visuals.

## API and Web Dashboard

- [x] Django check passes:

```powershell
python backend\manage.py check
```

- [ ] Django API is running at `http://localhost:8000`.
- [ ] Health endpoint returns successfully: `http://localhost:8000/health/`.
- [x] Next.js dashboard builds successfully:

```powershell
cd frontend
npm run build
npm test
cd ..
```

- [ ] Dashboard demo is running at `http://localhost:3000/dashboard`.
- [x] API-backed dashboard pages load from PostgreSQL with no static fallback data.
- [ ] Optional live YouTube contract test passes when quota/key are available:

```powershell
$env:RUN_YOUTUBE_LIVE_TESTS="1"
python -m pytest tests/test_youtube_live_contract.py -q
```

## Power BI

- [ ] Power BI connects to remote PostgreSQL database `nexabi`.
- [ ] Power BI uses schema `social_dw`.
- [ ] Report includes the required pages:
  - [ ] Executive Overview
  - [ ] Content Performance
  - [ ] Sentiment Analysis
  - [ ] Competitor Benchmarking
  - [ ] Posting Time Heatmap
- [ ] Slicers work for date, platform, brand, and content type where available.
- [ ] `.pbix` is saved under `dashboard/power_bi/`.
- [ ] Screenshots are saved under `dashboard/screenshots/`.

Power BI Desktop is required for the final `.pbix`; this environment cannot generate a
valid report file automatically. Existing screenshots are web-dashboard evidence and should
be refreshed after the final Power BI report is built.

## Submission Evidence

- [x] Terminal evidence for successful real YouTube ETL.
- [x] Terminal evidence for quality checks.
- [x] Refreshed files in `dashboard/exports/`.
- [ ] Power BI `.pbix` file.
- [ ] Refreshed dashboard screenshots after final Power BI/web dashboard review.
- [ ] Final API URL: `http://localhost:8000`.
- [ ] Final dashboard URL: `http://localhost:3000/dashboard`.
- [x] Final run guide reviewed: `GUIDE.md`.
- [x] Power BI build specification reviewed: `dashboard/power_bi/README.md`.
