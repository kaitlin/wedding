
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
import grooveshark as gs
import simplejson
from local_settings import GS_USER, GS_PASS, PLAYLIST_ID

def song_search(request):
    try:
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        client_ip = request.META['REMOTE_ADDR']
    gs.init()
    search_type = request.GET['search_type']
    search_string = request.GET['search_string']

    results = gs.api_call('get'+search_type+'SearchResults', {'query': search_string, 'country':'USA'}, client_ip)
    r = simplejson.dumps(results['result']['songs'])

    return HttpResponse(client_ip + r)


def add_song(request):
    
    gs.init()
    gs.authenticate_user(GS_USER, GS_PASS)
    songs = gs.api_call('getPlaylistSongs', {'playlistID': PLAYLIST_ID})['result']['songs']
    song_list = []
    for s in songs:
        song_list.append(s['SongID'])


    song_to_add = int(request.GET['SongID'])
    if song_to_add not in song_list:
        song_list.append(song_to_add)
        
        
        update = gs.api_call('setPlaylistSongs', {'playlistID': PLAYLIST_ID, 'songIDs': song_list })

        if update['result']['success'] == 1:
            return render_to_response('songs.html', {'add_success': 1})
        else:
            return render_to_response('songs.html', {'add_success': 0})

    else:
        return render_to_response('songs.html', {'add_success': 2})
