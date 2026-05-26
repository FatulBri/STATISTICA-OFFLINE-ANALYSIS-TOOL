"""Lightweight dataset schema diagnostics (no full analysis pipeline)."""
import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("diagnostics")


def run_file_diagnostics(input_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """Load file and return column/schema summary only."""
    from data_manager import DataManager

    dm = DataManager(input_path)
    dm.load_data(sheet_name)
    return dm.get_summary_stats()


def emit_diagnostics_json(input_path: str, sheet_name: Optional[str] = None) -> None:
    """Print machine-readable marker for Node.js bridge."""
    summary = run_file_diagnostics(input_path, sheet_name)
    print(f"DIAGNOSTICS|{json.dumps(summary, ensure_ascii=False)}")
