from pathlib import Path
from logging import getLogger

from requests.exceptions import ChunkedEncodingError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from tqdm import tqdm

from simple_downloader.config import (
    BAR_FORMAT,
    BASE_CHUNK,
    CHUNK_MULTIPLIER,
    DISABLE_CLI_MESSAGES,
    RETRY_STRATEGY,
    TOTAL_RETRIES,
)
from simple_downloader.core.exceptions import DeviceSpaceRunOutError, FileOpenError
from simple_downloader.core.models import MediaFile
from simple_downloader.core.logs import log_download, log_retry
from simple_downloader.handlers.requester import Requester


logger = getLogger(__name__)

TQDM_PARAMS = {
    "bar_format": BAR_FORMAT,
    "colour": "GREEN",
    "unit": "B",
    "unit_scale": True,
    "unit_divisor": BASE_CHUNK,
    "miniters": 1,
    "ascii": True,
    "disable": DISABLE_CLI_MESSAGES,
}


@retry(
    reraise=True,
    stop=stop_after_attempt(TOTAL_RETRIES),
    wait=wait_exponential(**RETRY_STRATEGY),
    retry=retry_if_exception_type(ChunkedEncodingError),
    before=log_download,
    before_sleep=log_retry,
)
def download(
    file: MediaFile,
    save_path: Path,
    http_client: Requester,
    chunk_size: int = BASE_CHUNK * CHUNK_MULTIPLIER,
) -> None:
    stream = http_client.get_response(file.stream_url, stream=True)
    size = int(stream.headers.get("content-length", 0))

    def save() -> None:
        abs_save_path = save_path.joinpath(str(file.filename))
        try:
            bf_out = abs_save_path.open("bw")
        except IOError:
            raise FileOpenError(abs_save_path)
        else:
            with bf_out, tqdm(desc=file.title, total=size, **TQDM_PARAMS) as bar:
                for chunk in stream.iter_content(chunk_size):
                    try:
                        bf_out.write(chunk)
                    except OSError:
                        raise DeviceSpaceRunOutError
                    else:
                        bar.update(len(chunk))

            logger.debug("Downloaded %s", file.title)

    save()
