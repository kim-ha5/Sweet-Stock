"""Backend configuration and project file locations."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE = Path(os.environ.get("SWEETSTOCK_DATABASE", BASE_DIR / "bakery_management.db"))
SCHEMA_FILE = BASE_DIR / "schema.sql"
SEED_FILE = BASE_DIR / "insert_data.sql"
VALID_STATUSES = {"Pending", "In Progress", "Ready", "Completed", "Cancelled"}
