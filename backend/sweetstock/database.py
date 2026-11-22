"""SQLite connection and initialization helpers."""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_database() -> sqlite3.Connection:
    """Return the request-scoped SQLite connection."""
    if "database" not in g:
        database = sqlite3.connect(current_app.config["DATABASE"])
        database.row_factory = sqlite3.Row
        database.execute("PRAGMA foreign_keys = ON")
        g.database = database
    return g.database


def close_database() -> None:
    """Close the request-scoped SQLite connection, if one was opened."""
    database = g.pop("database", None)
    if database is not None:
        database.close()


def initialize_database(
    database: sqlite3.Connection,
    schema_file: Path,
    seed_file: Path,
) -> None:
    """Create tables and load seed data, excluding SQL test selects."""
    database.executescript(_sqlite_script(schema_file))
    seed = _sqlite_script(seed_file).split("-- Testing", 1)[0]
    database.executescript(seed)


def _sqlite_script(path: Path) -> str:
    """Remove SQLite CLI-only directives before executing a script."""
    return "\n".join(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith(".")
    )
