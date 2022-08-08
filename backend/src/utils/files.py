import hashlib
import os
import shutil
import zipfile
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, Union, Optional, List, Tuple, Dict
from urllib.parse import urljoin, urlparse
from tempfile import NamedTemporaryFile, mkdtemp

import requests
from fastapi.logger import logger
from pydantic import AnyHttpUrl
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    Timeout,
)

from src.config import settings

env = os.environ.get

BUF_SIZE = 65536
MAX_WORKERS = int(env("MAX_WORKERS", 5))
NGINX_DATA_PATH = env("NGINX_DATA_PATH", "./static/upload")
NGINX_PREFIX = env("NGINX_PREFIX", "")
DOWNLOAD_TIMEOUT = int(env("DOWNLOAD_TIMEOUT", 10))


class FailedToDownload(Exception):
    pass


class InvalidFileStructure(Exception):
    pass


def md5_of_file(file: Any) -> str:
    md5 = hashlib.md5()
    file.seek(0)
    while True:
        data = file.read(BUF_SIZE)
        if not data:
            break
        md5.update(data)
    file.seek(0)
    return md5.hexdigest()


def download_file(url: AnyHttpUrl, output_filename: str) -> None:
    try:
        resp = requests.get(url, timeout=5, verify=False)
        if resp.status_code == requests.codes.not_found:
            raise FailedToDownload(url)
    except(
            ConnectionError,
            HTTPError,
            MissingSchema,
            InvalidSchema,
            InvalidURL,
            Timeout,
    ):
        raise FailedToDownload(url)
    with open(output_filename, "wb") as f:
        for chunk in resp.iter_content(1024):
            f.write(chunk)


def decompress_zip(zip_file_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
    with zipfile.ZipFile(str(zip_file_path), "r") as zip_file:
        zip_file.extractall(str(output_dir))


def save_file_content(url: Union[AnyHttpUrl, str], output_filename: Union[Path, str]) -> None:
    if urlparse(url).netloc:
        return download_file(url, output_filename)  # type: ignore
    NGINX_DATA_PATH = "/"
    file_path = Path(NGINX_DATA_PATH) / url
    shutil.copy(file_path, output_filename)


def save_file(
        url: Union[AnyHttpUrl, str],
        output_dir: Union[str, Path],
        output_filename: Optional[str] = None,
) -> Path:
    filename = output_filename or Path(urlparse(url).path).name
    output_file = Path(output_dir) / filename
    save_file_content(url, output_file)
    return output_file


def save_files(urls: List[Union[AnyHttpUrl, str]], output_basedir: Union[str, Path]) -> Tuple[str, Dict]:
    output_dir = mkdtemp(prefix="import_files_", dir=output_basedir)
    save_ = partial(save_file, output_basedir=Path(output_dir))
    workers = min(MAX_WORKERS, len(urls))
    with ThreadPoolExecutor(workers) as executor:
        res = executor.map(save_, urls)
    return output_dir, {filename.name: url for filename, url in zip(res, urls)}


def host_file(file: Any) -> str:
    p = Path(file.filename)
    target = (Path(NGINX_DATA_PATH) / md5_of_file(file.file)).with_suffix(p.suffix)
    with open(target, "wb") as f:
        f.write(file.file.read())
    return urljoin(NGINX_PREFIX, str(target))
