from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DISABLE_CLI_MESSAGES: bool = False

SAVE_FOLDER_NAME = "saves"
SUCCESS = "[+]"
INFO = "[!]"
FAILURE = "[-]"
UNKNOWN = "[?]"

DEFAULT_DELAY: float | tuple[float, float] | None = (1.1, 3.1)
DEFAULT_TIMEOUT: float | tuple[float, float] | None = (3.03, 42)  # connect and read timeout
MAX_REDIRECTS = 3
TOTAL_RETRIES = 5
RETRY_STRATEGY = {"multiplier": 10, "min": 10, "max": 160}  # (2 ^ attempt - 1) * mult

DEFAULT_ALBUM_NAME = "unknown album"

BASE_CHUNK: int = 1024
DEFAULT_CHUNK_MULTIPLIER: int = 8
BAR_FORMAT = f"{SUCCESS} " + "{desc} {percentage:3.0f}% [{bar:20}] {n_fmt}/{total_fmt} | {rate_fmt}"

SUPPORTED_EXTENSIONS = frozenset(
    {
        ".mp4",
        ".mov",
        ".m4v",
        ".ts",
        ".mkv",
        ".avi",
        ".wmv",
        ".webm",
        ".vob",
        ".gifv",
        ".mpg",
        ".mpeg",
        ".mp3",
        ".flac",
        ".wav",
        ".png",
        ".jpeg",
        ".jpg",
        ".gif",
        ".bmp",
        ".webp",
        ".heif",
        ".heic",
        ".tiff",
        ".svf",
        ".svg",
        ".ico",
        ".psd",
        ".ai",
        ".pdf",
        ".txt",
        ".log",
        ".csv",
        ".xml",
        ".cbr",
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".xz",
        ".tar",
        ".gz",
        ".tar",
        ".xz",
        ".iso",
        ".torrent",
        ".kdbx",
    }
)
