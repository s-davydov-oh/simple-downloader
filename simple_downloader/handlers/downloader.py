from pathlib import Path
from logging import getLogger

from tqdm import tqdm

from simple_downloader.config import BASE_CHUNK, CHUNK_MULTIPLIER
from simple_downloader.core.exceptions import DeviceSpaceRunOutError, FileOpenError
from simple_downloader.core.models import MediaFile
from simple_downloader.handlers.requester import requester


logger = getLogger(__name__)

TQDM_PARAMS = {
    "bar_format": "[+] {desc} {percentage:3.0f}% [{bar:20}] {n_fmt}/{total_fmt} | {rate_fmt}",
    "colour": "GREEN",
    "unit": "B",
    "unit_scale": True,
    "unit_divisor": BASE_CHUNK,
    "miniters": 1,
    "ascii": True,
}


def download(
    file: MediaFile,
    save_path: Path,
    chunk_size: int = BASE_CHUNK * CHUNK_MULTIPLIER,
) -> None:
    stream = requester(file.stream_url, stream=True)
    size = int(stream.headers.get("content-length", 0))

    def save() -> None:
        abs_save_path = save_path.joinpath(str(file.filename))
        try:
            bf_out = abs_save_path.open("bw")
        except IOError:
            raise FileOpenError(abs_save_path)
        else:
            logger.debug("Downloading %s", file.url)

            with bf_out, tqdm(desc=file.title, total=size, **TQDM_PARAMS) as bar:
                try:
                    for chunk in stream.iter_content(chunk_size):
                        bf_out.write(chunk)
                        bar.update(len(chunk))
                except OSError:
                    raise DeviceSpaceRunOutError

            logger.debug("Downloaded %s", file.title)

    return save()
