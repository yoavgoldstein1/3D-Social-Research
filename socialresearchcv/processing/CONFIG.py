import os

from socialresearchcv.analysis.CONSTANTS import CONSTANTS

try:
    import pyrealsense2 as rs2
except:
    print("pyrealsense2 not available, skipping. If you need it please install it")
import subprocess


class CONFIG:
    """This handles global configuration on processing algorithm
    """
    ##CLASS CLOUD VARIABLES##
    VERBOSE = False
    CLEAR_DATA_ON_RUN = True
    USE_AWS = False
    USE_GCP = True

    ##CLASS VARIABLES
    SAVE_OUTPUTS_IMAGES = True
    SAVE_OPENPOSE_IMAGES = False
    SAVE_OUTPUT_VIDEOS = True
    LOG_TO_CSV = True

    CONFIDENCE_THRESHOLD = 0.25
    VIEW_SCALE = 0.5
    BLUR_FACES = True
    HISTORY_SIZE = 25
    EXTRACT_AGE_GENDER = False

    DEPTH_SAMPLE_RECT = 10
    MILIMETERS_IN_METERS = 1000
    WIDTH = 656
    HEIGHT = 368
    FRAME_WAIT_TIME_MS = 1
    FPS = 15
    OPENPOSE_BUILD_PATH = '/openpose/build/examples/openpose/'

    SAVE_KEYPOINTS = True
    LOAD_FROM_FILE = True
    LOAD_KEYPOINTS_FROM_FILE = False
    SAVE_TO_PNG = True

    ##PROPERTIES##
    INPUTS_FOLDER = 'Inputs/'
    DRIVE_PATH = "" + INPUTS_FOLDER
    BAG_NAME = [DRIVE_PATH + "", "", 0, 240, 100]
    STEPS = [i for i in range(BAG_NAME[2], BAG_NAME[3], BAG_NAME[4])]
    STEPS.append(STEPS[-1] + BAG_NAME[3] % BAG_NAME[4])
    DIR_PATH = BAG_NAME[0]
    IMAGES_DIR = BAG_NAME[1]

    ##PATHS##
    RECORDING_PATH = 'Outputs/Data.pkl'
    COLOR_VIDEO_PATH = 'Outputs/color.pkl'
    PNG_PATH_COLOR = f'Outputs/{IMAGES_DIR}/color'
    PNG_PATH_DEPTH = f'Outputs/{IMAGES_DIR}/depth'
    PNG_PATH_RENDERED = f'Outputs/{IMAGES_DIR}/outputImages'
    KEYPOINTS_PATH = f'Outputs/{IMAGES_DIR}/keypoints'
    KEYPOINTS_PROJECTED_PATH = f'Outputs/{IMAGES_DIR}/keypoints_projected'
    RAW_DEPTH_PATH = f'Outputs/{IMAGES_DIR}/raw_depth'
    DEPTH_COLORMAP_PATH = f'Outputs/{IMAGES_DIR}/depth_colormap'
    OUTPUT_IMAGE_PATH_1 = f'Outputs/{IMAGES_DIR}/output1/'
    OUTPUT_IMAGE_PATH_2 = f'Outputs/{IMAGES_DIR}/output2/'
    OUTPUT_IMAGE_PATH_3 = f'Outputs/{IMAGES_DIR}/output3/'

    DEPTH_RAW_VIDEO_PATH = f'Outputs/{IMAGES_DIR}/raw_depth/depth_raw'
    DEPTH_COLORMAP_VIDEO_PATH = f'Outputs/{IMAGES_DIR}/depth_colormap/depth_colormap'
    OUT_FILE_NAME_1 = f'{BAG_NAME[1]}_{BAG_NAME[2]}_{BAG_NAME[3]}_1'
    OUT_FILE_NAME_2 = f'{BAG_NAME[1]}_{BAG_NAME[2]}_{BAG_NAME[3]}_2'
    OUT_FILE_NAME_3 = f'{BAG_NAME[1]}_{BAG_NAME[2]}_{BAG_NAME[3]}_3'
    OUT_PATH_1 = os.path.join('Outputs', IMAGES_DIR, OUT_FILE_NAME_1)
    OUT_PATH_2 = os.path.join('Outputs', IMAGES_DIR, OUT_FILE_NAME_2)
    OUT_PATH_3 = os.path.join('Outputs', IMAGES_DIR, OUT_FILE_NAME_3)
    CSV_PATH = f'Outputs/{IMAGES_DIR}/{BAG_NAME[1]}'

    ##CONSTANTS##
    JOINT_NAMES_DICT = CONSTANTS.JOINT_NAMES_DICT

    @staticmethod
    def refresh_values():
        CONFIG.update_values()
        CONFIG.update_paths()

    @staticmethod
    def update_values():
        CONFIG.DRIVE_PATH = "" + CONFIG.INPUTS_FOLDER
        CONFIG.STEPS = [i for i in range(CONFIG.BAG_NAME[2], CONFIG.BAG_NAME[3], CONFIG.BAG_NAME[4])]
        CONFIG.STEPS.append(CONFIG.STEPS[-1] + CONFIG.BAG_NAME[3] % CONFIG.BAG_NAME[4])
        CONFIG.DIR_PATH = CONFIG.BAG_NAME[0]
        CONFIG.IMAGES_DIR = CONFIG.BAG_NAME[1]

    @staticmethod
    def update_paths():
        print('Updating paths')
        CONFIG.RECORDING_PATH = 'Outputs/Data.pkl'
        CONFIG.COLOR_VIDEO_PATH = 'Outputs/color.pkl'
        # DEPTH_RAW_VIDEO_PATH = 'Outputs/depth_raw.pkl'
        # DEPTH_COLORMAP_VIDEO_PATH = 'Outputs/depth_colormap.pkl'
        CONFIG.PNG_PATH_COLOR = f'Outputs/{CONFIG.IMAGES_DIR}/color'
        CONFIG.PNG_PATH_DEPTH = f'Outputs/{CONFIG.IMAGES_DIR}/depth'
        CONFIG.PNG_PATH_RENDERED = f'Outputs/{CONFIG.IMAGES_DIR}/outputImages'
        CONFIG.KEYPOINTS_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/keypoints'
        CONFIG.KEYPOINTS_PROJECTED_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/keypoints_projected'
        CONFIG.RAW_DEPTH_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/raw_depth'
        CONFIG.DEPTH_COLORMAP_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/depth_colormap'
        CONFIG.OUTPUT_IMAGE_PATH_1 = f'Outputs/{CONFIG.IMAGES_DIR}/output1/'
        CONFIG.OUTPUT_IMAGE_PATH_2 = f'Outputs/{CONFIG.IMAGES_DIR}/output2/'
        CONFIG.OUTPUT_IMAGE_PATH_3 = f'Outputs/{CONFIG.IMAGES_DIR}/output3/'

        CONFIG.DEPTH_RAW_VIDEO_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/raw_depth/depth_raw'
        CONFIG.DEPTH_COLORMAP_VIDEO_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/depth_colormap/depth_colormap'
        CONFIG.OUT_FILE_NAME_1 = f'{CONFIG.BAG_NAME[1]}_{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_1'
        CONFIG.OUT_FILE_NAME_2 = f'{CONFIG.BAG_NAME[1]}_{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_2'
        CONFIG.OUT_FILE_NAME_3 = f'{CONFIG.BAG_NAME[1]}_{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_3'
        CONFIG.OUT_PATH_1 = os.path.join('Outputs', CONFIG.IMAGES_DIR, CONFIG.OUT_FILE_NAME_1)
        CONFIG.OUT_PATH_2 = os.path.join('Outputs', CONFIG.IMAGES_DIR, CONFIG.OUT_FILE_NAME_2)
        CONFIG.OUT_PATH_3 = os.path.join('Outputs', CONFIG.IMAGES_DIR, CONFIG.OUT_FILE_NAME_3)
        CONFIG.CSV_PATH = f'Outputs/{CONFIG.IMAGES_DIR}/{CONFIG.BAG_NAME[1]}'
        print('Configuration paths updated')

    @staticmethod
    def get_input_filenames():
        final_video_path1 = CONFIG.OUT_PATH_1 + ".mp4"
        final_video_path2 = CONFIG.OUT_PATH_2 + ".mp4"

        final_name_1 = f'{CONFIG.BAG_NAME[1]}/{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_1_Final.mp4'
        final_name_2 = f'{CONFIG.BAG_NAME[1]}/{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_2_Final.mp4'
        final_name_3 = f'{CONFIG.BAG_NAME[1]}/{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_3_Final.mp4'

        final_csv_path = f'{CONFIG.OUT_PATH_1}.csv'
        final_csv_name = f'{CONFIG.BAG_NAME[1]}/{CONFIG.BAG_NAME[2]}_{CONFIG.BAG_NAME[3]}_Final.csv'

        return final_csv_name, final_name_1, final_name_2, final_name_3

    @staticmethod
    def get_number_of_frames():
        '''Runs the video and fetches the number of frames using librealsense.'''
        pipeline = rs2.pipeline()
        config = rs2.config()
        stream = rs2.stream.depth
        config.disable_all_streams()
        config.enable_stream(stream)
        config.enable_device_from_file(CONFIG.DIR_PATH, repeat_playback=False)
        profile = pipeline.start(config)
        playback = profile.get_device().as_playback()
        frame = rs2.composite_frame(rs2.frame())
        n = 0
        playback.resume()

        try:
            while playback.current_status() == rs2.playback_status.playing:
                frameset = pipeline.wait_for_frames()
                n += 1
        except:
            print(f'There are {n} {stream} frames in this bag.')
        finally:
            return n

    @staticmethod
    def get_openpose_run_command():
        '''Obtains run command for openpose depends on the SAVE_OUTPUT_VIDEOS flag.'''
        print(f'Creating openpose videos flag is: {CONFIG.SAVE_OPENPOSE_IMAGES}')

        if CONFIG.SAVE_OPENPOSE_IMAGES:
            run_command = f'--render_pose 1 ' \
                          f'--image_dir ..\/{CONFIG.PNG_PATH_COLOR} ' \
                          f'--write_json ..\/{CONFIG.KEYPOINTS_PATH} ' \
                          f'--write_images ..\/{CONFIG.PNG_PATH_RENDERED} ' \
                          f'--tracking 1 ' \
                          f'--model_pose BODY_21A ' \
                          f'--display 0 '
        else:
            run_command = f'--render_pose 0 ' \
                          f'--image_dir ..\/{CONFIG.PNG_PATH_COLOR} ' \
                          f'--write_json ..\/{CONFIG.KEYPOINTS_PATH} ' \
                          f'--tracking 1 ' \
                          f'--model_pose BODY_21A ' \
                          f'--display 0 '
        return run_command
