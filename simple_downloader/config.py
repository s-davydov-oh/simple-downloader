from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SAVE_FOLDER_NAME = "saves"
DELAY: float | tuple[float, float] | None = (1.1, 3.1)
MAX_REDIRECTS = 3
TIMEOUT: tuple[float, float] = (3.03, 42)  # connect and read timeout.
TOTAL_RETRIES = 5
RETRY_STRATEGY = {"multiplier": 10, "min": 10, "max": 160}  # (2 ^ attempt - 1) * mult.
CHUNK_MULTIPLIER = 8
SUPPORTED_EXTENSIONS = frozenset({})
