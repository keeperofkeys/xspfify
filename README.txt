Make sure python 3.0 or later is installed on your machine

Visit https://developer.spotify.com/console/get-playlist-tracks/ and obtain an OAUTH token for your Spotify account. These last a limited amount of time (1 hour?) but you can get another one if it expires

- in a text editor, open the xspfify/main.py file and edit the following values:

- set the value of OAUTH_TOKEN to the value obtained above
- set the value of SPOTIFY_USERNAME to your username (otherwise you'll end up with copies of my playlists!)
- set the value of OUTPUT_PATH to a directory path that exists on your computer

- open the console and navigate to the xspfify directory, then run the following commands, one at a time:
> python3 -m venv venv
> source venv/bin/activate
(venv)> easy_install requests
(venv)> python
>>> import main
>>> main.backup_playlists_to_xspf()
