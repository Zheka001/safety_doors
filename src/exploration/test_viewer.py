import open3d as o3d
from pathlib import Path

from src.utils.extracting import unzip, remove_extracted


if __name__ == '__main__':
    for elem in Path('../../data/point_cloud_gt/clouds_stereo').iterdir():
        path_to_file = unzip(str(elem), 'extracted')
        pcd = o3d.io.read_point_cloud(path_to_file)
        o3d.visualization.draw_geometries([pcd])
        remove_extracted(path_to_file)

