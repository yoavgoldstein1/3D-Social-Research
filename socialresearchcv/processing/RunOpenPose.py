import os
from os import path

from socialresearchcv.processing import FeatureCSVRecorder
from socialresearchcv.processing.CONFIG import CONFIG
from socialresearchcv.processing.FeatureCSVRecorder import run_all


class OPRunner:
    @staticmethod
    def check_folders(folder_list):
        for folder in folder_list:
            if not path.isdir(path.realpath(folder)):
                print(f'creating folder in: {folder}')
                os.makedirs(folder)

    @staticmethod
    def run_all(start_index, end_index, progress_bar=None):

        dir_list = [CONFIG.PNG_PATH_COLOR, CONFIG.PNG_PATH_DEPTH, CONFIG.PNG_PATH_RENDERED, CONFIG.KEYPOINTS_PATH,
                    CONFIG.KEYPOINTS_PROJECTED_PATH, CONFIG.RAW_DEPTH_PATH, CONFIG.DEPTH_COLORMAP_PATH]

        OPRunner.check_folders(dir_list)

        FeatureCSVRecorder.save_bag_to_images(max_frames=end_index, start_frame=start_index, end_frame=end_index,
                                              progress_bar=progress_bar)


if __name__ == '__main__':
    run_all()
