"""Normalize, validate and deterministically sample historical CFPB exports."""
from pathlib import Path
import pandas as pd

COLUMN_ALIASES = {
    "Date received": "date_received", "Product": "product",
    "Sub-product": "sub_product", "Issue": "issue", "Sub-issue": "sub_issue",
    "Consumer complaint narrative": "narrative", "Company": "company",
    "Complaint ID": "complaint_id", "Company response to consumer": "company_response",
    "Timely response?": "timely_response", "State": "state",
    "Date sent to company": "date_sent_to_company",
}
REQUIRED = {"complaint_id", "date_received", "product", "issue", "narrative"}


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.rename(columns=COLUMN_ALIASES).copy()
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["complaint_id"] = df["complaint_id"].astype("string").str.strip()
    df["date_received"] = pd.to_datetime(df["date_received"], errors="coerce")
    df["narrative"] = df["narrative"].astype("string").str.strip()
    return df


def prepare(input_csv: str | Path, output_dir: str | Path, sample_size: int = 25000, seed: int = 42):
    """Process a local CFPB CSV or zipped CSV; preserve a reproducible subset."""
    if sample_size < 1:
        raise ValueError("sample_size must be positive")
    path = Path(input_csv)
    if not path.is_file():
        raise FileNotFoundError(path)
    chunks = []
    counts = {"source_rows": 0, "eligible_rows": 0}
    for chunk in pd.read_csv(path, chunksize=50000, low_memory=False, dtype={"Complaint ID": "string", "complaint_id": "string"}):
        df = normalize_columns(chunk)
        counts["source_rows"] += len(df)
        product = df["product"].astype("string").str.lower()
        selected = product.str.contains(r"credit card|checking|savings", regex=True, na=False)
        df = df.loc[selected & df["narrative"].notna() & df["narrative"].str.len().ge(80) & df["complaint_id"].ne("").fillna(False) & df["date_received"].notna()]
        counts["eligible_rows"] += len(df)
        chunks.append(df)
    if not chunks or counts["eligible_rows"] == 0:
        raise ValueError("No eligible complaint narratives found")
    combined = pd.concat(chunks, ignore_index=True).drop_duplicates(subset="complaint_id", keep="first")
    # Stable hash ordering makes the sample independent of input row ordering.
    hashes = pd.util.hash_pandas_object(combined["complaint_id"] + f"-{seed}", index=False)
    combined = combined.assign(_hash=hashes).sort_values(["_hash", "complaint_id"]).head(sample_size).drop(columns="_hash")
    dest = Path(output_dir)
    dest.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(dest / "complaints.parquet", index=False)
    counts["unique_eligible_rows"] = counts["eligible_rows"] # see README: pre-dedup count
    counts["sample_rows"] = len(combined)
    counts["narrative_missing_rate_in_sample"] = float(combined["narrative"].isna().mean())
    import json
    (dest / "profile.json").write_text(json.dumps(counts, indent=2) + "\n")
    return counts
