import open3d as o3d
import numpy as np
# from matplotlib import pyplot as plt
from  pathlib import Path

from src.utils.extracting import remove_extracted, unzip

if __name__ == '__main__':

    for i, elem in enumerate(Path('../../data/clouds_stereo').iterdir()):
    # print("Load a ply point cloud, print it, and render it")
        path_to_file = unzip(elem, 'data/extracted')
        pcd = o3d.io.read_point_cloud(path_to_file)

        downpcd = pcd.voxel_down_sample(voxel_size=0.15)

        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30), fast_normal_computation=True)
        plane_model, inliers = downpcd.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=1000)
        inlier_cloud = downpcd.select_by_index(inliers)
        outliers_cloud = downpcd.select_by_index(inliers, invert=True)
        plane2_model, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.15, ransac_n=3, num_iterations=5000)
        inlier_cloud2 = outliers_cloud.select_by_index(inliers2)
        outliers_cloud2 = outliers_cloud.select_by_index(inliers2, invert=True)
        inlier_cloud.paint_uniform_color([1,0,0])
        inlier_cloud2.paint_uniform_color([0,1,0])
        outliers_cloud2.paint_uniform_color([0,1,1])
        print(inlier_cloud2.get_max_bound())
        max_bound = inlier_cloud2.get_max_bound()
        points = np.asarray(outliers_cloud2.points)
        indexes = np.where(points[:, 1] > max_bound[1])[0]
        outliers_cloud2_filt = outliers_cloud2.select_by_index(indexes)
        outliers_cloud2_filt.paint_uniform_color([0.3, 0.2, 0.1])

        o3d.visualization.draw_geometries([inlier_cloud, inlier_cloud2, outliers_cloud2, outliers_cloud2_filt])
        o3d.visualization.draw_geometries([inlier_cloud])
        # o3d.visualization.draw_geometries([outliers_cloud2])
        plane1_len = len(np.asarray(inlier_cloud.points))
        plane2_len = len(np.asarray(inlier_cloud2.points))
        outliers_len = len(np.asarray(outliers_cloud2.points))
        print(f'plane1 has {plane1_len} points')
        print(f'plane2 has {plane2_len} points')
        print(f'outliers has {outliers_len} points')
        print(f'sanity check = {outliers_len+plane1_len+plane2_len == len(np.asarray(downpcd.points))}')
        print(f'alert: {len(np.asarray(outliers_cloud2_filt.points)) > 2000} ')
        print()
        remove_extracted(path_to_file)
