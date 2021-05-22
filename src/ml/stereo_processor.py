# -*- coding: utf-8 -*-
import open3d as o3d
import numpy as np

from src.utils.config import SingleConfig
from src.utils.extracting import unzip, remove_extracted


class StereoProcessor:
    def __init__(self):
        self._config = SingleConfig().get_part('stereo_processor')

        self._path_to_file = None

    def run(self, filename):
        pcd = self._read_file(filename)
        downpcd = self._preprocess(pcd)
        clouds = self._divide_pcd(downpcd)
        clouds = self._filter_other_objects(clouds)
        quantity = len(np.asarray(clouds[2].points))
        remove_extracted(self._path_to_file)
        return quantity > self._config.threshold

    def _read_file(self, filename):
        path_to_file = unzip(filename, self._config.path_to_unzip)
        pcd = o3d.io.read_point_cloud(path_to_file)
        return pcd

    @staticmethod
    def _preprocess(pcd):
        downpcd = pcd.voxel_down_sample(voxel_size=0.15)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30),
                                 fast_normal_computation=True)
        return downpcd

    @staticmethod
    def _divide_pcd(pcd):
        coeff, inliers = pcd.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=1000)
        platform = pcd.select_by_index(inliers)
        outliers_cloud = pcd.select_by_index(inliers, invert=True)

        coeff2, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=5000)
        train = outliers_cloud.select_by_index(inliers2)
        other_objects = outliers_cloud.select_by_index(inliers2, invert=True)
        platform.paint_uniform_color([1, 0, 0])
        train.paint_uniform_color([0, 1, 0])
        other_objects.paint_uniform_color([0, 1, 1])
        return [platform, train, other_objects]

    @staticmethod
    def _filter_other_objects(clouds):
        max_bound = clouds[1].get_max_bound()
        points = np.asarray(clouds[2].points)
        indexes = np.where(points[:, 1] > max_bound[1])[0]
        other_objects_filt = clouds[2].select_by_index(indexes)
        other_objects_filt.paint_uniform_color([0.3, 0.2, 0.1])
        clouds[2] = other_objects_filt
        return clouds
