import csv
from socialresearchcv.processing.CONFIG import CONFIG

class CSVWriter:
    """This class manages the extraction of the data into CSV files
    """
    def __init__(self, path):
        """Init the writer

        Args:
            path (string): path of the file to write
        """
        self.path = path
        self.rows = []
        if CONFIG.LOG_TO_CSV:
            with open(self.path, 'w') as csvFile:
                # Write headers
                header = []
                header.append('FrameID')
                header.append('BodyID')
                header.append('Type')
                [header.append(f'Joint {joint + 1}') for joint in CONFIG.JOINT_NAMES_DICT.keys()]
                header.append('Distances')
                writer = csv.writer(csvFile)
                writer.writerow(header)
            csvFile.close()

    def add_row(self, row):
        """Adds a new row to the file

        Args:
            row (string): the row to write
        """
        if CONFIG.LOG_TO_CSV:
            self.rows.append(row)
            with open(self.path, 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(self.rows[-1])
            csvFile.close()

    def add_pose(self, world_parts, pose_id, frame_id, data_type, keypoint_id, distances=dict()):
        """Adds a new pose to the writer and adds it as a new row

        Args:
            world_parts (dictionary): list of keypoints in 3D space
            pose_id (int): the body number
            frame_id (int): frame number
            data_type (enum): type of data
            keypoint_id (int): keypoint number
            distances (_type_, optional): _description_. Defaults to dict().
        """
        if CONFIG.LOG_TO_CSV:
            row = []
            row.append(frame_id)
            row.append(pose_id)
            row.append(data_type)
            norm = CONFIG.MILIMETERS_IN_METERS
            for i in range(0,len(world_parts)):
                row.append(distances.get(i, 0)/norm)
            self.add_row(row)

    def add_poses(self, world_parts, pose_id, frame_id, data_type):
        """Adds multiple poses

        Args:
            world_parts (dictionary): list of keypoints in 3D space
            pose_id (int): the body number
            frame_id (int): frame number
            data_type (enum): type of data
        """
        if CONFIG.LOG_TO_CSV:
            row = []
            row.append(frame_id)
            row.append(pose_id)
            row.append(data_type)
            norm = CONFIG.MILIMETERS_IN_METERS
            [row.append(([b[0] / norm, b[1] / norm, b[2] / norm])) for b
             in world_parts]
            self.add_row(row)

    def add_keypoints2D(self, world_parts, pose_id, frame_id, data_type):
        """adds new keypoint info in 2D

        Args:
            world_parts (dictionary): list of keypoints in 3D space
            pose_id (int): the body number
            frame_id (int): frame number
            data_type (enum): type of data
        """
        if CONFIG.LOG_TO_CSV:
            row = []
            row.append(frame_id)
            row.append(pose_id)
            row.append(data_type)
            norm = 0.001
            [row.append(([b[0] / norm, b[1] / norm, b[2] / norm])) for b
             in world_parts]
            self.add_row(row)
            
    def add_age_gender_data(self, age_gender_data, pose_id, frame_id, data_type):
        """Adds age and gender data

        Args:
            age_gender_data (_type_): age and gender data
            pose_id (int): the body number
            frame_id (int): frame number
            data_type (enum): type of data
        """
        if CONFIG.LOG_TO_CSV:
            row = []
            row.append(frame_id)
            row.append(pose_id)
            row.append(data_type)
            for k in age_gender_data:
                row.append(f'{age_gender_data[k]}({k})')
            self.add_row(row)

    def add_empty_row(self, frame_index):
        """Adds a blank row

        Args:
            frame_index (int): frame index to add
        """
        row = []
        row.append(frame_index)
        self.add_row(row)
        
