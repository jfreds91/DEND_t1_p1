import os
import glob
import psycopg2
import pandas as pd
import datetime as dt
from sql_queries import *


def convert_type(l:list):
    '''
    converts all filetypes in a list to native types if they are numpy
    '''
    new_l = []
    for i in range(len(l)):
        try:
            new_l.append(l[i].item())
        except:
            new_l.append(l[i])
    return new_l


def process_song_file(conn, cur, filepath):
    '''
    Interprets json song file records and inserts them into the songs and artists tables
    INPUTS:
        conn: postgres connection object
        cur: postgres cursor object
        filepath: (str) full filepath of .json file
    
    RETURNS: None
    '''
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = convert_type(df[['song_id', 'title', 'artist_id', 'year', 'duration']].iloc[0].values.tolist())
    try:
        cur.execute(song_table_insert, song_data)
    except Exception as e:
        conn.rollback()
        print(e)
    
    # insert artist record
    artist_data = convert_type(df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_latitude']].iloc[0].values.tolist())
    try:
        cur.execute(artist_table_insert, artist_data)
    except Exception as e:
        conn.rollback()
        print(e)


def process_log_file(conn, cur, filepath):
    '''
    Interprets json log file records and inserts them into the users, time, and songplays tables
    INPUTS:
        conn: postgres connection object
        cur: postgres cursor object
        filepath: (str) full filepath of .json file
    
    RETURNS: None
    '''
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']
    df['ts_parse'] = df['ts'].apply(lambda x: dt.datetime.fromtimestamp(x/1000.0))
    df['hour'] = df['ts_parse'].dt.hour
    df['day'] = df['ts_parse'].dt.day
    df['week'] = df['ts_parse'].apply(lambda x: x.isocalendar()[1])
    df['month'] = df['ts_parse'].dt.month
    df['year'] = df['ts_parse'].dt.year
    df['weekday'] = df['ts_parse'].dt.weekday

    # convert timestamp column to datetime
    # t = 
    
    # insert time data records
    # time_data = 
    # column_labels = 
    time_df = df[['ts_parse', 'hour', 'day', 'week', 'month', 'year', 'weekday']]

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]
    user_df.drop_duplicates(subset = ['userId'], inplace = True)

    # insert user records
    for i, row in user_df.iterrows():
        try:
            cur.execute(user_table_insert, row)
        except Exception as e:
            conn.rollback()
            print(e)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        # print(row.song, row.artist, row.length)
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts_parse, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    '''
    Applies supplied function to all files in designated path; passes connection
    and cursor objects to function
    '''

    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(conn, cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()