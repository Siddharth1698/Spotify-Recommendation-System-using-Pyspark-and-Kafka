import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


import os
# import my_spotify_credentials as credentials
import numpy as np
import pandas as pd
import ujson
import spotipy
import spotipy.util
import seaborn as sns

# use your credentials
os.environ["SPOTIPY_CLIENT_ID"] = ''
os.environ["SPOTIPY_CLIENT_SECRET"] = ''
os.environ["SPOTIPY_REDIRECT_URI"] = ''

scope = 'user-library-read'
username = ''

token = spotipy.util.prompt_for_user_token(username, scope)

if token:
    spotipy_obj = spotipy.Spotify(auth=token)
    saved_tracks_resp = spotipy_obj.current_user_saved_tracks(limit=50)
else:
    print('Couldn\'t get token for that username')

number_of_tracks = saved_tracks_resp['total']
print('%d tracks' % number_of_tracks)


def save_only_some_fields(track_response):
    return {
        'id': str(track_response['track']['id']),
        'name': str(track_response['track']['name']),
        'artists': [artist['name'] for artist in track_response['track']['artists']],
        'duration_ms': track_response['track']['duration_ms'],
        'popularity': track_response['track']['popularity'],
        'added_at': track_response['added_at']
    }


tracks = [save_only_some_fields(track) for track in saved_tracks_resp['items']]

while saved_tracks_resp['next']:
    saved_tracks_resp = spotipy_obj.next(saved_tracks_resp)
    tracks.extend([save_only_some_fields(track) for track in saved_tracks_resp['items']])

tracks_df = pd.DataFrame(tracks)
pd.set_option('display.max_rows', len(tracks))

#pd.reset_option('display.max_rows')

tracks_df['artists'] = tracks_df['artists'].apply(lambda artists: artists[0])
tracks_df['duration_ms'] = tracks_df['duration_ms'].apply(lambda duration: duration/1000)

tracks_df = tracks_df.rename(columns = {'duration_ms':'duration_s'})

audio_features = {}

for idd in tracks_df['id'].tolist():
    audio_features[idd] = spotipy_obj.audio_features(idd)[0]

tracks_df['acousticness'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['acousticness'])
tracks_df['speechiness'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['speechiness'])
tracks_df['key'] = tracks_df['id'].apply(lambda idd: str(audio_features[idd]['key']))
tracks_df['liveness'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['liveness'])
tracks_df['instrumentalness'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['instrumentalness'])
tracks_df['energy'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['energy'])
tracks_df['tempo'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['tempo'])
tracks_df['time_signature'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['time_signature'])
tracks_df['loudness'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['loudness'])
tracks_df['danceability'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['danceability'])
tracks_df['valence'] = tracks_df['id'].apply(lambda idd: audio_features[idd]['valence'])

df = tracks_df


rec_df = pd.read_csv(r'C:\Users\siddh\Downloads\structuredstreamingkafkapyspark-master\rec_song.csv')
st.set_page_config(layout="wide")
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Spotify User Dashboard')

col1, col2 = st.beta_columns(2)
#
col1.header("Your Latest added Song")
top_5_songs = df[['name', 'artists']].head(5)
col1.table(top_5_songs)
#
col2.header("Your Top 10 Artists")
df1 = df['artists'].value_counts()[:11].to_frame()
df1['Name'] = df1.index
df1.rename(columns={'artists': 'Songs'}, inplace=True)
fig = px.pie(df1, values='Songs', names='Name', hole=0.2)
fig.update_traces(textposition='inside', textinfo='label')
col2.plotly_chart(fig, use_container_width=True)
####

col3, col4, col5 = st.beta_columns(3)
#


ur_favourite_artist = df[['artists']].value_counts().index[0][0]
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-Weight: bold;
}
</style>
""", unsafe_allow_html=True)

col3.header("Your Favourite Artist")
col3.markdown(f'<p class="big-font">{str(ur_favourite_artist)}</p>', unsafe_allow_html=True)
#
col4.header("Total Time of Songs")
time = round(df.duration_s.sum() / 3600, 2)
col4.markdown(f'<p class="big-font">{round(df.duration_s.sum() / 3600, 2)} hours</p>', unsafe_allow_html=True)
#
col5.header("Total Number of Songs")
col5.markdown(f'<p class="big-font">{df.count()[1]} songs</p>', unsafe_allow_html=True)
#
####

col6,col7 = st.beta_columns(2)
col6.header("Your Recommended Songs")


df2 = rec_df[['name','artists']]
print(df2)
col6.table(df2.head(10))
#


col7.header("Features of your Latest Songs")
df3 = rec_df.loc[:10, ['name', 'artists', 'acousticness', 'liveness', 'instrumentalness', \
                  'energy', 'danceability', 'valence']]
df3 = df3.T.reset_index()
df3.rename(columns={'index': 'theta', 0: 'zero', 1: 'one', 2: 'two', \
                    3: 'three', 4: 'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve'}, inplace=True)
df3_cols = df3.columns[1:]
len_cols = len(df3_cols)
categories = df3['theta'].tolist()[2:]
fig1 = go.Figure()
for i in range(0, len_cols):
    fig1.add_trace(go.Scatterpolar(
        r=df3[df3_cols[i]][2:].tolist(),
        theta=categories,
        fill='toself',
        name=df3[df3_cols[i]][0]))
fig1.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]
        )),
    showlegend=True
)
col7.plotly_chart(fig1, use_container_width=True)


