import json
from pathlib import Path
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import numpy as np

from src.ml.feature_extractor import FeatureExtractor
from src.utils.config import SingleConfig, SingletonMeta


class Classifier(metaclass=SingletonMeta):
    def __init__(self):
        self._config = SingleConfig().get_part('classifier')
        self._labels_path = Path(self._config.labels_path)
        self._pcd_path = Path(self._config.data_path)
        self._saved_features_path = Path(self._config.saved_features_path)
        self._model_path = Path(self._config.model_path)
        self.alpha_list = self._config.alpha_list
        self.voxel_downsample = None

        self._X = None
        self._y = None
        self._model = None
        if Path(self._model_path).exists():
            self._load_model()

    def load_data_and_labels(self, alpha_list, voxel_size):
        with self._labels_path.open() as f:
            labels_dicts = json.load(f)
        features = []
        labels = []
        to_save = {}
        features_exist = self._saved_features_path.exists()
        if features_exist:
            with self._saved_features_path.open() as f:
                loaded_features = json.load(f)
        for idx, record in enumerate(labels_dicts):
            labels.append(record['decision'])
            cur_pcd = str(self._pcd_path.joinpath(record['filename']))
            if features_exist:
                feature = loaded_features[record['filename']]
            else:
                feature = FeatureExtractor.extract_features(cur_pcd, alpha_list, voxel_size=voxel_size)
                to_save[record['filename']] = feature
            features.append(feature)
        if not features_exist:
            with self._saved_features_path.open('w') as f:
                json.dump(to_save, f, indent=4)

        print(f'Data loaded: {len(labels)}')
        self._X = np.array(features)
        self._y = np.array(labels)
        print('x shape = ', self._X.shape)
        print('y shape = ', self._y.shape)

    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self._X, self._y, test_size=0.20, random_state=42)
        cls = LogisticRegression()
        cls.fit(X_train, y_train)
        y_pred = cls.predict(X_test)
        print(y_pred)
        f1 = f1_score(y_test, y_pred)
        print('F1 score on test set:', f1)

        self._model = cls
        self._save_model()

    def predict(self, pcd_path: str):
        feature = FeatureExtractor.extract_features(pcd_path, self.alpha_list, voxel_size=self.voxel_downsample)
        return self._model.predict([feature])

    def _save_model(self):
        with open(self._model_path, 'wb') as output:
            pickle.dump(self._model, output)

    def _load_model(self):
        with open(self._model_path, 'rb') as input:
            self._model = pickle.load(input)

    @staticmethod
    def run():
        cls = Classifier()
        cls.train()

if __name__ == "__main__":
    cls = Classifier()
    # cls.load_data_and_labels([5,8,10,12], None)
    # cls.train()
    print(cls.predict("data/point_cloud_train/clouds_tof/cloud_0_1620665797175109.pcd"))







