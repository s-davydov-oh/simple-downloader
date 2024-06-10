from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DELAY: float | tuple[float, float] | None = (1.1, 3.1)
MAX_REDIRECTS = 3
TIMEOUT: tuple[float, float] = (3.03, 42)  # connect and read timeout.
