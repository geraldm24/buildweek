import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import csv
#import spotipy
#from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
load_dotenv()
DB_USER = os.getenv("DB_USER", default="OOPS")
DB_PASSWORD = os.getenv("DB_PASSWORD", default="OOPS")
DB_NAME = os.getenv("DB_NAME", default="OOPS")
DB_HOST = os.getenv("DB_HOST", default="OOPS")
conn = psycopg2.connect(dbname= DB_NAME,user= DB_USER,password=DB_PASSWORD,
                        host=DB_HOST)
c = conn.cursor()

spotify_table = """
  CREATE TABLE IF NOT EXISTS spotify_table (
    song_name VARCHAR(150) NOT NULL,
    song_popularity FLOAT NOT NULL,
    song_duration_ms FLOAT NOT NULL,
    acousticness FLOAT NOT NULL,
    danceability FLOAT NOT NULL,
    energy FLOAT NOT NULL,
    intrumentalness FLOAT NOT NULL,
    key FLOAT NOT NULL,
    liveness FlOAT NOT NULL,
    loudness FLOAT NOT NULL,
    audio_mode FLOAT NOT NULL,
    speechiness FLOAT NOT NULL,
    tempo FLOAT NOT NULL,
    time_signature FLOAT NOT NULL,
    audio_valence FLOAT NOT NULL
  );
"""
c.execute(spotify_table)
CsvPath = os.path.join(os.path.dirname(__file__),"data", "song_data2.csv")
# r read the file, next iterates through the file,
# copyfrom is equal to copy syntax in sql
# the commented out code below is what you need to make a new csv file
with open(CsvPath, 'r') as Csv:
    csv_reader = csv.reader(Csv)
    #with open('song_data2.csv', 'w', newline="") as new_file:
        #csv_writer = csv.writer(new_file, delimiter='|')

        #for line in csv_reader:
            #csv_writer.writerow(line)
    next(Csv)
    c.copy_from(Csv, 'spotify_table', sep='|')
conn.commit()



