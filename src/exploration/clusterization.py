import open3d as o3d
import numpy as np
# from matplotlib import pyplot as plt

from src.utils.extracting import remove_extracted, unzip

if __name__ == '__main__':

    print("Load a ply point cloud, print it, and render it")
    path_to_file = unzip('../../data/clouds_stereo/cloud_2_1620666790467281.pcd.zip', 'data/extracted')
    pcd = o3d.io.read_point_cloud(path_to_file)
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=16), fast_normal_computation=True)
    plane_model, inliers = pcd.segment_plane(distance_threshold=0.05, ransac_n=3, num_iterations=1000)
    inlier_cloud = pcd.select_by_index(inliers)
    outliers_cloud = pcd.select_by_index(inliers, invert=True)
    plane2_model, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.1, ransac_n=3, num_iterations=5000)
    inlier_cloud2 = outliers_cloud.select_by_index(inliers2)
    outliers_cloud2 = outliers_cloud.select_by_index(inliers2, invert=True)
    inlier_cloud.paint_uniform_color([1,0,0])
    inlier_cloud2.paint_uniform_color([0,1,0])
    outliers_cloud2.paint_uniform_color([0,1,1])
    o3d.visualization.draw_geometries([inlier_cloud, inlier_cloud2, outliers_cloud2])
    plane1_len = len(np.asarray(inlier_cloud.points))
    plane2_len = len(np.asarray(inlier_cloud2.points))
    outliers_len = len(np.asarray(outliers_cloud2.points))
    print(f'plane1 has {plane1_len} points')
    print(f'plane2 has {plane2_len} points')
    print(f'outliers has {outliers_len} points')
    print(f'sanity check = {outliers_len+plane1_len+plane2_len == len(np.asarray(pcd.points))}')

    remove_extracted(path_to_file)