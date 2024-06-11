from pathlib import Path
from logging import getLogger

from simple_downloader.config import CHUNK_MULTIPLIER
from simple_downloader.core.models import MediaFile
from simple_downloader.handlers.requester import requester


logger = getLogger(__name__)


def download(
    file: MediaFile,
    save_path: Path,
    chunk_size: int = 1024 * CHUNK_MULTIPLIER,
) -> None:
    stream = requester(file.stream_url, stream=True)

    def save() -> None:
        try:
            bf_out = save_path.joinpath(str(file.filename)).open("bw")
        except IOError as e:
            logger.debug(e)
        else:
            logger.debug("Downloading %s", file.url)
            with bf_out:
                for chunk in stream.iter_content(chunk_size):
                    bf_out.write(chunk)
            logger.debug("Downloaded %s", file.title)

    return save()
