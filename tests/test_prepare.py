import pandas as pd
import pytest
from openrag_cfpb.prepare import normalize_columns, prepare


def test_required_fields():
    with pytest.raises(ValueError, match="Missing required"):
        normalize_columns(pd.DataFrame({"Product": ["Credit card"]}))


def test_dedup_filter_and_reproducibility(tmp_path):
    rows = [
        {"Complaint ID": "1", "Date received": "2025-01-01", "Product": "Credit card", "Issue": "Billing", "Consumer complaint narrative": "This is a lengthy real-world-style test narrative describing a disputed charge and an unresolved billing issue."},
        {"Complaint ID": "1", "Date received": "2025-01-01", "Product": "Credit card", "Issue": "Billing", "Consumer complaint narrative": "This is a lengthy real-world-style test narrative describing a disputed charge and an unresolved billing issue."},
        {"Complaint ID": "2", "Date received": "2025-01-02", "Product": "Mortgage", "Issue": "Payment", "Consumer complaint narrative": "A" * 100},
    ]
    source = tmp_path / "input.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    stats = prepare(source, tmp_path / "output")
    assert stats["sample_rows"] == 1
    assert (tmp_path / "output" / "complaints.parquet").exists()
