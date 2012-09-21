'''
Play stream from soundcloud through gst
'''

import gst

#our stream to play
music_stream_uri='https://api.soundcloud.com/tracks/58716986/stream?client_id=aa13bebc2d26491f7f8d1e77ae996a64'

#creates a playbin (plays media form an uri) 
player = gst.element_factory_make("playbin", "player")

#set the uri
player.set_property('uri', music_stream_uri)

#start playing
player.set_state(gst.STATE_PLAYING)
print "Volume: ", player.get_property('volume')
player.set_property('volume', 0.5)

print "New Volume: ", player.get_property('volume')

#wait and let the music play
raw_input('Press enter to stop playing...')
