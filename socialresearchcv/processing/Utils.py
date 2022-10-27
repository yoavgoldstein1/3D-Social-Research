import pickle

import cv2
import numpy as np
import os
from socialresearchcv.processing.CONFIG import CONFIG

def clear_directory(current_dir):
    print(f'Removing contents of {current_dir}')

    if CONFIG.CLEAR_DATA_ON_RUN:
        os.system(f'rm -rf {current_dir}/keypoints_projected')
        os.system(f'rm -rf {current_dir}/color')
        os.system(f'rm -rf {current_dir}/depth')

        os.system(f'rm -rf {current_dir}/outputImages')
        os.system(f'rm -rf {current_dir}/keypoints')

        os.system(f'rm -rf {current_dir}/raw_depth')
        os.system(f'rm -rf {current_dir}/depth_colormap')
        os.system(f'rm -rf {current_dir}/../*.pkl')


        os.system(f'rm -rf {current_dir}/output1')
        os.system(f'rm -rf {current_dir}/output2')
        os.system(f'rm -rf {current_dir}/output3')

        os.system(f'rm -rf {current_dir}/out')
        os.system(f'rm -rf {current_dir}/*.pkl')
        os.system(f'rm -rf {current_dir}/*.avi')
        os.system(f'rm -rf {current_dir}/*.txt')
    print('Done')
    
    
def merge_csvs():
    current_dir = f'Outputs/{CONFIG.BAG_NAME[1]}'
    final_csv_path = f'{CONFIG.OUT_PATH_1}.csv'
    with open(final_csv_path, 'w') as f:
        for ind,i in enumerate(CONFIG.STEPS[:-1]):
            step = CONFIG.STEPS[ind+1]-i
            current_csv_path = os.path.join(current_dir, f'{CONFIG.BAG_NAME[1]}_{i}_{i+step}.csv')
            with open(current_csv_path, 'r') as f2:
                f.write(f2.read()) 
                
    print(f'CSV files merged succesfully to: {CONFIG.OUT_PATH_1}.csv')
                
def merge_videos():
    if CONFIG.SAVE_OUTPUT_VIDEOS:
        paths1 = []
        paths2 = []
        paths3 = []

        for ind,i in enumerate(CONFIG.STEPS[:-1]):
            step = CONFIG.STEPS[ind+1]-i
            path1 = 'file \''+f'outVideo1_{i}_{i+step}.avi\''
            path2 = 'file \''+f'outVideo2_{i}_{i+step}.avi\''
            path3 = 'file \''+f'outVideo3_{i}_{i+step}.avi\''
            paths1.append(path1)
            paths2.append(path2)
            paths3.append(path3)
            
        combined_path_text1 = os.path.join('Outputs',CONFIG.IMAGES_DIR,'videoPaths1.txt');
        combined_path_text2 = os.path.join('Outputs',CONFIG.IMAGES_DIR,'videoPaths2.txt');
        combined_path_text3 = os.path.join('Outputs',CONFIG.IMAGES_DIR,'videoPaths3.txt');

        os.system(f'rm -rf {combined_path_text1}')
        os.system(f'rm -rf {combined_path_text2}')
        os.system(f'rm -rf {combined_path_text3}')
        
        os.system(f'rm -rf {CONFIG.OUT_PATH_1}.avi')
        os.system(f'rm -rf {CONFIG.OUT_PATH_2}.avi')
        os.system(f'rm -rf {CONFIG.OUT_PATH_3}.avi')

        with open(combined_path_text1, 'w') as f:
            for item in paths1:
                f.write("%s\n" % item)

        with open(combined_path_text2, 'w') as f:
            for item in paths2:
                f.write("%s\n" % item)
                
        with open(combined_path_text3, 'w') as f:
            for item in paths3:
                f.write("%s\n" % item)
                
        if os.system(f'ffmpeg -f concat -safe 0 -i {combined_path_text1} -c copy {CONFIG.OUT_PATH_1}.avi'): 
            print(f'Failed to create mp4: {CONFIG.OUT_PATH_1}.avi')

        if os.system(f'ffmpeg -f concat -safe 0 -i {combined_path_text2} -c copy {CONFIG.OUT_PATH_2}.avi'):
            print(f'Failed to create avi: {CONFIG.OUT_PATH_2}.avi')
            
        if os.system(f'ffmpeg -f concat -safe 0 -i {combined_path_text3} -c copy {CONFIG.OUT_PATH_3}.avi'):
            print(f'Failed to create avi: {CONFIG.OUT_PATH_3}.avi')

        if os.system(f'ffmpeg -y -i {CONFIG.OUT_PATH_1}.avi {CONFIG.OUT_PATH_1}.mp4'):
            print(f'Failed to create mp4: {CONFIG.OUT_PATH_1}.mp4')
            
        if os.system(f'ffmpeg -y -i {CONFIG.OUT_PATH_2}.avi {CONFIG.OUT_PATH_2}.mp4'):
            print(f'Failed to create mp4: {CONFIG.OUT_PATH_2}.mp4')
            
        if os.system(f'ffmpeg -y -i {CONFIG.OUT_PATH_3}.avi {CONFIG.OUT_PATH_3}.mp4'):
            print(f'Failed to create mp4: {CONFIG.OUT_PATH_3}.mp4')
            
        print(f'Videos merged successfuly to: {CONFIG.OUT_PATH_1}.mp4')
        print(f'Videos merged successfuly to: {CONFIG.OUT_PATH_2}.mp4')
        print(f'Videos merged successfuly to: {CONFIG.OUT_PATH_3}.mp4')



        
