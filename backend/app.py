"""Flask entry point for the SweetStock backend."""

from backend.sweetstock import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
