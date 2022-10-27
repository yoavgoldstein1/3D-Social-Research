import cv2
import numpy as np
import pyrealsense2 as rs

from socialresearchcv.processing import Utils
from socialresearchcv.processing.CONFIG import CONFIG
from scipy.spatial import ConvexHull


class PoseViewer:
    def __init__(self, intrinsics):
        self.depth_intrinsics = intrinsics

    def get_point(self, x, y, d):
        p = rs.rs2_deproject_pixel_to_point(self.depth_intrinsics, [x, y], d)
        return p

    def ShowPoint(self, p, depth_image, depth_colormap, color_image):
        self.inner_show_point(p, depth_image, depth_colormap, color_image, None)

    def ShowPersonLabel(self, p, depth_image, depth_colormap, color_image, person_number):
        label = f'{person_number}'
        return self.inner_show_point(p, depth_image, depth_colormap, color_image, label, size=0.6)

    def inner_show_point(self, p, depth_image, depth_colormap, color_image, text_to_show, size=0.8):
        
        if depth_image is not None:
            world_p = self.get_world_point(p, depth_image)

            if world_p is None:
                print("WorldP is none")
                return color_image, depth_colormap, None

        if text_to_show is None:
            text_to_show = f'({world_p[0] / 1000:.2f},{world_p[1] / 1000:.2f},{world_p[2] / 1000:.2f})m'

        if depth_image is not None:
            size_normlization = size * (1 - (world_p[2] / 1000) / 20)
        else:
            size_normlization = size

        color_image = cv2.putText(color_image, text_to_show, (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, size_normlization,
                                  (255 * p[2], 255 * p[2], 255 * p[2]), thickness=1)
        
        if depth_image is not None:        
            depth_colormap = cv2.putText(depth_colormap, text_to_show, (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX,
                                         size_normlization,
                                         (255 * p[2], 255 * p[2], 255 * p[2]), thickness=2)
        x = p[0]
        y = p[1]
        delim = CONFIG.DEPTH_SAMPLE_RECT

    def get_world_point(self, p, depth_image):
        d = Utils.sample_depth(p, depth_image)
        if d is None:
            return [0, 0, 0]
        world_p = self.get_point(int(p[0]), int(p[1]), d)
        return [int(world_p[0]), int(world_p[1]), world_p[2]]

    def midpoint(self, p1, p2):
        return int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)

    def showDistances(self, points, depth_image, depth_colormap, color_out):
        distances = dict()
        for j, pair in points.items():
            if len(pair)<2 or pair[0] == [0, 0, 0] or pair[1] == [0, 0, 0]:
                continue

            x_y_points = [(p[0], p[1]) for p in pair]
            world_points = [self.get_world_point(p, depth_image) for p in pair]
            cv2.line(color_out, x_y_points[0], x_y_points[1], (255, 0, 0), 2)
            d = np.linalg.norm(np.array(world_points[0]) - np.array(world_points[1]))

            distances[j] = d
            text_to_show = f'{d / 1000:.2f}m'
            color_out = cv2.putText(color_out, text_to_show, self.midpoint(x_y_points[0], x_y_points[1]),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 0), thickness=3)
        return distances

    def showPointCloud(self, frame_id, pose_ids, point_clouds_over_time, depth_image, point_cloud_image, point_cloud_hull, csv_writer,
                       pose_viewer):

        history_size = CONFIG.HISTORY_SIZE
        for pc, index in zip(point_clouds_over_time[-history_size:], range(1, history_size)):
            for pose_id, point_cloud in zip(pose_ids, pc):
                points = []
                for p in point_cloud:
                    if p != [0, 0, 0]:
                        points.append((int(p[0]), int(p[1])))

                [cv2.circle(point_cloud_image, world_p, 10, self.get_color_for_pose_id(pose_id, history_size - index),
                            2) for world_p in points]

            for pose_id, point_cloud in zip(pose_ids, point_clouds_over_time[-1]):
                points = []
                for p in point_cloud:
                    if p != [0, 0, 0]:
                        points.append((int(p[0]), int(p[1])))
                
                try:
                    hull = ConvexHull(points)
                    h_points = np.array(hull.points)

                    hull_points = [[0, 0, 0]] * len(points)
                    for i in range(-1, len(hull.vertices) - 1):
                        p1 = (int(h_points[hull.vertices[i], 0]), int(h_points[hull.vertices[i], 1]))
                        p2 = (int(h_points[hull.vertices[i + 1], 0]), int(h_points[hull.vertices[i + 1], 1]))
                        color = self.get_color_for_pose_id(pose_id, 1)
                        cv2.line(point_cloud_hull, p1, p2, color, thickness=2)
                        hull_points[hull.vertices[i]] = [p1[0], p1[1], 1]
                except:
                    pass

            csv_writer.add_poses([pose_viewer.get_world_point(p_2d, depth_image) for p_2d in hull_points],
                                 pose_id, frame_id, "Cloud Points(m)")

        return point_cloud_image, h_points, point_cloud_hull

    def show_angles(self, points_angles_dict_personal, points_angles_dict_relative, depth_image, depth_colormap, angles_image_personal, angles_image_relative):
        for j, pairs in points_angles_dict_personal.items():
            for pair in pairs:
                if pair[0] == [0, 0, 0] or pair[1] == [0, 0, 0]:
                    continue
                x_y_points = [(p[0], p[1]) for p in pair]

                cv2.line(angles_image_personal, x_y_points[0], x_y_points[1], (0, 255, 255), 2)

        for j, pair in points_angles_dict_relative.items():
            if len(pair)<2 or pair[0] == [0, 0, 0] or pair[1] == [0, 0, 0]:
                continue
            x_y_points = [(p[0], p[1]) for p in pair]

            cv2.line(angles_image_relative, x_y_points[0], x_y_points[1], (255, 255, 0), 2)
        return angles_image_personal, angles_image_relative

    def get_color_for_pose_id(self, pose_id, index):
        luminance = 200 // (2*index/CONFIG.HISTORY_SIZE)
        if pose_id is 0:
            return (luminance, 0, 0)
        elif pose_id is 1:
            return (0, luminance, 0)
        elif pose_id is 2:
            return (0, 0, luminance)
        else:
            return (255, 255, 255)
