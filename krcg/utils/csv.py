"""CSV utilities."""

import csv
import io
import urllib.request
import zipfile


def get_zip_csv(url: str, *args: str) -> list[csv.DictReader]:
    """Return CSV readers for files inside a remote ZIP archive.

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    local_filename, _headers = urllib.request.urlretrieve(url)
    readers: list[csv.DictReader] = []
    with zipfile.ZipFile(local_filename) as z:
        for arg in args:
            data = z.read(arg).decode("utf-8-sig")
            readers.append(csv.DictReader(io.StringIO(data)))
    urllib.request.urlcleanup()
    return readers


def get_github_csv(url: str, *args: str) -> list[csv.DictReader]:
    """Return CSV readers for files hosted under a base URL (e.g., GitHub).

    Files are fully read into memory to ensure underlying file descriptors are
    closed immediately.
    """
    readers: list[csv.DictReader] = []
    for arg in args:
        local_filename, _headers = urllib.request.urlretrieve(url + arg)
        with open(local_filename, encoding="utf-8-sig") as f:
            data = f.read()
        readers.append(csv.DictReader(io.StringIO(data)))
    urllib.request.urlcleanup()
    return readers
