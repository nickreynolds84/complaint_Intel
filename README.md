# OpenRAG — CFPB Consumer Complaint Intelligence

**Milestone 1: real-data acquisition and profiling.** This repository is a starter, not yet a working RAG application.

## Data provenance

Use the CFPB's [official historical narrative archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/) for text. The current complaint database no longer includes narratives; don't substitute its newest export for the archive. The CFPB's [field reference](https://cfpb.github.io/api/ccdb/fields.html) describes structured metadata.

Download an archive export manually and extract the CSV (or supply a ZIP containing a CSV) to `data/raw/`. Start with a smaller historical export, rather than the full multi-year archive. The tool deliberately **does not silently download** an unspecified snapshot. Record the source URL and download date for provenance. Never commit raw consumer narratives without a separate privacy/redistribution review.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/prepare_data.py --input data/raw/complaints.csv --sample-size 25000
pytest -q
```

The command creates `data/processed/complaints.parquet` and `profile.json`. It filters to credit-card and checking/savings products, retains narratives of at least 80 characters, removes duplicate complaint IDs, and takes a deterministic sample. It handles the original CFPB export column names; inspect your archive's headers before running. No source data is included in this starter.

## Planned next steps

1. Verify archive schema, actual coverage, and missingness; improve streaming sampling for large archives.
2. Build DuckDB analytics and topic discovery.
3. Implement provider-agnostic RAG with citations and a benchmark harness.
4. Add Streamlit, Docker Compose, CI, and a reproducible demo corpus.

## Interpretation caveat

Complaints are consumer-reported, not independently verified, and do not represent a random sample. Do not treat raw complaint volume as a normalized company risk score.
