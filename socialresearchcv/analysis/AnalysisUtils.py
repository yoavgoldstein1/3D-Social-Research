import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from socialresearchcv.analysis.CONSTANTS import CONSTANTS as CONSTANTS

pd.options.mode.chained_assignment = None
def get_events(dfs_distances, titles, events_df, bag_title, start_frame, end_frame, parts):
    """ Get a list of event (for the scripted videos)

    Args:
        dfs_distances (list<Dataframe>): list of dataframes to parse
        titles (list<string>): list of video titles
        events_df (Dataframe): dataframe with the required events
        bag_title (string): the video name
        start_frame (int): the frame to start parsing with
        end_frame (int): the frame to end labeling
        parts (_type_): _description_
    """
    for df, title in zip(dfs_distances, titles):
        if bag_title is title:
            name = title.split('/')[-1]
            df.loc[:, 'Scenario'] = df.loc[:, 'FrameID']
            index = 0
            #             index = int(events_df.loc[events_df['Scenario'] == events_df['Scenario'][0],name])
            key_scenarios = []
            for scenario in events_df['Scenario']:
                try:
                    ed = int(events_df.loc[events_df['Scenario'] == scenario, name])
                except ValueError:
                    continue
                if ed < start_frame:
                    index = ed
                    continue
                if ed > end_frame:
                    break
                df['Scenario'].loc[(df['FrameID'] > index) & (df['FrameID'] < ed)] = scenario
                key_scenarios.append((index, ed, scenario))
                index = ed
            return key_scenarios


def split_3d_values(dfs):
    """Splits the single cell 3D positions into 3 separate cells

    Args:
        dfs (list<Dataframe>): list of dataframes with respected data

    Returns:
        dfs_splitted: a list<Dataframes> with the 3D positions splitted to separate columns
    """
    dfs_splitted = []
    for df in dfs:
        df_keypoints = df.loc[df['Type'] == 'Keypoints(m)']

        if df_keypoints.size == 0:
            continue

        convert_columns = []
        for joint in CONSTANTS.JOINT_NAMES_DICT.values():
            convert_columns.append(joint)

        new_columns = []
        df_splitted = pd.DataFrame()
        for c in convert_columns:
            df_keypoints[c] = df_keypoints[c].str[1:-1]
            split_cols = [f'{c}X', f'{c}Y', f'{c}Z']
            df_splitted[split_cols] = df_keypoints[c].str.split(",", expand=True, )
            [new_columns.append(col) for col in split_cols]

        new_columns.append('FrameID')
        new_columns.append('BodyID')
        df_splitted['BodyID'] = df_keypoints['BodyID']
        df_splitted['FrameID'] = df_keypoints['FrameID']

        df_splitted[new_columns] = df_splitted[new_columns].apply(pd.to_numeric)
        dfs_splitted.append(df_splitted)
    return dfs_splitted


def calc_dist(x, y):
    """Calculate the distance between two 3D points

    Args:
        x (list<float>): 3D point 1
        y (list<float>): 3D point 2

    Returns:
        float: the distance between the two points, np.nan if distance is 0
    """
    if type(x) == list and type(y) == list:
        a = np.array((x[0], x[1], x[2])).astype(np.float)
        b = np.array((y[0], y[1], y[2])).astype(np.float)
        try:
            dist = np.linalg.norm(a - b)
            if dist == 0:
                return np.nan
            else:
                return dist
        except:
            print(f"Invalid operations: {a[1]} and {b[1]}")
            return np.nan


