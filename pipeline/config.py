"""Shared settings. The Gemini API key is read from the .env file in this folder
(never commit .env: it's in .gitignore), or from the GEMINI_API_KEY environment variable."""
import os, pathlib

_env = pathlib.Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "models/gemini-embedding-2"
STORE_DISPLAY_NAME = "p02-knowledge-base"
STORE_FILE = ".store_name"      # setup_store.py writes the store name here
STALE_AFTER_MONTHS = 12
