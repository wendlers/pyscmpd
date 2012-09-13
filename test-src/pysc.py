'''
Soundcloud client test
'''

import soundcloud

# create a client object with your app credentials
client = soundcloud.Client(client_id='aa13bebc2d26491f7f8d1e77ae996a64')

# fetch track to stream
track = client.get('/tracks/58716986')

# get the tracks streaming URL
stream_url = client.get(track.stream_url, allow_redirects=False)

# print the tracks stream URL
print stream_url.location

user_tracks = client.get('/users/griz/tracks');

for res in user_tracks:
	print res.title, res.permalink
