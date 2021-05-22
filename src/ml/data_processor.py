import json
from pathlib import Path

from src.ml.classifier import Classifier
from src.utils.config import SingleConfig
from src.utils.extracting import unzip, remove_extracted


class DataProcessor:
    def __init__(self):
        self._config = SingleConfig().get_part('data_processor')
        self._path_to_data = Path(self._config.path_to_data)
        self._result_json = Path(self._config.result_json)
        self._classifier = Classifier()
        self._json_list = list()

    def process(self):
        for i, elem in enumerate(Path(self._config.path_to_data).iterdir()):
            path_to_file = unzip(str(elem), str(elem.parent))
            if path_to_file is None:
                continue
            result = self._classifier.predict(path_to_file)
            self._json_list.append({
                'alert': result.tolist()[0],
                'filename': path_to_file,
                'number': i,
            })
            remove_extracted(path_to_file)
        self._write_to_json()

    def _write_to_json(self):
        with open(self._config.result_json, 'w') as file:
            json.dump(self._json_list, file, indent=4)

    @staticmethod
    def run():
        DataProcessor().process()
