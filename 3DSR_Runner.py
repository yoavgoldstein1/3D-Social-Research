import subprocess
import sys
from socialresearchcv.processing.CONFIG import CONFIG
from socialresearchcv.processing.InteractionAnalyzer import InteractionAn
from socialresearchcv.processing.RunOpenPose import OPRunner
from socialresearchcv.processing.Utils import clear_directory
from socialresearchcv.processing.Utils import merge_csvs, merge_videos


class SocialResearchRunner:
    @staticmethod
    def run_loop(bag_names, bag_paths):
        for input_bag_name, bag_gs_path in zip(bag_names, bag_paths):

            # Set parameters for the generator
            CONFIG.BAG_NAME = [CONFIG.DRIVE_PATH + f'{input_bag_name}.bag', input_bag_name, 0, 150, 100]
            CONFIG.refresh_values()

            # Clear old files
            current_dir = f'Outputs/{CONFIG.BAG_NAME[1]}'
            clear_directory(current_dir)

            # Get number of total frames in video
            n = CONFIG.get_number_of_frames()
            CONFIG.BAG_NAME[3] = n - 1
            CONFIG.refresh_values()

            # Run openpose and depth processing
            OPRunner.run_all(start_index=0, end_index=CONFIG.BAG_NAME[3], progress_bar=None)

            # Run openpose on RG images
            run_command = CONFIG.get_openpose_run_command()
            batcmd = f'cd openpose && sudo ./build/examples/openpose/openpose.bin {run_command}'
            print(subprocess.check_output(batcmd, shell=True))
            print(f'Parsing Video:{CONFIG.BAG_NAME[1]}')

            # Run interaction analysis to create CSVs and visualizations
            for ind, i in enumerate(CONFIG.STEPS[:-1]):
                step = CONFIG.STEPS[ind + 1] - i
                InteractionAn.run(start_index=i, end_index=i + step, progress=None)

            merge_csvs()
            merge_videos()

            # Clear workspace
            clear_directory(current_dir)

if __name__ == '__main__':
    bag_names = sys.argv[1]
    bag_paths = sys.argv[2]
    CONFIG.SAVE_OUTPUT_VIDEOS = sys.argv[3] == 'True'
    CONFIG.SAVE_OPENPOSE_IMAGES = sys.argv[4] == 'True'
    CONFIG.CLEAR_DATA_ON_RUN = sys.argv[5] == 'True'
    CONFIG.refresh_values()
    SocialResearchRunner.run_loop([bag_names], [bag_paths])
