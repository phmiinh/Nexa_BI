# Final Technical Delivery Checklist

Use this checklist for the final SocialLens BI technical handoff.

## Environment

- [ ] `.env` exists locally and is not committed.
- [ ] `DATABASE_URL` points to the remote PostgreSQL database.
- [ ] `SOCIALENS_DATABASE_URL` points to the same remote warehouse for the Django API.
- [ ] `YOUTUBE_API_KEY` is set.
- [ ] `YOUTUBE_CHANNEL_IDS` and/or `YOUTUBE_QUERIES` are set for the final YouTube scope.
- [ ] `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` is set for the dashboard demo.

## Final ETL

- [ ] Ran real YouTube ETL with no sample fallback:

```powershell
python -m etl.cli run --sources youtube --no-sample-fallback --database-url $env:DATABASE_URL
```

- [ ] Confirmed the run did not use sample data.
- [ ] Confirmed PostgreSQL schema `social_dw` exists in the remote database.
- [ ] Confirmed final warehouse views exist.

## Quality and Exports

- [ ] Ran quality checks:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

- [ ] Exported dashboard views:

```powershell
python -m etl.cli export --database-url $env:DATABASE_URL
```

- [ ] Confirmed CSV and JSON files exist in `dashboard/exports/`.
- [ ] Spot-checked exported metrics against Power BI visuals.

## API and Web Dashboard

- [ ] Django check passes:

```powershell
python backend\manage.py check
```

- [ ] Django API is running at `http://localhost:8000`.
- [ ] Health endpoint returns successfully: `http://localhost:8000/health/`.
- [ ] Next.js dashboard builds successfully:

```powershell
cd frontend
npm run build
cd ..
```

- [ ] Dashboard demo is running at `http://localhost:3000/dashboard`.
- [ ] API-backed dashboard pages load without relying on static fallback data.

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

## Submission Evidence

- [ ] Terminal evidence for real YouTube ETL with `--no-sample-fallback`.
- [ ] Terminal evidence for quality checks.
- [ ] Refreshed files in `dashboard/exports/`.
- [ ] Power BI `.pbix` file.
- [ ] Dashboard screenshots.
- [ ] Final API URL: `http://localhost:8000`.
- [ ] Final dashboard URL: `http://localhost:3000/dashboard`.
- [ ] Final run guide reviewed: `GUIDE.md`.
- [ ] Power BI build specification reviewed: `dashboard/power_bi/README.md`.
