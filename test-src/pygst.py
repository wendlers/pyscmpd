'''
Play stream from soundcloud through gst
'''

import gst

def on_tag(bus, msg):
    taglist = msg.parse_tag()
    print('on_tag:')
    for key in taglist.keys():
        print('\t%s = %s' % (key, taglist[key]))

#our stream to play
music_stream_uri='https://api.soundcloud.com/tracks/58716986/stream?client_id=aa13bebc2d26491f7f8d1e77ae996a64'

#creates a playbin (plays media form an uri) 
player = gst.element_factory_make("playbin", "player")

#set the uri
player.set_property('uri', music_stream_uri)

#start playing
player.set_state(gst.STATE_PLAYING)

#listen for tags on the message bus; tag event might be called more than once
bus = player.get_bus()
bus.enable_sync_message_emission()
bus.add_signal_watch()
bus.connect('message::tag', on_tag)

#wait and let the music play
raw_input('Press enter to stop playing...')
