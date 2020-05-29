from flask import Flask, render_template, request
import numpy as np
import keras.models
import re
import sys 
import os
import base64
#sys.path.append(os.path.abspath("./model"))
from load import * 
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json
import pandas as pd
from minisom import MiniSom



def create_app():
    global model
    model = init()
    app = Flask(__name__)
    # configure the database:
  
    db.init_app(app)
    migrate.init_app(app, db)

    return app

@app.route('/')
def index_view():
    return render_template('index.html')

def scaled_songs(a_array):
    '''takes scaled input array and returns a df with scaled values'''
    global songs
    #filtering songs by predicted label of sample track
    songs = songs.sort_index()
    filtered_songs = songs[songs['label'] == model.predict_classes(a_array)[0]]
    # dropping unnecessary columns and renaming for readability
    songs_scaled = filtered_songs.join(pd.DataFrame(features_scaled)).drop(
    labels=features.columns, axis=1)
    songs_scaled = songs_scaled.rename(
    columns={0: features.columns[0],
             1: features.columns[1],
             2: features.columns[2],
             3: features.columns[3],
             4: features.columns[4],
             5: features.columns[5],
             6: features.columns[6],
             7: features.columns[7],
             8: features.columns[8],
             9: features.columns[9]})
    return songs_scaled 
def find_neighbors(a_df):
    '''takes scaled df and returns df filtered for songs near to sample '''
    global a_list
    # computing distance from sample track for each track in cluster
    a_df['distance'] = [(np.linalg.norm(
    a_df[features.columns][i:i+1] - adj_input(a_list))) 
    for i in range(0, len(a_df))]
    # filtering to only songs within a certain distance
    neighbors = a_df[a_df['distance'] < .2].sort_values('distance')
    return neighbors
def results_dataframe(neighbors):
    # turning input scaled to df
    global input_scaled
    global track_info
    # neighbors = find_neighbors(scaled_songs(adj_input(a_list)))
    input_scaled = pd.DataFrame(adj_input(a_list)).rename(
    columns={0: features.columns[0],
             1: features.columns[1],
             2: features.columns[2],
             3: features.columns[3],
             4: features.columns[4],
             5: features.columns[5],
             6: features.columns[6],
             7: features.columns[7],
             8: features.columns[8],
             9: features.columns[9]})
    # rejoining artist and title with song features
    results = pd.DataFrame(track_info, 
                       index=[0], 
                       columns=['song', 'artist']
                      ).rename(columns={'song': 'song_name',
                                        'artist': 'song_artist'}
                              )
    results = pd.concat([results, input_scaled], axis=1)
    results['label'] = model.predict_classes(input_scaled)
    # adding sample track to filtered songs
    results = pd.concat([results, neighbors])
    # dropping duplicates where name and artist are identical
    results = results.drop_duplicates(subset=['song_name', 'song_artist'])
    #return top 10 song names with artist
    result_df = pd.concat([results[:1], results.sample(10).sort_values('distance')])
    result_df = result_df[['song_name','song_artist']]
    result_df = pd.concat([results[:1], results.sample(10).sort_values('distance')])
    result_df = result_df.drop_duplicates(subset=['song_name', 'song_artist'])
    return result_df
@app.route('/predict/',methods=['GET','POST'])
def predict():
    client_credentials_manager = SpotifyClientCredentials(client_id='f13a6b55c2d949939455644bbd6f31d9', client_secret='c7c009270ff0483db51d25543563d55c')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist = sp.playlist('open.spotify.com/playlist/2YRe7HRKNRvXdJBp9nXFza')
    track_info = dict(song=playlist['tracks']['items'][12]['track']['name'], 
                  artist=playlist['tracks']['items'][12]['track']['album']['artists'][0]['name'],
                  uri=playlist['tracks']['items'][12]['track']['uri'])
    track_features = sp.audio_features(track_info['uri'])
    track = [track_features[0][i] for i in features]
    the_list = [track_info['song'], track_info['artist'], track]
    print(take_ten(the_list))
    #main function
def take_ten(a_list):
  '''takes input list for 1 song and returns a json file with the 10 most similar songs''' 
  global track_info
  #setting static variables for results_dataframe function
  input_scaled = np.empty((1,10))
  track_info = dict({'artist': a_list[1], 'song': a_list[0]})
  #saving results as json
  results_df = results_dataframe(find_neighbors(scaled_songs(adj_input(a_list))))[['song_name', 'song_artist']]
  results_df.to_json('results.json', orient='records')
  with open('results.json') as json_file:
    json_data = json.load(json_file)
  return json_data
#sub functions
def adj_input(the_list):
    '''takes an input list and returns cleaned and scaled version'''
    global a_list
    a_list = the_list
    input_vector = a_list[2:]
    input_scaled = scaler.transform(np.array(input_vector).reshape(1, -1))
    return input_scaled

if __name__ == "__main__":
    my_app = create_app()
    my_app.run(debug=True)
   