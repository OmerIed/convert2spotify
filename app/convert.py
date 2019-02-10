import bs4, os, requests, spotipy, sys, pprint, json, re
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import urllib
from app import db
from flask import Flask, request, redirect, g, render_template, flash
from app.models import User, Search
from flask_login import current_user
class Convert():
    #This func takes the url and returns a zip of songs+artist, and the playlist name    
    def gethtml(playlistURL):
        res = requests.get(playlistURL)
        res.raise_for_status()
        playlist = bs4.BeautifulSoup(res.text, features="html.parser")
        songs = Convert.getSongsName(playlist)
        artists = Convert.getArtistsName(playlist)
        combine = zip(songs,artists)
        playlist_name = playlist.select('h1')[0].getText()
        creator_name = playlist.select('h2')[0].getText()
        playlist_name += "-" + creator_name
        return combine, playlist_name
    #gets the soup object and returns a list of songs names in the playlist
    def getSongsName(soup):
        elems = soup.select('.tracklist-item__text__headline')
        sngs = []
        for elem in elems:
            sngs.append((elem.getText()).strip())
        return sngs
    #gets the soup object and returns a list of artists names in the playlist
    def getArtistsName(soup):
        elems = soup.select('a')
        artistsName = []
        for elem in elems:
            if('data-test-song-artist-url' in elem.attrs):
                artistsName.append(elem.getText())
        return artistsName
    #formats the username to the needed format for the spotify API
    def formatUsername(username):
        #format 1:https://open.spotify.com/user/2112345y25blnvtbp55mjuray?si=ZyLdKCBfSm-7vexohREDnA
        if(username.startswith(r'https://open.spotify.com/user/')):
            print(username)
            username = re.split(r'\W+',username)[5]
        #format 2:spotify:user:21234x5y25blnvtbp55mjuray    
        elif(username.startswith('spotify:user:')):
            print(username)
            username = username[13:]
        elif(not len(username)==25):
            raise ValueError('username format unknown')
        return username
    #searches the songs on spotify and returns a list of its ids
    def searchSongs(combine, sp):
        songs_missed = 0
        songs_uncertain = 0
        count = 0
        track_ids = []
        for song, artist in combine:
            found = sp.search(q=song + " " + artist ,type="track", limit=1)
            try:
                track_ids.append(found['tracks']['items'][0]['uri'])
                print(str(count+1) + ":" + found['tracks']['items'][0]['uri'])
                count+=1
            except IndexError:
                #song was not found - remove all characters that are not digits or letters
                #checks if the search has special chars:
                if(not song.isalnum() or not artist.isalnum()):
                    second_string = re.split(r'\W+', artist)[0].strip() +' ' + re.split(r'\W+', song)[0].strip()
                    found = sp.search(q=second_string ,type="track", limit=1)
                    try:
                        track_ids.append(found['tracks']['items'][0]['uri'])
                        count+=1
                        print(str(count) + ":" + found['tracks']['items'][0]['uri'])
                        songs_uncertain += 1
                    except IndexError:
                        songs_missed += 1
                else:
                    songs_missed += 1
        return track_ids, songs_missed, songs_uncertain              

    #this func will initialize the conversion
    def init(playlistURL, username):
        # Spotify URLS
        SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
        SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
        SPOTIFY_API_BASE_URL = "https://api.spotify.com"
        scope='user-library-read playlist-modify-private playlist-modify-public'
        API_VERSION = "v1"
        SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
        # Server-side Parameters
        CLIENT_SIDE_URL = "http://127.0.0.1"
        PORT = 5000
        REDIRECT_URI = "http://localhost:5000/callback/"
        auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": scope,
            "client_id": os.environ.get('SPOTIPY_CLIENT_ID')
            }
        url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return redirect(auth_url)
    def after_token(token):
        PLAYLIST_URL = os.environ.get('PLAYLIST_URL')
        print("PLAYLIST URL:" + str(PLAYLIST_URL))
        combine, playlist_name = Convert.gethtml(PLAYLIST_URL)
        username = Convert.formatUsername(os.environ.get('SPOTIFY_USERNAME'))
        print(username)
        if token:
            sp = spotipy.Spotify(auth=token)
            print(sp)
            sp.trace = False
            playlists = sp.user_playlist_create(username, playlist_name, public=True)
        else:
            raise ValueError
        track_ids, songs_missed, songs_uncertain = Convert.searchSongs(combine, sp)
        #adds the songs to spotify using its ids
        while track_ids: 
            results = sp.user_playlist_add_tracks(username, playlists['id'], track_ids[:100])
            track_ids = track_ids[100:]
        if current_user.is_authenticated:    
            search = Search(playlist=PLAYLIST_URL, spusername=username, playlistname=playlist_name, author=current_user)
            db.session.add(search)
            db.session.commit()
            flash('Conversion completed for username {}, playlistlink={}'.format(
                username, PLAYLIST_URL))
        else:
            flash('Conversion completed.')
        return True
        
