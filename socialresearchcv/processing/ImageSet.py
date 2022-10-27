import os
import cv2
import numpy as np
import pickle
from socialresearchcv.processing.CONFIG import CONFIG
from socialresearchcv.processing.Utils import blur_face


class ImageSet:
    """Represents a set of images (color, depth, raw, etc.)
    """
    def __init__(self,index):
        path = f'Outputs/{CONFIG.IMAGES_DIR}/'
        color_path = f'{path}color/color_{index}.png'
        color_out_path = f'{path}outputImages/color_{index}_rendered.png'
        keypoints_path = f'{path}keypoints/color_{index}_keypoints.json'
        out_3d_keypoints_path = f'{CONFIG.KEYPOINTS_PROJECTED_PATH}/color_{index}_keypoints_projected.json'
        self.color = cv2.imread(color_path)

        with (open(f'{CONFIG.DEPTH_RAW_VIDEO_PATH}_{index}.pkl', 'rb')) as file:
            self.depth_image = pickle.load( file)
        with (open(f'{CONFIG.DEPTH_COLORMAP_VIDEO_PATH}_{index}.pkl', 'rb' )) as file:        
            self.depth_colormap = pickle.load( file)    
    
        if os.path.exists(color_out_path):
            self.color_out = cv2.imread(color_out_path)
        else:
            self.color_out = np.copy(self.color)
        self.analyzed = np.copy(self.color)
        self.point_cloud = np.copy(self.color)
        self.point_cloud_hull = np.copy(self.color)
        self.angles_image_personal = np.copy(self.color)
        self.angles_image_relative = np.copy(self.color)
        self.keypoints_ids = np.copy(self.color)
        self.person_ids = np.copy(self.color)
        self.age_gender = np.copy(self.color)

        self.keypoints_path = keypoints_path
        self.out_3d_keypoints_path = out_3d_keypoints_path


    def blur_faces(self, keypoints_list):
        """Perform blur on the face using the openpose keypoint information

        Args:
            keypoints_list (list): list of keypoints
        """
        
        keypoints = [keypoints_list[0], keypoints_list[1]]
        if len(keypoints)<2 or keypoints[0] == [0, 0, 0] or keypoints[1] == [0, 0, 0]:
            return
        else:
            self.color = blur_face(self.color, keypoints)
            self.color_out = blur_face(self.color_out, keypoints)
            self.analyzed = blur_face(self.analyzed, keypoints)
            self.point_cloud = blur_face(self.point_cloud, keypoints)
            self.point_cloud_hull = blur_face(self.point_cloud_hull, keypoints)
            self.angles_image_personal = blur_face(self.angles_image_personal, keypoints)
            self.angles_image_relative = blur_face(self.angles_image_relative, keypoints)
            self.person_ids = blur_face(self.person_ids, keypoints)
            self.age_gender = blur_face(self.age_gender, keypoints)
            self.keypoints_ids = blur_face(self.keypoints_ids, keypoints)


    
    def draw_images(self, frame_number):
        """Visualize images in several ways

        Args:
            frame_number (int): number of frame to process
        """
        c_resized = cv2.resize(self.color, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        d_resized = cv2.resize(self.depth_colormap, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        c_o_resized = cv2.resize(self.color_out, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        a_o_resized = cv2.resize(self.analyzed, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        c_resized = cv2.putText(c_resized, f'Color {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                thickness=2)
        d_resized = cv2.putText(d_resized, f'Depth {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                thickness=2)
        c_o_resized = cv2.putText(c_o_resized, f'Skeleton {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                  (0, 0, 0),
                                  thickness=2)
        a_o_resized = cv2.putText(a_o_resized, f'Analysis {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                  (0, 0, 0),
                                  thickness=2)

        images1 = np.hstack((c_resized, d_resized))
        images2 = np.hstack((c_o_resized, a_o_resized))
        images_final = np.vstack((images1, images2))

        pc_resized = cv2.resize(self.point_cloud, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        pc_resized = cv2.putText(pc_resized, f'Point Cloud {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                 (0, 0, 0),
                                 thickness=2)
        pc_hull_resized = cv2.resize(self.point_cloud_hull, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        pc_hull_resized = cv2.putText(pc_hull_resized, f'Cloud Frame {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                      1,
                                      (0, 0, 0), thickness=2)
        angles_image_personal_resized = cv2.resize(self.angles_image_personal, None, fx=CONFIG.VIEW_SCALE,
                                                   fy=CONFIG.VIEW_SCALE)
        angles_image_personal_resized = cv2.putText(angles_image_personal_resized, f'Personal {frame_number}', (2, 30),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                                    thickness=2)
        angles_image_relative_resized = cv2.resize(self.angles_image_relative, None, fx=CONFIG.VIEW_SCALE,
                                                   fy=CONFIG.VIEW_SCALE)
        angles_image_relative_resized = cv2.putText(angles_image_relative_resized, f'Relative {frame_number}', (2, 30),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),
                                                    thickness=2)
        images3 = np.hstack((pc_resized, pc_hull_resized))
        images4 = np.hstack((angles_image_personal_resized, angles_image_relative_resized))
        images_final_2 = np.vstack((images3, images4))
        
        
        k_id_resized = cv2.resize(self.keypoints_ids, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        k_id_resized = cv2.putText(k_id_resized, f'Keypoint IDs {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                 (0, 0, 0),
                                 thickness=2)
        p_id_resized = cv2.resize(self.person_ids, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        p_id_resized = cv2.putText(p_id_resized, f'Person IDs {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                 (0, 0, 0),
                                 thickness=2)
        
        p_age_gender_resized = cv2.resize(self.age_gender, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
        p_age_gender_resized = cv2.putText(p_age_gender_resized, f'Age and Gender {frame_number}', (2, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                 (0, 0, 0),
                                 thickness=2)
        
        images5 = np.hstack((k_id_resized, p_id_resized))
        images6 = np.hstack((c_resized, p_age_gender_resized))

        images_final_3 = np.vstack((images5, images6))

        key = cv2.waitKey(CONFIG.FRAME_WAIT_TIME_MS)

        if CONFIG.SAVE_OUTPUTS_IMAGES:
            if not os.path.exists(CONFIG.OUTPUT_IMAGE_PATH_1):
                os.makedirs(CONFIG.OUTPUT_IMAGE_PATH_1)
            if not os.path.exists(CONFIG.OUTPUT_IMAGE_PATH_2):
                os.makedirs(CONFIG.OUTPUT_IMAGE_PATH_2)
            if not os.path.exists(CONFIG.OUTPUT_IMAGE_PATH_3):
                os.makedirs(CONFIG.OUTPUT_IMAGE_PATH_3)
            path1 = f'{CONFIG.OUTPUT_IMAGE_PATH_1}output_{frame_number}.jpg'
            cv2.imwrite(path1, images_final)
            path2 = f'{CONFIG.OUTPUT_IMAGE_PATH_2}output_{frame_number}.jpg'
            cv2.imwrite(path2, images_final_2)
            path3 = f'{CONFIG.OUTPUT_IMAGE_PATH_3}output_{frame_number}.jpg'
            cv2.imwrite(path3, images_final_3)
