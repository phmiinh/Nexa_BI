# SocialLens BI Notebooks

These notebooks are the BI analysis layer for the final report. Run them after `make demo`
or after `python -m etl.cli run --sources sample --output-dir data/processed`.

Required notebook plan:

1. `01_data_quality_overview.ipynb` - missing values, duplicates, metric ranges.
2. `02_kpi_baseline.ipynb` - canonical KPI calculations and baseline tables.
3. `03_content_performance_analysis.ipynb` - top/bottom posts and content type performance.
4. `04_posting_time_heatmap.ipynb` - weekday/hour heatmap and posting windows.
5. `05_sentiment_brand_health.ipynb` - sentiment trend and negative spike review.
6. `06_share_of_voice_competitor.ipynb` - brand vs competitor share of voice.
7. `07_executive_insights.ipynb` - final insight summaries for report/slides.

Each notebook should end with insight bullets in this format:

- Key finding
- Supporting data
- Recommended action
