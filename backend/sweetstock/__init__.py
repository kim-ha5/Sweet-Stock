"""SweetStock application setup."""

import sqlite3

from flask import Flask, jsonify

from .config import DATABASE, SEED_FILE, SCHEMA_FILE
from .database import close_database as close_database_connection
from .database import get_database, initialize_database
from .routes import register_routes


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the SweetStock Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(DATABASE),
        SECRET_KEY="sweetstock-local-development-key",
    )
    if test_config:
        app.config.update(test_config)

    @app.teardown_appcontext
    def close_database(_: BaseException | None) -> None:
        close_database_connection()

    @app.errorhandler(sqlite3.IntegrityError)
    def handle_integrity_error(error: sqlite3.IntegrityError):
        return jsonify(error="That change violates a database rule"), 409

    @app.errorhandler(sqlite3.Error)
    def handle_database_error(error: sqlite3.Error):
        return jsonify(error="The database could not complete that operation"), 500

    register_routes(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Recreate the schema and load the sample data."""
        database = get_database()
        initialize_database(database, SCHEMA_FILE, SEED_FILE)
        database.commit()
        print(f"Initialized {app.config['DATABASE']}")

    return app
