import open3d as o3d
import numpy as np
# from matplotlib import pyplot as plt
from pathlib import Path

from src.utils.extracting import remove_extracted, unzip

if __name__ == '__main__':

    for i, elem in enumerate(Path('data/clouds_stereo').iterdir()):
        path_to_file = unzip(str(elem), 'data/extracted')
        pcd = o3d.io.read_point_cloud(path_to_file)

        downpcd = pcd.voxel_down_sample(voxel_size=0.3)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30), fast_normal_computation=True)
        plane_model, inliers = downpcd.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=1000)
        platform = downpcd.select_by_index(inliers)
        outliers_cloud = downpcd.select_by_index(inliers, invert=True)
        plane2_model, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=1000)
        train = outliers_cloud.select_by_index(inliers2)
        other_objects = outliers_cloud.select_by_index(inliers2, invert=True)

        platform.paint_uniform_color([1, 0, 0])
        train.paint_uniform_color([0, 1, 0])
        other_objects.paint_uniform_color([0, 1, 1])

        max_bound = train.get_max_bound()
        points = np.asarray(other_objects.points)
        indexes = np.where(points[:, 1] > max_bound[1])[0]
        other_objects_filt = other_objects.select_by_index(indexes)
        other_objects_filt.paint_uniform_color([0.3, 0.2, 0.1])

        o3d.visualization.draw_geometries([platform, train, other_objects, other_objects_filt])
        o3d.visualization.draw_geometries([platform])
        # o3d.visualization.draw_geometries([outliers_cloud2])
        plane1_len = len(np.asarray(platform.points))
        plane2_len = len(np.asarray(train.points))
        outliers_len = len(np.asarray(other_objects.points))
        print(f'plane1 has {plane1_len} points')
        print(f'plane2 has {plane2_len} points')
        print(f'outliers has {outliers_len} points')
        print(f'sanity check = {outliers_len+plane1_len+plane2_len == len(np.asarray(downpcd.points))}')
        print(f'alert: {len(np.asarray(other_objects_filt.points)) > 2000} ')
        print()
        remove_extracted(path_to_file)

        symbol = input()
        if symbol == 'q':
            break
