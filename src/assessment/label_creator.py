# -*- coding: utf-8 -*-
import json
import open3d as o3d
from pathlib import Path

from src.utils.config import SingleConfig
from src.utils.extracting import unzip, remove_extracted


class LabelCreator:
    def __init__(self):
        self._config = SingleConfig().get_part('label_creator')
        self._json_list = list()
        self._read_json()

    def process(self):
        for i, elem in enumerate(Path(self._config.path_to_data).iterdir()):
            path_to_file = unzip(str(elem), str(elem.parent)) if '.zip' in str(elem) else str(elem)
            if path_to_file is None:
                continue
            self._show_pcd(path_to_file)
            self._process_label(path_to_file, i)
            if '.zip' in str(elem):
                remove_extracted(path_to_file)

            if i % 10 == 0:
                self._write_to_json()

        self._write_to_json()

    def _show_pcd(self, path_to_file):
        pcd = o3d.io.read_point_cloud(path_to_file)
        o3d.visualization.draw_geometries([pcd], width=1080, height=720)

    def _process_label(self, path_to_file, number):
        print('\nChoose: 1  - for alert, 0 - for safe start. Press Enter to save answer ...')
        result = int(input())
        self._json_list.append({
            'decision': result,
            'filename': str(Path(path_to_file).name),
            'number': number,
        })

    def _read_json(self):
        if Path(self._config.result_json).exists():
            with open(self._config.result_json, 'r') as file:
                self._json_list = json.load(file)

    def _write_to_json(self):
        with open(self._config.result_json, 'w') as file:
            json.dump(self._json_list, file, indent=4)

    @staticmethod
    def run():
        LabelCreator().process()
