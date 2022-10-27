######## Clean OpenPose Generated CSVs into X, Y, Z Keypoint CSVs

# Import Relevant Libraries
import pandas as pd
import glob, os, csv
from socialresearchcv.analysis.CONSTANTS import CONSTANTS as CONSTANTS
from socialresearchcv.analysis.AnalysisUtils import split_3d_values
import re

def get_file_parsing_locations(file_names, in_folder_prefix, out_folder_prefix):
    in_names = [f'{in_folder_prefix}{fn}.csv' for fn in file_names]
    out_names = [f'{out_folder_prefix}clean_{fn}.csv' for fn in file_names]
    conf_names = [f'{out_folder_prefix}clean_{fn}_confidence.csv' for fn in file_names]
    return in_names,out_names,conf_names

# Get File List
def get_files(path):
    os.chdir(f'{path}/clean/input')
    file_list = []
    for f in glob.glob("processed*"):
        file_list.append(f)
    return file_list

# Create list of keypoints
def get_keypoints():
    """
    Get the list of keypoints
    :return: list of keypoint strings
    """
    convert_columns = []
    for joint in CONSTANTS.JOINT_NAMES_DICT.values():
        convert_columns.append(joint)
    return convert_columns

# Function for Separating DF Keypoints into X, Y, Z
def separate_coordinates(df):   
    new_columns = []
    df_keypoints = df.loc[df['Type'] == 'Keypoints(m)']
    df_split = pd.DataFrame()
    convert_columns = get_keypoints()
    for c in convert_columns:
        df_keypoints[c] = df_keypoints[c].str[1:-1]
        split_cols = [f'{c}X',f'{c}Y',f'{c}Z']
        df_split[split_cols] = df_keypoints[c].str.split(",",expand=True,)
        [new_columns.append(col) for col in split_cols]
    # Append remaining columns
    new_columns.append('FrameID')
    new_columns.append('BodyID')
    df_split['BodyID'] = df_keypoints['BodyID']
    df_split['FrameID'] = df_keypoints['FrameID']
    # Convert from string to float 
    df_split[new_columns] = df_split[new_columns].apply(pd.to_numeric)
    # Clean Keypoints ("split") Dataframe
    df_split.reset_index(inplace=True)
    df_split.rename(columns = {'index' : 'df_index'}, inplace=True)
    # del c, split_cols, df_keypoints, new_columns
    return df_split

def get_column_dict():
    column_dict = {0:'FrameID', 1:'BodyID', 2:'Type'}
    for key, value in CONSTANTS.JOINT_NAMES_DICT.items():
        column_dict[key+3] = value
    column_dict[24] = "Distances"
    return column_dict

def get_df_dict(path, file_list):
    df_dict = {}
    for filename in file_list:
        df = pd.read_csv(f'{path}{filename}', low_memory=False,na_values='[0.0, 0.0, 0.0]')
        column_dict = get_column_dict()
        df.columns = column_dict.values()
        drop_list = df.index[df['BodyID'] == 'BodyID'].tolist() # Clear rows where value is a string (leftover from the parsing)
        df = df.drop(drop_list)
        df = separate_coordinates(df)
#         one = filename.split('/Baseline_')[1]
#         two = one.split('_0_')[0]
#         three = two.replace('_0_', '')
#         four = three.replace('_', ' ')
        fn = os.path.basename(filename)
        fn = os.path.splitext(fn)[0]
        fn = fn.replace('_',' ')
        df_dict[fn] = df
    return df_dict

def get_confidence_csvs(path, file_list):
    for filename in file_list:
        convert_columns = get_keypoints()
        df = pd.read_csv(f'{path}/clean/input/{filename}', low_memory=False,na_values='[0.0, 0.0, 0.0]')
        column_dict = get_column_dict()
        df.columns = column_dict.values()
        drop_list = df.index[df['BodyID'] == 'BodyID'].tolist() # Clear rows where value is a string (leftover from the parsing)
        df = df.drop(drop_list)
        df = keep_confidence(df)
        one = filename.split('ine_')[1]
        two = one.split('_0_')[0]
        three = two.replace('_0_', '')
        four = three.replace('_', ' ')
        for c in convert_columns:
            df = df.drop(columns=[f'{c}X', f'{c}Y'])
        df.to_csv(f'{path}/clean/output/{four}_confidence.csv', index=False)
        