def calculate_custom_distance(dfs_splitted, titles, events_df, input_df, first_part, second_part, parts, start_frame,
                              end_frame, scenario, title, df_name, show_events=False, save_fig=False, plot_fig=True):
    """Calculate custom 3D euclidean distances based on the parameters provided

    Args:
        dfs_splitted (list(Dataframe)): a list of dataframes that contains the 3D positions
        titles (list(string)): list of titles for the dataframes
        events_df (list(Dataframe)): list of special events
        input_df (Dataframe): the input dataframe
        first_part (string): first keypoint to measure distance from
        second_part (string): second keypoing to measuere the distance from
        parts (set(keypoints)): set pf keypoints to measure from
        start_frame (int): start frame to measure from
        end_frame (int): end frame to measure to
        scenario (string): scenario title, for annotated specific scenario
        title (string): title for the plot, of needed
        df_name (string): name of dataframe, for plotting purposes
        show_events (bool, optional): whether to show labels for the events list. Defaults to False.
        save_fig (bool, optional): whether to save the output calculation. Defaults to False.
        plot_fig (bool, optional): whether to plot the output calculation. Defaults to False.

    Returns:
        Dataframe: a dataframe of distances between first_part and second_part
    """
    df_cross_keypoints = input_df.copy()

    # Make BodyID and FrameID numeric
    df_cross_keypoints['BodyID'] = df_cross_keypoints['BodyID'].apply(pd.to_numeric)
    df_cross_keypoints['FrameID'] = df_cross_keypoints['FrameID'].apply(pd.to_numeric)

    df_orig = input_df.copy()
    # Leave only frames with 2+ people
    #     df_cross_keypoints['HasTwoPersons'] = df_cross_keypoints.FrameID.duplicated(keep=False)
    #     df_cross_keypoints = df_cross_keypoints.loc[df_cross_keypoints.HasTwoPersons, :]

    # Convert parts from string to numeric vector of 3 values (x,y,z)
    df_cross_keypoints[first_part] = df_cross_keypoints[first_part].apply(lambda x: x[1:-1].split(','))
    if (first_part != second_part):
        df_cross_keypoints[second_part] = df_cross_keypoints[second_part].apply(lambda x: x[1:-1].split(','))

    # Create next cross vector, representing the second person
    next_df_cross_keypoints = df_cross_keypoints.shift(-1)

    # Take one for Body 1 and on for body 2
    df_cross_keypoints = df_cross_keypoints.loc[df_cross_keypoints.BodyID == 0]
    next_df_cross_keypoints = next_df_cross_keypoints.loc[next_df_cross_keypoints.BodyID == 1]

    # Create the distance DF and use combine to calculate the distance for each 3D vector
    df2 = df_cross_keypoints.copy()
    new_dist_column = f'{first_part}_to_{second_part}'
    df2[new_dist_column] = df_cross_keypoints[first_part].combine(next_df_cross_keypoints[second_part],
                                                                  lambda x, y: calc_dist(x, y))
    df2 = df2[(df2['FrameID'] > start_frame) & (df2['FrameID'] < end_frame)]

    if plot_fig:
        # Plot stuff
        ax = df2.plot(lw=1, x='FrameID', y=new_dist_column, colormap='jet', marker='.', markersize=1,
                      title=f'{df_name}\n\n{scenario} - {title}{first_part}(0) and {second_part}(1) ({start_frame},{end_frame})',
                      figsize=(20, 6))
        if show_events:
            parts = set([first_part, second_part])
            key_scenarios = get_events(dfs_splitted, titles, events_df, df_name, start_frame, end_frame, parts)
            for key_scenario in key_scenarios:
                try:
                    first_loc = df2.iloc[key_scenario[1] - start_frame]
                    ind = max(1, key_scenario[1])
                except IndexError:
                    pass
                for part in parts:
                    if part is not 'FrameID':
                        if np.isnan(first_loc[new_dist_column]):
                            first_loc[part] = -1
                        ax.text(ind, first_loc[new_dist_column] + 0.1, f'<-{key_scenario[2]}({ind})', rotation=45,
                                c='gray')
    if save_fig:
        plt.savefig(f'{df_name}{scenario} - {title}{parts}({start_frame},{end_frame}).png'.replace(" ", "_").strip(
            '[]').replace(",", "_"), dpi=300)

    return df2


def get_num_of_people(df_for_count_internal):
    """[INTERNAL] returns the number of people for each frame

    Args:
        df_for_count_internal (Dataframe): the dataframe to compute from

    Returns:
        Dataframe: number of people in each frame
    """
    new_df = pd.DataFrame(df_for_count_internal)
    num_of_people = new_df['FrameID'].value_counts()
    return num_of_people