def sample_depth(p, depth_image):
    x, y = int(p[0]), int(p[1])
    x_range = range(x - CONFIG.DEPTH_SAMPLE_RECT, x + CONFIG.DEPTH_SAMPLE_RECT)
    y_range = range(y - CONFIG.DEPTH_SAMPLE_RECT, y + CONFIG.DEPTH_SAMPLE_RECT)
    if x - CONFIG.DEPTH_SAMPLE_RECT < 0 or \
            x + CONFIG.DEPTH_SAMPLE_RECT > depth_image.shape[1] or \
            y - CONFIG.DEPTH_SAMPLE_RECT < 0 or \
            y + CONFIG.DEPTH_SAMPLE_RECT > depth_image.shape[0] or \
            p[2] < CONFIG.CONFIDENCE_THRESHOLD:
        return None

    d_vals = [depth_image[int(y_val), int(x_val)] for x_val, y_val in zip(x_range, y_range)]
    filter(lambda a: a[0] != 0 and a[1] != 0, d_vals)
    # print(d_vals)
    d = np.median(d_vals)

    return d

def blur_face(target_image, kepoints_list):

    keypoint = kepoints_list[1]
    p1 = kepoints_list[0]
    p2 = kepoints_list[1]
    a = np.array([p1[0],p1[1]])
    b = np.array([p2[0],p2[1]])
    dist = np.linalg.norm(a-b)
    edge = int(dist/2)+4
    color = (255, 255, 255) 
    thickness = 8
    kp = p1
    start_point = (kp[0]-edge, kp[1]-edge) 
    end_point = (kp[0]+edge, kp[1]+edge)
    
    blurred_img = cv2.GaussianBlur(target_image, (25, 25), 15)
    mask = np.zeros(target_image.shape, dtype=np.uint8)
    mask = cv2.circle(mask, (kp[0],kp[1]), edge, color, -1)

    out = np.where(mask!=np.array([255, 255, 255]), target_image, blurred_img)
    
    return out


class VideoExporter():
    def __init__(self, videp_path, image_format='RGB', start_frame=0, end_frame=0):
        self.fps = 1
        self.images = []
        self.videp_path = f'{videp_path}_{start_frame}_{end_frame}.pkl'
        self.image_format = image_format

    def add_image(self, image):
        self.images.append(image)

    def save_images(self):
        images = self.images
        height = images[0].shape[0]
        width = images[0].shape[1]
        size = (width, height)
        out = cv2.VideoWriter(self.videp_path, cv2.VideoWriter_fourcc(*'DIVX'), self.fps, size)
        count = 0
        if self.image_format == 'RGB':
            for i in range(len(images)):
                # writing to a image array
                out.write(images[i])
                count += 1
            print(f'Saved {count} images with format={self.image_format} to {self.videp_path}')
        elif self.image_format == 'DEPTH' or self.image_format == 'COLOR':
            with open(self.videp_path, 'wb') as file:
                pickle.dump(self.images, file)
            print(f'Saved {len(self.images)} images with format={self.image_format} to {self.videp_path}')

        out.release()

    def load_images(self):
        if self.image_format == 'RGB':
            vidcap = cv2.VideoCapture(self.videp_path)

            def getFrame(sec):
                hasFrames, image = vidcap.read()
                if hasFrames:
                    self.images.append(image)
                return hasFrames

            sec = 1
            frameRate = 0.5  # //it will capture image in each 0.5 second
            count = 1
            success = getFrame(sec)
            while success:
                success = getFrame(sec)
        elif self.image_format == 'DEPTH' or self.image_format == 'COLOR':
            with (open(self.videp_path, 'rb')) as file:
                self.images = pickle.load(file)

    def pop_image(self):
        return self.images.pop(0)


class DatumData:
    def __init__(self, datum):
        if datum is not None:
            self.poseKeypoints = datum.poseKeypoints
            # self.cvOutputData = np.copy(datum.cvOutputData.copy())
            self.poseScores = datum.poseScores
            # self.frameNumber = datum.frameNumber
            self.dump_file_path = None

    def add_save_path(self, dump_file_path):
        self.dump_file_path = dump_file_path


class DatumList:

    def __init__(self, save_path):
        self.datum_list = []
        self.color_images = []
        self.depth_images = []
        self.save_path = save_path

    def add_datum(self, new_datum):
        self.datum_list.append(new_datum)

    def save_all(self):
        with open(self.save_path, 'wb') as file:
            for d in self.datum_list:
                pickle.dump(d.poseKeypoints, file)
                pickle.dump(d.poseScores, file)
        print(f"Saved {len(self.datum_list)} elements to {self.save_path}")

    def open_from_file(self):
        with (open(self.save_path, 'rb')) as file:
            while True:
                try:
                    d = DatumData(datum=None)
                    d.poseKeypoints = pickle.load(file)
                    d.poseScores = pickle.load(file)
                    self.datum_list.append(d)
                except EOFError:
                    break
        print(f'Loaded {len(self.datum_list)} keypoints from {self.save_path}')


    def pop_datum(self):
        return self.datum_list.pop(0)
    
    