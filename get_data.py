'''
Extract the data from the .txt files, into one pandas dataframe
'''

import pandas as pd
import os
import re
import matplotlib.pyplot as plt


data_dir = 'DriftTest_Chicago'
save_dir = 'Plots'

def get_data(data_dir):
    # Create a list of all the files in the data directory
    files = os.listdir(data_dir)
    files = [os.path.join(data_dir, file) for file in files]
    files = [file for file in files if re.search('.txt', file) and not re.search('Readme', file)]
    print(files)
    # Create an empty dataframe
    df_lst = []
    # Loop through all the files
    for file in files:
        new_df, new_df_metadata = process_file_to_df(file)
        df_lst.append((new_df, new_df_metadata))
                      
    return df_lst
        
def process_file_to_df(file):
    STARTING_STRING = '**********'
    
    # Read the file into a pandas dataframe
    with open(file, 'r') as f:
        lines = f.readlines()
    
    lines = [line.strip() for line in lines]
    data_start_idx = lines.index(STARTING_STRING) + 1
    lines = lines[data_start_idx:]
    data = [line.split(',') for line in lines]
    #The first element in each line looks like this "2024-01-05 15:12:34.665" we conver to datetime format
    print('!')
    print(len(data))
    data = [[pd.to_datetime(line[0]), *line[1:]] for line in data]
    
    metadata = {}
    first_channel = data[0][1]

    metadata['first_channel'] = first_channel
    #we assume every channel reports every cycle
    for i in range(len(data)):
        if data[i][-1][-1] == 'C':
            metadata['temp_channel'] = int(data[i][1])
        if i != 0 and data[i][1] == first_channel:
            metadata['num_channels'] = i
            break

    #convert measurement to float (we keep track of which one is temp through metadata dict)
    data = [[*line[:2], convert_to_float(line[2])] for line in data]
    print(data[0])
    #convert channel to int
    data = [[line[0], int(line[1]), line[2]] for line in data]

    data_df = pd.DataFrame(data, columns=['timestamp', 'channel', 'measurement'])

    return data_df, metadata

def convert_to_float(x):
    if re.search('NaN', x):
        return float('NaN')
    return float(re.sub('[^0-9.\-]','',x))

def gen_joint_graphs(df_lst):
    print('temperature channel : {}'.format(df_lst[0][1]['temp_channel']))
    joint_df = pd.concat([df_tup[0] for df_tup in df_lst], axis=0)
    joint_df = joint_df.dropna()
    channels = joint_df['channel'].unique()
    for channel in channels:
        channel_df = joint_df[joint_df['channel'] == channel]
        channel_df = channel_df.sort_values(by='timestamp')
        plt.scatter(channel_df['timestamp'], channel_df['measurement'], s=1)
        plt.title(f'Channel {channel} Measurements')
        plt.xlabel('Time')
        plt.xticks(rotation=45)
        plt.xticks(fontsize=8)
        plt.ylim(-100, 100)
        if channel == df_lst[0][1]['temp_channel']:
            plt.ylabel('Temperature (C)')
        else:
            plt.ylabel('Voltage VS reference (mV)')
        plt.savefig(os.path.join(save_dir, f'channel_{channel}_plot.png'))
        plt.close() 


def main():
    df_lst = get_data(data_dir)
    for df in df_lst:
        print(df[0].head())
    gen_joint_graphs(df_lst)


if __name__ == '__main__':
    main()

