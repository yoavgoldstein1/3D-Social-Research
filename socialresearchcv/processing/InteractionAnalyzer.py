import glob
import itertools
import os
import sys

import cv2
from socialresearchcv.processing.CONFIG import CONFIG
import json
import pyrealsense2 as rs

from socialresearchcv.processing.CSVWriter import CSVWriter
from socialresearchcv.processing.ImageSet import ImageSet
from socialresearchcv.processing.Keypoint import Keypoint
from socialresearchcv.processing.PoseViewer import PoseViewer
# from socialresearchcv.processing.AgeGenderDetector import AgeGenderDetector


class InteractionAn():

    @staticmethod
    def run_all(save_world_points=False, start_index=0, end_index = 0,progress_bar=None):
        """Run interaction pipeline and save data as required in the CONFIG file

        Args:
            save_world_points (bool, optional): true if 3D points needs to be exported. Defaults to False.
            start_index (int, optional): start frame. Defaults to 0.
            end_index (int, optional): end frame. Defaults to 0.
            progress_bar (_type_, optional): progress bar object. Defaults to None.

        Raises:
            Exception: _description_
        """
        pipeline = rs.pipeline()
        config = rs.config()
        if CONFIG.LOAD_FROM_FILE:
            config.enable_device_from_file(CONFIG.DIR_PATH)
        else:
            config.enable_stream(rs.stream.depth)
        profile = pipeline.start(config)
        # Get stream profile and camera intrinsics
        profile = pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        w, h = depth_intrinsics.width, depth_intrinsics.height
        pose_viewer = PoseViewer(intrinsics=depth_intrinsics)
        
        csv_writer = CSVWriter(path=f'{CONFIG.CSV_PATH}_{start_index}_{end_index}.csv')
        index = start_index
        point_cloud_over_time = []

        # if CONFIG.EXTRACT_AGE_GENDER:
            # ag_detector = AgeGenderDetector()

        
        for number in (range(end_index-start_index)):
            
            if progress_bar is not None:
                progress_bar.set_description(f'Parsing Frame #{index}')
                progress_bar.update(1)

            image_set = ImageSet(index)
            
            with open(image_set.keypoints_path) as json_file:
                data = json.load(json_file)
                people = data['people']

                if len(people) <= 0:  # No People found, adding empty row
                    csv_writer.add_empty_row(frame_index=index)
                else:
                    point_cloud_over_time.append([])
                    frame_keypoints = list()

                    ################# CREATE FRAME KEYPOINTS ###############
                    ########################################################
                    for p_index, p in enumerate(people):

                        keypoints_list = p['pose_keypoints_2d']
                        current_keypoint = Keypoint(index, p_index, image_set, keypoints_list, pose_viewer)
                        
                        
                        point_for_cloud = []
                        for i in range(0, len(keypoints_list) // 3):
                            p_cloud = [int(keypoints_list[3 * i]), int(keypoints_list[3 * i + 1]),
                                        keypoints_list[3 * i + 2]]
                            point_for_cloud.append(p_cloud)
                        
                        csv_writer.add_poses(
                            [pose_viewer.get_world_point(p_2d, image_set.depth_image) for p_2d in point_for_cloud],
                            p_index, index, "Keypoints(m)")
                        csv_writer.add_keypoints2D(
                            [p_2d for p_2d in point_for_cloud],
                            p_index, index, "Keypoints(image)")
                        point_cloud_over_time[-1].append(point_for_cloud)

                        frame_keypoints.append(current_keypoint)

                    ########################################################
                    ################# ANALYZE AND PRESENT DATA #############
                    ########################################################

                    
                    # Age and Gender
                    # if CONFIG.EXTRACT_AGE_GENDER:
                        # out_image,a_g_data = ag_detector.detect(image_set.age_gender)
                        # [csv_writer.add_age_gender_data(data, i, index, f'Age and Gender') for i,data in enumerate(a_g_data)]


                    # distance points
                    for kp in frame_keypoints:
                        pose_viewer.ShowPoint(kp.keypoint_joints_2d[0], image_set.depth_image,
                                                                            image_set.depth_colormap,
                                                                            image_set.analyzed)
                    #Keypoint IDs
                    for kp in frame_keypoints:
                        for j in range(0, 20):
                            pose_viewer.ShowPersonLabel(kp.keypoint_joints_2d[j], None,
                                                                                None,
                                                                                image_set.keypoints_ids, CONFIG.JOINT_NAMES_DICT[j])
                        
                    #Person IDs
                    for kp in frame_keypoints:
                         for j in range(0, 20):
                            pose_viewer.ShowPersonLabel(kp.keypoint_joints_2d[j], None,
                                                                                None,
                                                                                image_set.person_ids, str(kp.keypoint_body_id))
                            



                    # Add points for distance
                    points_distance_dict = dict()
                    for j in range(0, 20):
                        points_distance_dict[j] = [kp.keypoint_joints_2d[j] for kp in frame_keypoints]

                    distances = pose_viewer.showDistances(points_distance_dict, image_set.depth_image,
                                                            image_set.depth_colormap, image_set.analyzed)
                    csv_writer.add_pose([(0, 0, 0)] * len(CONFIG.JOINT_NAMES_DICT.keys()), None, index, "Distance(m)",
                                        keypoint_id=-1, distances=distances)

                    # Point cloud visualization
                    pose_viewer.showPointCloud(index,
                                                [k.keypoint_body_id for k in
                                                frame_keypoints],
                                                point_cloud_over_time,
                                                image_set.depth_image, image_set.point_cloud,
                                                image_set.point_cloud_hull, csv_writer,
                                                pose_viewer)

                    # Add points for angles
                    points_angles_dict_relative = dict()
                    for j in [2, 5, 15, 16]:
                        points_angles_dict_relative[j] = [kp.keypoint_joints_2d[j] for kp in frame_keypoints]

                    points_angles_dict_personal = dict()
                    bodies = [k.keypoint_body_id for k in frame_keypoints]
                    for pair in itertools.product([(2, 5), (2, 3), (5, 6)], bodies):
                        points_angles_dict_personal[pair[0]] = [
                            (kp.keypoint_joints_2d[pair[0][0]], kp.keypoint_joints_2d[pair[0][1]]) for kp in
                            frame_keypoints]
                    pose_viewer.show_angles(points_angles_dict_personal,
                                            points_angles_dict_relative,
                                            image_set.depth_image,
                                            image_set.depth_colormap,
                                            image_set.angles_image_personal,
                                            image_set.angles_image_relative)

                if save_world_points:
                    if os.listdir(CONFIG.KEYPOINTS_PROJECTED_PATH) and index is 0:
                        sys.exit(f'Path {CONFIG.PNG_PATH_COLOR} for projected keypoints is not empty')
                    with open(image_set.out_3d_keypoints_path, 'w') as outfile:
                        json.dump(data, outfile)

            index += 1

            if index==end_index:
                if CONFIG.VERBOSE:
                    print("End index reached, raising exception")
                raise Exception



                
            if CONFIG.SAVE_OUTPUT_VIDEOS:
            
                for p_index, p in enumerate(people):

                    keypoints_list = p['pose_keypoints_2d']
                    current_keypoint = Keypoint(index, p_index, image_set, keypoints_list, pose_viewer)
                        
                        
                    point_for_cloud = []
                    for i in range(0, len(keypoints_list) // 3):
                        p_cloud = [int(keypoints_list[3 * i]), int(keypoints_list[3 * i + 1]),
                                    keypoints_list[3 * i + 2]]
                        point_for_cloud.append(p_cloud)
                    if CONFIG.BLUR_FACES and CONFIG.SAVE_OUTPUT_VIDEOS:
                        image_set.blur_faces(point_for_cloud)
                image_set.draw_images(index)

    @staticmethod
    def export_to_video(path, file_name, start_index, end_index):
        """Export sequence into video

        Args:
            path (string): images path
            file_name (string): output file name
            start_index (int): start frame
            end_index (int): end frame
        """
        img_array = []
        files = glob.glob(path + "*")
        for i in range(start_index, end_index):
            img_path = path+"output_"+str(i)+'.jpg'
            img = cv2.imread(img_path)
            if img is not None:
                height, width, layers = img.shape
                size = (width, height)
                img_array.append(img)
        
        out_path = f'Outputs/{CONFIG.IMAGES_DIR}/{file_name}'
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()

    @staticmethod
    def run(start_index = 0, end_index = 0, progress=None):
        """Run the interaction analysis

        Args:
            start_index (int, optional): start frame. Defaults to 0.
            end_index (int, optional): end frame. Defaults to 0.
            progress (_type_, optional): progress bar object. Defaults to None.
        """
        
        try:
            pass
            InteractionAn.run_all(save_world_points=False, start_index=start_index, end_index=end_index, progress_bar=progress)
        except FileNotFoundError as e:
            print('File not found!', file=sys.stderr)
            print(e)
        except Exception as e:
            pass
            if CONFIG.VERBOSE:
                print('Something went wrong, carrying on', file=sys.stderr)
                import traceback 
                traceback.print_exc() 
                print(e,file=sys.stderr)

        if CONFIG.SAVE_OUTPUT_VIDEOS:
            InteractionAn.export_to_video(CONFIG.OUTPUT_IMAGE_PATH_1, f'outVideo1_{start_index}_{end_index}.avi', start_index, end_index)
            InteractionAn.export_to_video(CONFIG.OUTPUT_IMAGE_PATH_2, f'outVideo2_{start_index}_{end_index}.avi', start_index, end_index)
            InteractionAn.export_to_video(CONFIG.OUTPUT_IMAGE_PATH_3, f'outVideo3_{start_index}_{end_index}.avi', start_index, end_index)

