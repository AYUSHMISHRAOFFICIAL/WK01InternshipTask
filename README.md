# AIOrbit Companies Module Dataset

This pipeline extracts, cleans, deduplicates, verifies, enriches, qualifies, and generates descriptions for AI-focused companies, producing a final dataset of 1,000+ companies.

## Setup

1. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill in API keys
3. Add `credentials.json` for Google Sheets.

## Execution

Before running the pipeline, you can supply bulk candidate datasets by downloading them locally and placing them into `data/raw/external/`.

- **Epoch AI Companies**: Download from `https://epoch.ai/data/ai-companies-documentation/downloads` and place as `data/raw/external/epoch_ai.csv`
- **World Bank AI Startup Dataset**: Check `https://www.worldbank.org/` and place as `data/raw/external/world_bank_ai.csv`
- **Webclaw startup dataset**: Download from `https://webclaw.io/data/startups` and place as `data/raw/external/webclaw.csv`

The pipeline will automatically ingest, map, and process them as raw candidates while preserving data provenance.

Run the pipeline:
`python run.py`
