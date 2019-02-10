#! python3
# appleToSpotify.py
# this program will convert apple music playlist to spotify
import bs4, os, requests, spotipy, sys, pprint, json, re
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from app import app, db
from app.models import User, Search
@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'User': User, 'Search': Search}
###this function gets the beautifulsoup object and return a list of all the song names
### in the playlist
####os.environ['SPOTIPY_CLIENT_ID'] = '32cf9085b1f84393b4bd377279192fed'
####os.environ['SPOTIPY_CLIENT_SECRET'] = '73b90fdafc1f4a07a0cd237238b5d284'
####os.environ['SPOTIPY_REDIRECT_URI'] =  'https://localhost:8080'
####if len(sys.argv) > 1:
####    playlistName = sys.argv[1]
####else:
####    playlistName = 'https://itunes.apple.com/il/playlist/nov18/pl.u-XkD04Mpf2pjzq5'
##def getSongsName(soup):
##    elems = soup.select('.tracklist-item__text__headline')
##    sngs = []
##    for elem in elems:
##        sngs.append((elem.getText()).strip())
##    return sngs
###gets the soup object and returns a list of artists names in the playlist
##def getArtistsName(soup):
##    elems = soup.select('a')
##    artistsName = []
##    for elem in elems:
##        if('data-test-song-artist-url' in elem.attrs):
##            artistsName.append(elem.getText())
##    return artistsName
##playlistName = input("insert apple music playlist link")
##res = requests.get(playlistName)
##res.raise_for_status()
##playlist = bs4.BeautifulSoup(res.text, features="html.parser")
##songs = getSongsName(playlist)
##artists = getArtistsName(playlist)
##combine = zip(songs,artists)
####for item in combine:
####    print(item)
###now we will create a spotify playlist with their API
### create empty playlist:
### asks the user his spotify username, and the playlist details
##playlist_name = (playlist.select('h1')[0].getText()).strip()
##creator_name = (playlist.select('h2')[0].getText()).strip()
##playlist_name += "-" + creator_name
##playlist_description = ('''A copy of the requested playlist from apple music,
##made originally by {}. /n this playlist was converted to spotify by a program made by
##Omer Iedovnik.''').format(creator_name)
##scope='user-library-read playlist-modify-private playlist-modify-public'
##username = input('enter your spotify username:')
###checks in what format the username is and changes it consequently:
###format 1:https://open.spotify.com/user/2112345y25blnvtbp55mjuray?si=ZyLdKCBfSm-7vexohREDnA
##if(username.startswith(r'https://open.spotify.com/user/')):
##    print(username)
##    username = re.split(r'\W+',username)[5]
###format 2:spotify:user:21234x5y25blnvtbp55mjuray    
##elif(username.startswith('spotify:user:')):
##    print(username)
##    username = username[13:]
##elif(not len(username)==25):
##    raise ValueError('username format unknown')
####this authorizes the request
####token = util.prompt_for_user_token(username[13:],scope,client_id='32cf9085b1f84393b4bd377279192fed',
####                           client_secret='73b90fdafc1f4a07a0cd237238b5d284',
####                           redirect_uri='https://localhost:8080')
##token = util.prompt_for_user_token(username, scope)
##
###creates the new playlist
##if token:
##    sp = spotipy.Spotify(auth=token)
##    sp.trace = False
##    playlists = sp.user_playlist_create(username, playlist_name, public=True)
##    pprint.pprint(playlists)
### searches the songs from the apple music playlist (apm)
##songs_missed = 0
##songs_uncertain = 0
##count = 0
##track_ids = []
##for song, artist in combine:
##    found = sp.search(q=song + " " + artist ,type="track", limit=1)
##    try:
##        track_ids.append(found['tracks']['items'][0]['uri'])
##        print(str(count+1) + ":" + found['tracks']['items'][0]['uri'])
##        count+=1
##    except IndexError:
##        #song was not found - remove all characters that are not digits or letters
##        #checks if the search has special chars:
##        if(not song.isalnum() or not artist.isalnum()):
##            second_string = re.split(r'\W+', artist)[0].strip() +' ' + re.split(r'\W+', song)[0].strip()
##            found = sp.search(q=second_string ,type="track", limit=1)
##            try:
##                track_ids.append(found['tracks']['items'][0]['uri'])
##                count+=1
##                print(str(count) + ":" + found['tracks']['items'][0]['uri'])
##                songs_uncertain += 1
##            except IndexError:
##                songs_missed += 1
##        else:
##            songs_missed += 1
##while track_ids: 
##    results = sp.user_playlist_add_tracks(username, playlists['id'], track_ids[:100])
##    track_ids = track_ids[100:]
##print(str(songs_missed) + " songs were missed.\n " + str(songs_uncertain) + " songs are uncertain")
##    


















    