def keep_confidence(df):
    """
    Keep the confidence score for the dataframe
    :param df: the input dataframe to manipulate
    :return: df_split - the processed dataframe, with confidence score
    """
    new_columns = []
    df_keypoints = df.loc[df['Type'] == 'Keypoints(image)']
    df_split = pd.DataFrame()
    convert_columns = get_keypoints()
    for c in convert_columns:
        df_keypoints[c] = df_keypoints[c].str[1:-1]
        split_cols = [f'{c}X',f'{c}Y',f'{c}_Confidence']
        df_split[split_cols] = df_keypoints[c].str.split(",",expand=True,)
        [new_columns.append(col) for col in split_cols]
    # Append remaining columns
    new_columns.append('FrameID')
    new_columns.append('BodyID')
    df_split['BodyID'] = df_keypoints['BodyID']
    df_split['FrameID'] = df_keypoints['FrameID']
    # Convert from string to float 
    df_split[new_columns] = df_split[new_columns].apply(pd.to_numeric)
    # Clean Keypoints ("split") Dataframe
    df_split.reset_index(inplace=True)
    df_split.rename(columns = {'index' : 'df_index'}, inplace=True)
    # del c, split_cols, df_keypoints, new_columns
    return df_split

# Function takes dataframe and list of frame numbers where pid switches occur and returns dataframes with correct PIDs
def fix_pidswitch(df,switches):
    for x in switches:
        min_val = df[df['FrameID']==x].index.values.min()
        df.loc[min_val:,'BodyID'] = df['BodyID']-1
        df.loc[min_val:,'BodyID'] = df['BodyID'].abs()
    return df

# Send all dfs through pid switch fixing function
def clean_pid_switching(path, df_dict):
    df_dict_switched = {}
    with open(f'{path}/switches.csv') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            video = df_dict[row[0]]                         # The video name is in the first column
            switches = row[1:]
            while ('' in switches):                         # Remove empty strings from list
                switches.remove('')
            for i in range(0, len(switches)):               # Convert strings to integers
                switches[i] = int(switches[i])
            switched_video = fix_pidswitch(df=video,switches=switches)
            df_dict_switched[row[0]] = switched_video
    return df_dict_switched


def prepare_for_analysis(curr_df,cleaned_dfs, df_dict):
    """
    Prepare the dataframe for analysis
    :param curr_df: the dataframe to prepare
    :param cleaned_dfs: list of dataframes to add the cleaned one to
    :param df_dict: dictionalry to append the cleaned dataframe into
    :return:
    """
    cleaned_df = curr_df.copy()

    drop_list = cleaned_df.index[cleaned_df['BodyID'] == 'BodyID'].tolist()
    cleaned_df = cleaned_df.drop(drop_list)
    
    #remove rows where BodyID = ""
    cleaned_df.dropna(subset = ["BodyID"], inplace=True)
    cleaned_df = cleaned_df.drop(columns=['Distances'])
    
    #Convert joints to representative values
    column_dict = {0:'FrameID', 1:'BodyID', 2:'Type'}
    for key, value in CONSTANTS.JOINT_NAMES_DICT.items():
        column_dict[key+3] = value
    cleaned_df.columns = column_dict.values()
    cleaned_dfs.append(cleaned_df)
    
    # Original R script expects 1,2,3 - left X,Y,Z
    cleaned_df_splitted = split_3d_values([cleaned_df])
    df_dict.append(cleaned_df_splitted)
    cleaned_df_splitted_for_body = cleaned_df_splitted[0]
    cleaned_df_splitted_for_body.drop(cleaned_df_splitted_for_body[cleaned_df_splitted_for_body["BodyID"]==2].index,inplace=True)

    # Remove 3rd BodyID
    rows_to_clean = cleaned_df_splitted_for_body.loc[cleaned_df_splitted_for_body["BodyID"]==2]
    clean_candidates = cleaned_df_splitted_for_body.loc[cleaned_df_splitted_for_body["FrameID"].isin(rows_to_clean.FrameID)]
    clean_candidates = clean_candidates.loc[clean_candidates.BodyID>0]

    # Prepare data columns for R processing
    columns_d = cleaned_df_splitted_for_body.columns.copy()
    columns_d = [c.lower() for c in columns_d]
    columns_d = [re.sub('^r', 'r_',c) for c in columns_d]
    columns_d = [re.sub('^l', 'l_',c) for c in columns_d]
    columns_d = [re.sub('midhip', 'mid_hip',c) for c in columns_d]
    columns_d = [c[:-1] + c[-1].upper() for c in columns_d]
    
    final_df_for_export = cleaned_df_splitted_for_body.copy()
    final_df_for_export.columns = columns_d
    
    return final_df_for_export

# events_table_path = 'data/Script Frame Timing.csv'
# events_df = pd.read_csv(events_table_path, low_memory=False)
# del events_table_path


# @Doron Shiffer-Sebba, if you want it applied to pandas dataframe you need to call df.div(4) in the column that represents your keypoint.