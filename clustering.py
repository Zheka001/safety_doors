import open3d as o3d
import numpy as np


class FeatureExtractor:

    @staticmethod
    def find_var(points: np.ndarray):
        return [np.var(points[:, i]) for i in range(points.shape[1])]

    @staticmethod
    def count_poi(plane1: np.ndarray, plane2: np.ndarray, other: np.ndarray, alpha):
        vars1 = FeatureExtractor.find_var(plane1)
        vars2 = FeatureExtractor.find_var(plane2)
        if min(vars1) < min(vars2):
            platform, platform_vars = plane1, vars1
            train, train_vars = plane2, vars2
        else:
            platform, platform_vars = plane2, vars2
            train, train_vars = plane1, vars1

        low_var_id = np.argmin(platform_vars)
        saved_axis = [i for i in range(3) if i != low_var_id]

        platform = platform[:, saved_axis]
        train = train[:, saved_axis]
        objects = other[:, saved_axis]
        del platform_vars[low_var_id]
        del train_vars[low_var_id]

        max_var_id = np.argmax(train_vars)
        saved_axis = [i for i in range(2) if i != max_var_id]

        platform = platform[:, saved_axis]
        train = train[:, saved_axis]
        objects = objects[:, saved_axis]
        del platform_vars[max_var_id]
        del train_vars[max_var_id]

        train_center = np.sum(train)/train.shape[0]
        platform_center = np.sum(platform)/platform.shape[0]

        clean_side = 'left' if platform_center > train_center else 'right'
        if clean_side == 'left':
            objects = objects[objects > train_center]
        else:
            objects = objects[objects < train_center]

        # most_platform = platform_vars[0] * 3 # 66% of platform points
        # margin = np.abs(train_center-platform_center) - most_platform
        # margin = margin if margin > 0 else np.abs(train_center - platform_center) / alpha

        result = []
        for i in range(len(alpha)):
            margin = np.abs(train_center - platform_center) / alpha[i]
            cur_objects = objects[(objects < train_center + margin) & (objects > train_center - margin)]
            result.append(len(cur_objects))

        # print(train.shape, platform.shape)
        # print(train_vars[0], platform_vars[0])
        # print(f'train {np.min(train)}:{np.max(train)}')
        # print(f'platform {np.min(platform)}:{np.max(platform)}')
        # print(f'train_center={train_center}, platform_center={platform_center}')
        # print(f'most platform dist = {most_platform}, margin = {margin}, margin_candidate = {np.abs(train_center - platform_center) / 5}')
        print(f'Objects before: {other.shape[0]}, objects after: {result} for alpha: {alpha}')

        return result

    @staticmethod
    def extract_features(pcd_path: str, alpha_list, voxel_size=None, show=False):
        pcd = o3d.io.read_point_cloud(pcd_path)
        if voxel_size is not None:
            pcd.voxel_down_sample(voxel_size=0.5)
        plane_model, inliers = pcd.segment_plane(distance_threshold=0.05, ransac_n=3, num_iterations=1000)
        inlier_cloud = pcd.select_by_index(inliers)
        outliers_cloud = pcd.select_by_index(inliers, invert=True)
        plane2_model, inliers2 = outliers_cloud.segment_plane(distance_threshold=0.1, ransac_n=3, num_iterations=5000)
        inlier_cloud2 = outliers_cloud.select_by_index(inliers2)
        outliers_cloud2 = outliers_cloud.select_by_index(inliers2, invert=True)
        inlier_cloud.paint_uniform_color([1, 0, 0])
        inlier_cloud2.paint_uniform_color([0, 1, 0])
        outliers_cloud2.paint_uniform_color([0, 1, 1])
        if show:
            o3d.visualization.draw_geometries([inlier_cloud, inlier_cloud2, outliers_cloud2])
        plane1_points = np.asarray(inlier_cloud.points)
        plane2_points = np.asarray(inlier_cloud2.points)
        outliers_points = np.asarray(outliers_cloud2.points)

        # print(f'plane1 has {len(plane1_points)} points')
        # print(f'plane2 has {len(plane2_points)} points')
        # print(f'outliers has {len(outliers_points)} points')
        # print(
        #     f'sanity check = {len(outliers_points) + len(plane1_points) + len(plane2_points) == len(np.asarray(pcd.points))}')
        #
        # print(plane1_points.shape)
        # print((plane1_points[0]))
        # print('Vars for plane1: ', find_var(plane1_points))
        # print('Vars for plane2: ', find_var(plane2_points))

        return FeatureExtractor.count_poi(plane1_points, plane2_points, outliers_points, alpha_list)


if __name__ == '__main__':
    pcd = "data/point_cloud_train/clouds_tof/cloud_0_1620666065884775.pcd"
    FeatureExtractor.extract_features(pcd, [5, 6, 7, 8], voxel_size=0.5, show=True)
