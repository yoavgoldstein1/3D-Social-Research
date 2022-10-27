import pickle
import sys
import traceback

import cv2
import os
from sys import platform
import argparse
import time

import numpy as np
import pyrealsense2 as rs

from socialresearchcv.processing.CONFIG import CONFIG

# Import Openpose (Windows/Ubuntu/OSX)
from socialresearchcv.processing.CSVWriter import CSVWriter
from socialresearchcv.processing.PoseViewer import PoseViewer
from socialresearchcv.processing.Utils import VideoExporter, DatumData

index = 0


def draw_images(color_im, depth_im):
    c_resized = cv2.resize(color_im, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)
    d_resized = cv2.resize(depth_im, None, fx=CONFIG.VIEW_SCALE, fy=CONFIG.VIEW_SCALE)

    images = np.hstack((c_resized, d_resized))
    cv2.imshow("Poses Output with Depth", images)
    key = cv2.waitKey(15)


def get_native_datum(op, color_image):
    datumNative = op.Datum()
    # Convert to opencv format
    color_image = cv2.cvtColor(np.array(color_image), cv2.COLOR_RGB2BGR)
    datumNative.cvInputData = color_image
    opWrapper.emplaceAndPop([datumNative])
    return datumNative


def run_all(max_frames, start_frame=0, end_frame=0, progress_bar=None):
    global opWrapper
    global index
    index = start_frame

    # Tracker = SkeletonTracker()
    try:
        if not CONFIG.LOAD_KEYPOINTS_FROM_FILE:
            dir_path = '../build'
            try:
                # Windows Import
                if platform == "win32":
                    # Change these variables to point to the correct folder (Release/x64 etc.)
                    os.environ['PATH'] = os.environ[
                                             'PATH'] + ';' + dir_path + '/../openpose_tracking/build/x64/Release;' + dir_path + '/../openpose_tracking/build/bin;'
                    # print(dir_path)
                    import pyopenpose as op
                else:
                    # Change these variables to point to the correct folder (Release/x64 etc.)
                    # sys.path.append('<YOUR PATH>/build/python');
                    # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
                    sys.path.append('../../../usr/local/python/')  # for colab
                    from openpose import pyopenpose as op
            except ImportError as e:
                print(
                    'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
                raise e

            # Flags
            parser = argparse.ArgumentParser()
            parser.add_argument("--image_dir", default="../../../examples/media/",
                                help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
            parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
            args = parser.parse_known_args()

            # Custom Params (refer to include/openpose/flags.hpp for more parameters)
            params = dict()
            params["model_folder"] = "/content/openpose/models"
            params["model_pose"] = "BODY_25"

            # Add others in path?
            for i in range(0, len(args[1])):
                curr_item = args[1][i]
                if i != len(args[1]) - 1:
                    next_item = args[1][i + 1]
                else:
                    next_item = "1"
                if "--" in curr_item and "--" in next_item:
                    key = curr_item.replace('-', '')
                    if key not in params:  params[key] = "1"
                elif "--" in curr_item and "--" not in next_item:
                    key = curr_item.replace('-', '')
                    if key not in params: params[key] = next_item

            opWrapper = op.WrapperPython()
            opWrapper.configure(params)
            opWrapper.start()
        else:
            curr_color_writer = VideoExporter(CONFIG.COLOR_VIDEO_PATH, image_format='COLOR', start_frame=start_frame,
                                              end_frame=end_frame)
            curr_color_writer.load_images()
            curr_depth_raw_writer = VideoExporter(CONFIG.DEPTH_RAW_VIDEO_PATH, image_format='DEPTH',
                                                  start_frame=start_frame, end_frame=end_frame)
            curr_depth_raw_writer.load_images()
            curr_depth_colormap_writer = VideoExporter(CONFIG.DEPTH_COLORMAP_VIDEO_PATH, image_format='DEPTH',
                                                       start_frame=start_frame, end_frame=end_frame)
            curr_depth_colormap_writer.load_images()

        if CONFIG.SAVE_KEYPOINTS:
            curr_color_writer = VideoExporter(CONFIG.COLOR_VIDEO_PATH, image_format='COLOR', start_frame=start_frame,
                                              end_frame=end_frame)
            curr_depth_raw_writer = VideoExporter(CONFIG.DEPTH_RAW_VIDEO_PATH, image_format='DEPTH',
                                                  start_frame=start_frame, end_frame=end_frame)
            curr_depth_colormap_writer = VideoExporter(CONFIG.DEPTH_COLORMAP_VIDEO_PATH, image_format='DEPTH',
                                                       start_frame=start_frame, end_frame=end_frame)

        pipeline = rs.pipeline()
        config = rs.config()

        if CONFIG.LOAD_FROM_FILE:
            config.enable_device_from_file(CONFIG.DIR_PATH)
        else:
            config.enable_stream(rs.stream.pose)

        profile = pipeline.start(config)
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)
        start = time.time()

        # Get stream profile and camera intrinsics
        profile = pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        depth_intrinsics = depth_profile.get_intrinsics()
        w, h = depth_intrinsics.width, depth_intrinsics.height

        pose_viewer = PoseViewer(intrinsics=depth_intrinsics)
        csv_writer = CSVWriter(path=CONFIG.CSV_PATH)
        last_datum = None
        start = time.time()

        ind = 0
        while True:
            ind += 1

            frames = pipeline.wait_for_frames()
            if not CONFIG.SAVE_KEYPOINTS:
                time.sleep(1 / CONFIG.FPS)
            if ind < start_frame:
                continue

            align_to = rs.stream.color
            align = rs.align(align_to)

            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            if CONFIG.SAVE_TO_PNG:

                if os.listdir(CONFIG.PNG_PATH_COLOR) and index is 0:
                    sys.exit(f'Path {CONFIG.PNG_PATH_COLOR} for color is not empty')
                if os.listdir(CONFIG.PNG_PATH_DEPTH) and index is 0:
                    sys.exit(f'Path {CONFIG.PNG_PATH_DEPTH} for depth is not empty')

                color_image = cv2.cvtColor(np.array(color_image), cv2.COLOR_RGB2BGR)
                cv2.imwrite(f'{CONFIG.PNG_PATH_COLOR}/color_{index}.png', color_image)
                cv2.imwrite(f'{CONFIG.PNG_PATH_DEPTH}/depth_{index}.png', depth_image)

            index += 1

            if progress_bar is not None:
                progress_bar.set_description(f'Working on frame {index}')
                progress_bar.update(1)

            if CONFIG.LOAD_KEYPOINTS_FROM_FILE:
                curr_time = time.time()
                start = time.time()
                datum = DatumData(None)
                datum.add_save_path(CONFIG.RECORDING_PATH)
                keypoints = datum.poseKeypoints
                out_image = curr_color_writer.pop_image()
                depth_image = curr_depth_raw_writer.pop_image()
                depth_colormap = curr_depth_colormap_writer.pop_image()
                pose_scores = datum.poseScores
            else:
                datumNative = get_native_datum(op, color_image)
                datum = DatumData(datum=datumNative)
                keypoints = datum.poseKeypoints
                out_image = datumNative.cvOutputData
                pose_scores = datum.poseScores

            res_datum = datum

            if res_datum is not None:
                datum = res_datum

            last_datum = datum

            points = []
            labels = []
            poseIDs = []

            if CONFIG.SAVE_KEYPOINTS:
                datum.add_save_path(CONFIG.RECORDING_PATH)
                curr_color_writer.add_image(datumNative.cvOutputData)
                curr_depth_raw_writer.add_image(depth_image.copy())
                curr_depth_colormap_writer.add_image(depth_colormap.copy())

                if ind > max_frames:  # if key 'q' is pressed
                    print('You Pressed Save Key (S)!')
                    curr_color_writer.save_images()
                    curr_depth_raw_writer.save_images()
                    curr_depth_colormap_writer.save_images()
                    return

            if datum.poseKeypoints is None:
                draw_images(out_image, depth_colormap)
                continue

            if len(keypoints.shape) == 0:
                continue

            for body, poseID in zip(keypoints, range(0, len(keypoints))):
                if body[1][0] != 0 and body[1][0]:  # Take neck key points
                    points.append(body[1])
                if body[0][0] != 0 and body[0][0]:  # Take Head point for id visualization
                    labels.append(body[0])
                poseIDs.append(poseID)  # Take all pose IDs
                world_parts = [pose_viewer.get_world_point(p, depth_image) for p in body]

            key = cv2.waitKey(1)
            if key == 27: break

    except Exception as e:
        traceback.print_exc()
        sys.exit(-1)


def save_bag_to_images(max_frames, start_frame=0, end_frame=0, progress_bar=None):
    index = start_frame

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(CONFIG.DIR_PATH)
    profile = pipeline.start(config)

    playback = profile.get_device().as_playback()
    playback.set_real_time(False)
    start = time.time()

    profile = pipeline.get_active_profile()
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
    depth_intrinsics = depth_profile.get_intrinsics()
    w, h = depth_intrinsics.width, depth_intrinsics.height

    curr_depth_raw_writer = VideoExporter(CONFIG.DEPTH_RAW_VIDEO_PATH, image_format='DEPTH', start_frame=start_frame,
                                          end_frame=end_frame)
    curr_depth_colormap_writer = VideoExporter(CONFIG.DEPTH_COLORMAP_VIDEO_PATH, image_format='DEPTH',
                                               start_frame=start_frame, end_frame=end_frame)
    ind = 0
    while True:
        ind += 1
        frames = pipeline.wait_for_frames()

        if ind < start_frame:
            continue

        align_to = rs.stream.color
        align = rs.align(align_to)
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        color_image = cv2.cvtColor(np.array(color_image), cv2.COLOR_RGB2BGR)
        cv2.imwrite(f'{CONFIG.PNG_PATH_COLOR}/color_{index}.png', color_image)
        cv2.imwrite(f'{CONFIG.PNG_PATH_DEPTH}/depth_{index}.png', depth_image)

        with (open(f'{CONFIG.DEPTH_RAW_VIDEO_PATH}_{index}.pkl', 'wb')) as file:
            pickle.dump(depth_image.copy(), file)
        with (open(f'{CONFIG.DEPTH_COLORMAP_VIDEO_PATH}_{index}.pkl', "wb")) as file:
            pickle.dump(depth_colormap.copy(), file)

        index += 1

        if ind > max_frames:
            return


if __name__ == '__main__':
    run_all(max_frames=100)
