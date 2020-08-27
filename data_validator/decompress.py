import os
import asyncio
import lzma
import struct
import pandas as pd
import numpy as np
from datetime import datetime
# from datetime import date, timedelta
tasks = []

def init_file_decompression(file_directory):
    print('\n\nDecompressing files for data cleaning...\n')
    global path
    path = file_directory
    start_loop()


def start_loop():
    dir_list = os.listdir(path)
    sorted_files = sorted(dir_list)

    # current_file = sorted_files[2]
    # print(current_file)
    # file = os.path.join(path, current_file)
    # print(file)
    # data_frame = decompress_data(file)
    # print(data_frame)

    build_tasks(sorted_files)


loop = asyncio.get_event_loop()

def build_tasks(sorted_files):
    # start_time = time.time()
    for file in sorted_files[2:]:
        current_file = os.path.join(path, file)
        task = asyncio.ensure_future(decompress_data(current_file.format(current_file)))
        tasks.append(task)

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
    # cleanup()
    # print("\n ----------------------------------------------------------------")
    # print("|              Completed in %s Seconds            |" % (time.time() - start_time))
    # print(" ----------------------------------------------------------------\n\n\n")

# async def test(file):
#     print(file)



async def decompress_data(file):
    chunk_size = 128
    fmt = '>3i2f'
    chunk_size = struct.calcsize(fmt)
    data = []
    with lzma.open(file) as f:
        while True:
            chunk = f.read(chunk_size)
            if chunk:
                data.append(struct.unpack(fmt, chunk))
            else:
                break
    df = pd.DataFrame(data)
    df.columns = ['TIME', 'ASKP', 'BIDP', 'ASKV', 'BIDV']
    write_file(file, df)

    print('finished task')


def write_file(file, df):
    year = int(file[-24:-20])
    month = int(file[-19:-17])
    day = int(file[-16:-14])
    hour = int(file[-13:-11])
    df = df.dropna()
    df = df.sort_values(by=['TIME'])

    # SAMPLE DATAFRAME FOR TESTING SMALL SETS:
    # df2 = pd.DataFrame(np.array([[1, 2, 3], [2, 5, 6], [1, 8, 9]]),
    # columns=['a', 'b', 'c'])
    # print('starting valuie : ')
    # print(df2)
    # df2 = df2.sort_values(by=['a'])

    # duplicateDFRow = df2[df2.duplicated(['a'])]
    # print(duplicateDFRow)
    # prev_val = ''
    # for i, row in df2.iterrows():
    #     print('----------------------------')
    #     if prev_val == row[0] :
    #         print("TEY ARE SAME TIME")
    #         # df2.drop(df2.index[i])
    #         df2.drop(i, inplace=True)
    #     else:
    #         print('not same')
    #     prev_val = row[0]
    # print('ending val :')
    # print(df2)


    file_date_object = datetime(year, month, day, hour)             # Build date object from integers in file name
    epoch = datetime.utcfromtimestamp(0)                            # Build Epoch
    date_ms = (file_date_object - epoch).total_seconds() * 1000.0   # Build fime timestamp in ms from epoch
    prev_row_time = ''  # Used from comparing current column to prev column in loop below

    for i, row in df.iterrows():
        if prev_row_time == row[0]:
            df.drop(i, inplace=True)    # Remove any rows from dataframe with duplicate timestamps
        else:
            ms_time_stamp = date_ms + row[0]
            df.at[i,'TIME'] = ms_time_stamp     # Convert timestamp into ms from epoc rathe than ms from the hour start
        prev_row_time = row[0]

        # ask_price = row[1]/100000
        # bid_price = row[2]/100000
        # df.at[i,1] = ask_price
        # df.at[i,2] = bid_price

    # print(df)
    df.to_csv(r'/Users/ericlingren/Desktop/test.csv', index = False)

# decompress_data()




# DATA FORMAT:

# [ TIME  ] [ ASKP  ] [ BIDP  ] [ ASKV  ] [ BIDV  ]

# TIME is a 32-bit big-endian integer representing the number of milliseconds that have passed since the beginning of this hour.
# ASKP is a 32-bit big-endian integer representing the asking price of the pair, multiplied by 100,000.
# BIDP is a 32-bit big-endian integer representing the bidding price of the pair, multiplied by 100,000.
# ASKV is a 32-bit big-endian floating point number representing the asking volume, divided by 1,000,000.
# BIDV is a 32-bit big-endian floating point number representing the bidding volume, divided by 1,000,000.





