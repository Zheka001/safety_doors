
import open3d as o3d
import numpy as np
from matplotlib import pyplot as plt

def find_var(points: np.ndarray):
    ax1 = np.var(points[:,0])
    ax2 = np.var(points[:,1])
    ax3 = np.var(points[:,2])
    return [ax1, ax2, ax3]


print("Load a ply point cloud, print it, and render it")
pcd = o3d.io.read_point_cloud("/Users/rnwind/Documents/Projects/safety_doors/data/point_cloud_train/clouds_tof/cloud_0_1620665797175109.pcd")
pcd.voxel_down_sample(voxel_size=0.5)
# pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=16), fast_normal_computation=True)

plane_model, inliers = pcd.segment_plane(distance_threshold=0.05, ransac_n=3, num_iterations=1000)
inlier_cloud = pcd.select_by_index(inliers)
outliers_cloud = pcd.select_by_index(inliers, invert=True)
plane2_model, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.1, ransac_n=3, num_iterations=5000)
inlier_cloud2 = outliers_cloud.select_by_index(inliers2)
outliers_cloud2 = outliers_cloud.select_by_index(inliers2, invert=True)
inlier_cloud.paint_uniform_color([1,0,0])
inlier_cloud2.paint_uniform_color([0,1,0])
outliers_cloud2.paint_uniform_color([0,1,1])
# o3d.visualization.draw_geometries([inlier_cloud, inlier_cloud2, outliers_cloud2])
plane1_points = np.asarray(inlier_cloud.points)
plane2_points = np.asarray(inlier_cloud2.points)
outliers_points = np.asarray(outliers_cloud2.points)
print(f'plane1 has {len(plane1_points)} points')
print(f'plane2 has {len(plane2_points)} points')
print(f'outliers has {len(outliers_points)} points')
print(f'sanity check = {len(outliers_points) + len(plane1_points) + len(plane2_points) == len(np.asarray(pcd.points))}')

print(plane1_points.shape)
print((plane1_points[0]))
print('Vars for plane1: ', find_var(plane1_points))
print('Vars for plane2: ', find_var(plane2_points))






