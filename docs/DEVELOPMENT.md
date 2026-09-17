# Development

Initial bootstrap:

    python -m pip install -e ".[dev]"
    python -m pytest
    python -m ruff check .
    python -m mypy src

Development flow:

SPEC -> TEST -> IMPLEMENT -> VERIFY -> REVIEW -> RELEASE
