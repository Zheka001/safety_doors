# -*- coding: utf-8 -*-
import zipfile
from pathlib import Path


def unzip(path_to_file: str, destination: str):
    try:
        with zipfile.ZipFile(path_to_file, 'r') as zip_ref:
            zip_ref.extractall(destination)
    except FileNotFoundError:
        return None
    filename = str(Path(path_to_file).name)[:-4]
    return str(Path(destination).joinpath(filename))


def remove_extracted(path_to_file: str):
    Path(path_to_file).unlink()
