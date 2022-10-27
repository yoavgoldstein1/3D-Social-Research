import numpy as np
import pandas as pd
from socialresearchcv.analysis.AnalysisUtils import get_events


def plot_distances(df_distances,titles, events_df,dataframe, parts, start_frame, end_frame, scenario ,title, df_name, show_events=False, save_fig=False):

    df2 = pd.DataFrame(dataframe, columns=parts)
    df2 = df2[(df2['FrameID'] > start_frame) & (df2['FrameID'] < end_frame)]

    ax = df2.plot(lw=1, x='FrameID', colormap='jet', marker='.', markersize=1, 
             title=f'{df_name}\n\n{scenario} - {title}{parts}({start_frame},{end_frame})',figsize=(20,6))
    
    if show_events:
        key_scenarios = get_events(df_distances, titles, events_df, df_name, start_frame, end_frame, parts)
        print(key_scenarios)
        for key_scenario in key_scenarios:
            try:
                first_loc = df2.iloc[key_scenario[1]-start_frame]
                ind = max(1,key_scenario[1])
            except IndexError:
                pass
            for part in parts:
                if part is not 'FrameID':
                    if np.isnan(first_loc[part]):
                        first_loc[part] = -1
                        ind = start_frame
                    ax.text(ind, first_loc[part]+0.1, f'<-{key_scenario[2]}({ind})',rotation=45, c='gray')
    if save_fig:
        plt.savefig(f'{df_name}{scenario} - {title}{parts}({start_frame},{end_frame}).png'.replace(" ","_").strip('[]').replace(",","_"), dpi=300)




def show_keypoint(part, start_frame, end_frame, data_frame, show_bounding_box = False, title='', df_name = '', save_fig=False, save_csv=False):

    columns = ['FrameID','BodyID',f'{part}X',f'{part}Y',f'{part}Z']
    tf_projected = pd.DataFrame(data_frame, columns=columns)
    tf_projected = tf_projected[(tf_projected['FrameID'] > start_frame) & (tf_projected['FrameID'] < end_frame)]
    tf_projected['Frame'] = tf_projected['FrameID']
    tf_projected['Frame'] -= tf_projected['Frame'].min()
    tf_projected.loc[tf_projected['BodyID'] == 0, 'Frame'] = -tf_projected.loc[tf_projected['BodyID'] == 0, 'Frame']
    
    ax = tf_projected.plot.scatter(x=f'{part}X',
                          y=f'{part}Z',
                          c='Frame',
                          colormap='seismic',
                          title=f'{df_name}\n\n{part} {title} ({start_frame},{end_frame})'
                                  )
    ax.set_xlabel(f'{part}X')

    if show_bounding_box:
        import matplotlib.patches as patches
        tf_projected= tf_projected[(tf_projected[f'{part}X'] != 0)]
        tf_projected= tf_projected[(tf_projected[f'{part}Z'] != 0)]

        min_0 = tf_projected[tf_projected['BodyID']==0].min()
        max_0 = tf_projected[tf_projected['BodyID']==0].max()
        min_1 = tf_projected[tf_projected['BodyID']==1].min()
        max_1 = tf_projected[tf_projected['BodyID']==1].max()

        # Create a Rectangle patch
        rect_0 = patches.Rectangle((min_0[f'{part}X'],min_0[f'{part}Z']),max_0[f'{part}X']-min_0[f'{part}X'],max_0[f'{part}Z']-min_0[f'{part}Z'],linewidth=2,edgecolor='gray',facecolor='none')
        rect_1 = patches.Rectangle((min_1[f'{part}X'],min_1[f'{part}Z']),max_1[f'{part}X']-min_1[f'{part}X'],max_1[f'{part}Z']-min_1[f'{part}Z'],linewidth=2,edgecolor='gray',facecolor='none')


        # Add the patch to the Axes
        ax.add_patch(rect_0)
        ax.add_patch(rect_1)
    if save_fig:
        plt.savefig(f'{df_name}_{title.replace(" ","_")}_{part.replace(" ","_")}_{start_frame}_{end_frame}.png', dpi=300)
    if save_csv:
        tf_projected.to_csv(f'{df_name}_{title.replace(" ","_")}_{part.replace(" ","_")}_{start_frame}_{end_frame}.csv')


import matplotlib.pyplot as plt

def show_custom_distance(part, start_frame, end_frame, data_frame, show_bounding_box = False, title='', df_name = '', save_fig=False):

    columns = ['FrameID','BodyID',f'{part}X',f'{part}Y',f'{part}Z']
    tf_projected = pd.DataFrame(data_frame, columns=columns)
    tf_projected = tf_projected[(tf_projected['FrameID'] > start_frame) & (tf_projected['FrameID'] < end_frame)]
    tf_projected['Frame'] = tf_projected['FrameID']
    tf_projected['Frame'] -= tf_projected['Frame'].min()
    tf_projected.loc[tf_projected['BodyID'] == 0, 'Frame'] = -tf_projected.loc[tf_projected['BodyID'] == 0, 'Frame']

    cmhot = plt.cm.get_cmap("hot")
    threedee = plt.figure(figsize=(12,12)).gca(projection='3d')
    y_data = tf_projected[f'{part}Y']#-(min(tf_projected[f'{part}Y']))
    ax = threedee.scatter(tf_projected[f'{part}X'], -y_data+1, tf_projected[f'{part}Z'], cmap='seismic',c=tf_projected['Frame'])
    threedee.set_xlabel('X')
    threedee.set_ylabel('Y')
    threedee.set_zlabel('Z')
    threedee.set_title(f'{df_name}\n\n{part} {title} ({start_frame},{end_frame})')
    threedee.view_init(elev=-300, azim=0)
    plt.show()
    if save_fig:
        plt.savefig(f'{df_name}_{title.replace(" ","_")}_{part.replace(" ","_")}_{start_frame}_{end_frame}.png', dpi=300)


 
