import os
import pandas as pd
import socialresearchcv.analysis.Cleaner as clean
from socialresearchcv.analysis.AnalysisUtils import calculate_custom_distance
from socialresearchcv.analysis.CONSTANTS import CONSTANTS as CONSTANTS


def preprocess_files(titles):
    """
    Preprocess CSV files prior to R processing
    :param titles: path for the raw CSV files
    :return: None
    """
    # File names to read
    file_splits = [os.path.split(fn[0]) for fn in titles]

    # # Define input and output folders
    in_folder_prefix_list = [splits[0] for splits in file_splits]

    out_folder_prefix = 'Inputs/'
    # Files to write csv names into
    if not os.path.exists(out_folder_prefix):
        os.mkdir(out_folder_prefix)

    in_names = [f'{in_folder_prefix}/{os.path.splitext(fn[1])[0]}.csv' for in_folder_prefix, fn in
                zip(in_folder_prefix_list, file_splits)]
    out_names = [f'{out_folder_prefix}clean_{os.path.splitext(fn[1])[0]}.csv' for fn in file_splits]
    conf_names = [f'{out_folder_prefix}clean_{os.path.splitext(fn[1])[0]}_confidence.csv' for fn in file_splits]

    # Files to write csv names into
    if os.path.exists(f'{out_folder_prefix}csv_list.txt'):
        os.remove(f'{out_folder_prefix}csv_list.txt')

    csv_list = open(f'{out_folder_prefix}csv_list.txt', 'x')

    # Read and initial clean the CSV files
    df_dict = []
    cleaned_dfs = []
    for out_name, in_name in zip(out_names, in_names):
        curr_df = pd.read_csv(in_name, low_memory=False)
        # Process each CSV
        processed_df = clean.prepare_for_analysis(curr_df, cleaned_dfs, df_dict)
        # Save parsed file to csv in R folder inputs
        processed_df.to_csv(out_name, index=False)
        print(f'{in_name} parsed successfully and saved to: {out_name}')
        # Write csv name to text file
        csv_list.write(out_name)
        csv_list.write('\n')
    csv_list.close()

    thorax_dists = []

    for cleaned_df, in_name in zip(cleaned_dfs, in_names):
        fig_df = cleaned_df.copy()
        df_keypoints = fig_df.loc[fig_df['Type'] == 'Keypoints(m)']
        distance_df = calculate_custom_distance(dfs_splitted=fig_df, titles=[""], events_df=None, input_df=df_keypoints,
                                                first_part='Thorax', second_part='Thorax', parts=['FrameID'],
                                                start_frame=0,
                                                end_frame=4000, scenario='Entire Video',
                                                title='Distances over time for joints:',
                                                df_name=in_name, show_events=False)

        df_for_figure = distance_df.filter(items=['FrameID', 'Thorax_to_Thorax'])
        df_for_figure = df_for_figure.rename(columns={"Thorax_to_Thorax": "Thorax_dist"})
        print(in_name)
        # if ADD_SCRIPTED_VIDEOS == True:
        if in_name[7] == 'P':
            clip_frames = in_name.split('/')[3][:-10]
        else:
            clip_frames = in_name.split('/')[2][:-4]
        # else:
        # clip_frames = in_name.split('/')[3][:-10]
        df_for_figure.to_csv(f'Inputs/thorax_dist_clean_{clip_frames}.csv', index=False)
        print(f'{clip_frames} for figure 6 successfully saved to: Inputs/thorax_dist_clean_{clip_frames}.csv')

        thorax_dists = []

    for cleaned_df, in_name in zip(cleaned_dfs, in_names):
        fig_df = cleaned_df.copy()
        df_keypoints = fig_df.loc[fig_df['Type'] == 'Keypoints(m)']
        distance_df = calculate_custom_distance(dfs_splitted=fig_df, titles=[""], events_df=None, input_df=df_keypoints,
                                                first_part='Thorax', second_part='Thorax', parts=['FrameID'],
                                                start_frame=0,
                                                end_frame=4000, scenario='Entire Video',
                                                title='Distances over time for joints:',
                                                df_name=in_name, show_events=False)

        df_for_figure = distance_df.filter(items=['FrameID', 'Thorax_to_Thorax'])
        df_for_figure = df_for_figure.rename(columns={"Thorax_to_Thorax": "Thorax_dist"})
        print(in_name)
        # if ADD_SCRIPTED_VIDEOS == True:
        if in_name[7] == 'P':
            clip_frames = in_name.split('/')[3][:-10]
        else:
            clip_frames = in_name.split('/')[2][:-4]
        # else:
        # clip_frames = in_name.split('/')[3][:-10]
        df_for_figure.to_csv(f'Inputs/thorax_dist_clean_{clip_frames}.csv', index=False)
        print(f'{clip_frames} for figure 6 successfully saved to: Inputs/thorax_dist_clean_{clip_frames}.csv')

    for out_name, csv_path, conf_name in zip(out_names, in_names, conf_names):
        curr_df = pd.read_csv(csv_path, low_memory=False)
        cleaned_df = curr_df.copy()
        # remove rows where BodyID = ""
        cleaned_df.dropna(subset=["BodyID"], inplace=True)
        cleaned_df = cleaned_df.drop(columns=['Distances'])
        column_dict = {0: 'FrameID', 1: 'BodyID', 2: 'Type'}
        for key, value in CONSTANTS.JOINT_NAMES_DICT.items():
            column_dict[key + 3] = value
        cleaned_df.columns = column_dict.values()
        # Create confidence csvs
        conf_df = cleaned_df.copy()
        conf_df.columns = column_dict.values()
        drop_list = conf_df.index[
            conf_df['BodyID'] == 'BodyID'].tolist()  # Clear rows where value is a string (leftover from the parsing)
        conf_df = conf_df.drop(drop_list)
        conf_df = clean.keep_confidence(conf_df)
        convert_columns = clean.get_keypoints()
        for c in convert_columns:
            conf_df = conf_df.drop(columns=[f'{c}X', f'{c}Y'])
        conf_df.to_csv(conf_name, index=False)
        print(f'{csv_path} confidence parsed successfully and saved to: {conf_name}')