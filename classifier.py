import json
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import numpy as np

from src.ml.feature_extractor import FeatureExtractor

class Classifier:
    def __init__(self):
        self.labels_path = Path('data/clouds_tof.json')
        self.pcd_path = Path('data/point_cloud_train/clouds_tof')
        self.saved_features_path = Path('data/features.json')
        self.X = None
        self.y = None


    def load_data_and_labels(self, alpha_list, voxel_size):
        with self.labels_path.open() as f:
            labels_dicts = json.load(f)
        features = []
        labels = []
        to_save = {}
        features_exist = self.saved_features_path.exists()
        if features_exist:
            with self.saved_features_path.open() as f:
                loaded_features = json.load(f)
        for idx, record in enumerate(labels_dicts):
            labels.append(record['decision'])
            cur_pcd = str(self.pcd_path.joinpath(record['filename']))
            if features_exist:
                feature = loaded_features[record['filename']]
            else:
                feature = FeatureExtractor.extract_features(cur_pcd, alpha_list, voxel_size=voxel_size)
                to_save[record['filename']] = feature
            features.append(feature)
        if not features_exist:
            with self.saved_features_path.open('w') as f:
                json.dump(to_save, f, indent=4)

        print(f'Data loaded: {len(labels)}')
        self.X = np.array(features)
        self.y = np.array(labels)
        print('x shape = ', self.X.shape)
        print('y shape = ', self.y.shape)

    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.20, random_state=42)
        cls = LogisticRegression()
        cls.fit(X_train, y_train)
        y_pred = cls.predict(X_test)
        print(y_pred)
        f1 = f1_score(y_test, y_pred)
        print(f1)

if __name__ == "__main__":
    cls = Classifier()
    cls.load_data_and_labels([5,6,7,8], None)
    cls.train()







