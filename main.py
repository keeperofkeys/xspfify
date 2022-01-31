#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import requests
from xml.sax.saxutils import escape
import re

SPOTIFY_BASE_URL = 'https://api.spotify.com'
OAUTH_TOKEN = ''  # obtain this at https://developer.spotify.com/console/get-playlist-tracks/
SPOTIFY_USERNAME = 'chisrazor' # set your username
PLAYLIST_LIMIT = 50
SONG_LIMIT = 100
OUTPUT_PATH = '/Users/chris/playlists'  # set this to your desired path
SANITIZER = re.compile('[a-zA-Z ()0-9]+')


def get_auth_header():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + OAUTH_TOKEN
    }


def get_playlists(user_id='me', limit=PLAYLIST_LIMIT, offset=0):
    url = SPOTIFY_BASE_URL + '/v1/' + user_id + '/playlists?limit=' + str(limit) + '&offset=' + str(offset)

    headers = get_auth_header()
    playists = requests.get(url, headers=headers)
    return playists.json()


def get_my_playlists(user_id='me', username=SPOTIFY_USERNAME):
    offset = 0
    playlists = get_playlists(user_id)
    total = playlists['total']
    limit = PLAYLIST_LIMIT
    my_lists = []

    while offset < total:
        playlists = get_playlists(user_id, offset=offset, limit=limit)
        for p in playlists['items']:
            owner = p['owner']['id']
            if owner == username:
                my_lists.append({
                    # 'owner': owner,
                    'name': p['name'],
                    'id': p['id'],
                    'length': p['tracks']['total']
                })
        offset += limit

    return my_lists


def get_playlist_tracks(playlist_id):
    url = SPOTIFY_BASE_URL + '/v1/playlists/' + playlist_id + '/tracks'
    headers = get_auth_header()
    tracks_full = requests.get(url, headers=headers).json()
    tracks = []
    for t in tracks_full['items']:
        tr = t['track']
        tracks.append({
            'title': tr['name'],
            'artist': tr['artists'][0]['name'],
            'album': tr['album']['name']
        })
    return tracks


def get_track_xspf_fragment(track_info, omit_album=True):
    ret_str = "<track>"
    if track_info['artist']:
        ret_str += "<creator>" + escape(track_info['artist']) + "</creator>"
    if track_info['album'] and not omit_album:
        ret_str += "<album>" + escape(track_info['album']) + "</album>"
    if track_info['title']:
        ret_str += "<title>" + escape(track_info['title']) + "</title>"
    ret_str += "</track>"
    return ret_str


def convert_spotify_playlist_to_xspf(playlist_id, omit_album=True):
    tracks_info = get_playlist_tracks(playlist_id)
    xspf = """<?xml version="1.0" encoding="UTF-8"?><playlist version="1" xmlns="http://xspf.org/ns/0/"><trackList>"""
    for track_info in tracks_info:
        xspf += get_track_xspf_fragment(track_info, omit_album=omit_album)

    xspf += """</trackList></playlist>"""
    return xspf


def get_track_details(track_uri):
    url = SPOTIFY_BASE_URL + '/v1/tracks/' + track_uri
    headers = get_auth_header()
    response = requests.get(url, headers=headers)
    return response.json()


def get_basic_track_details(track_uri):
    json = get_track_details(track_uri)
    return {
        'artist': json['artists'][0]['name'],
        'title': json['name'],
        'album': json['album']['name']
    }


def write_playlist_to_xspf_file(playlist_id, filename):
    xspf = convert_spotify_playlist_to_xspf(playlist_id)
    path = OUTPUT_PATH + "/" + filename + ".xspf"
    f = codecs.open(path, "w", "utf-8")
    f.write(xspf)
    f.close()


def make_filename(text):
    return ''.join(SANITIZER.findall(text))


def backup_playlists_to_xspf(user_id='me', username=SPOTIFY_USERNAME):
    playlists = get_my_playlists(user_id, username)
    for playlist in playlists:
        if playlist['length'] <= SONG_LIMIT:
            write_playlist_to_xspf_file(playlist['id'], make_filename(playlist['name']))
