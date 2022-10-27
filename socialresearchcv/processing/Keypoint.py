class Keypoint:

    def __init__(self, frameID, bodyID, image_set, raw_keypoints, pose_viewer):
        """Initializes a new keypoint object

        Args:
            frameID (int): associated frame
            bodyID (int): associated body
            image_set (ImageSet): set of corresponding images
            raw_keypoints (list): list of detected keypoints
            pose_viewer (_type_): _description_
        """
        self.keypoint_frame_id = frameID
        self.keypoint_body_id = bodyID
        self.keypoint_color_image = image_set.color
        self.keypoint_depth_image = image_set.depth_image
        self.keypoint_depth_colormap = image_set.depth_colormap
        self.keypoint_raw = raw_keypoints
        self.pose_viewer = pose_viewer
        self.keypoint_joints_2d = dict()
        self.keypoint_joints_3d = dict()
        self.add_joints()

    def add_joints(self):
        """Add to 2D and 3D joints
        """
        for i in range(0, len(self.keypoint_raw) // 3):

            p_2d = [int(self.keypoint_raw[3 * i]), int(self.keypoint_raw[3 * i + 1]), self.keypoint_raw[3 * i + 2]]
            self.keypoint_joints_2d[i] = p_2d

            p_3d = self.pose_viewer.get_world_point(p_2d, self.keypoint_depth_image)
            p_3d[2] = int(p_3d[2])
            self.keypoint_joints_3d[i] = p_3d


    def show_keypoint(self, joint_id):
        """Visualize the keypoint

        Args:
            joint_id (int): keypoint to visualize

        Returns:
            image, image: Visualized images
        """
        point = self.keypoint_joints_2d[joint_id]
        self.keypoint_color_image, self.keypoint_depth_colormap, _ =  self.pose_viewer.ShowPoint(point,self.keypoint_depth_image, self.keypoint_depth_colormap,
                                                                self.keypoint_color_image)
        return self.keypoint_color_image, self.keypoint_depth_colormap, _



