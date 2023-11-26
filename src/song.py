# song.py

import urllib.parse
import re
import asyncio
import aiohttp
import json
from urls import TDB_USAGE_URL, THWIKI
from circle import Circle, CircleIdentifier
from album import Album, AlbumIdentifier

class SongIdentifier:
    
    CIRCLE_NAME = CircleIdentifier.ARTIST_NAME
    ALBUM_NAME = AlbumIdentifier.ALBUM_NAME
    ALBUM_ID = None
    SONG_NAME = None
    SONG_ID = None
    SONG_LIST = {
        'Song Title': SONG_NAME,
        'Song ID': SONG_ID
    }
    ALBUM_LIST_WITH_SONGS = {**AlbumIdentifier.ALBUM_LIST, **SONG_LIST}

class Songs:
    def __init__(self):
        self.song_identifier = SongIdentifier()
        self.album_instance = Album(Circle())  # Pass a Circle instance directly here
        self.song_list = {}

    async def _songs_by_id(self,  songs_id, **kwargs):
        return await self._songs_details(songs_id **kwargs)
    
    async def search_song_name(self, song_name, **kwargs):
        song_search_url = TDB_USAGE_URL.search_song_id_by_name(song_name)
        async with aiohttp.ClientSession() as session:
            response = await session.get(song_search_url, headers=TDB_USAGE_URL.HEADERS)
            data = await response.json()
            if response.status == 200:
                data = await response.json()
                songs = data.get('items', [])
                if songs:
                    songs_id = songs[0]['id']
                    return await self._song_details(songs_id)
                else:
                    return {"error": f"No album found for {song_name}"}
            else:
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

    async def _song_details(self, song_id, include_lyrics=True):
        song_details_url=TDB_USAGE_URL.get_song_details(song_id)
        async with aiohttp.ClientSession()as session:
            response=await session.get(song_details_url,headers=TDB_USAGE_URL.HEADERS)
            data=await response.json()
            print(json.dumps(data, ensure_ascii=False, indent=4))
            

            if include_lyrics and 'song' in data:
                song_data = data['song']

                if isinstance(song_data, dict):
                    # Extracting the song name
                    song_name = song_data.get('defaultName') or song_data.get('name')

                    # Fetching lyrics based on song name
                    th_api = THWIKI.API_URL
                    th_headers = THWIKI.TH_HEADERS
                    th_params = THWIKI.lyrics_search_by_song_title(song_name)

                    async with aiohttp.ClientSession() as th_session:
                        th_response = await th_session.get(th_api, params=th_params, headers=th_headers)

                        if th_response.status == 200:
                            th_lyrics_data = await th_response.json()
                            th_lyrics_wikitext = th_lyrics_data.get('parse', {}).get('wikitext', '')
                            print(f"Lyrics for {song_name}:\n{th_lyrics_wikitext}")
                        else:
                            print(f"Failed to fetch lyrics for {song_name}. Status code: {th_response.status}")
                else:
                    print(f"Unexpected format for 'song' field. Expected a dictionary, got {type(song_data)}.")


#///////////////////////search via album//////////////////////////////////////////////////////////////
    async def song_list_by_album(self, identifier, **kwargs):
        # Corrected the method call by passing the identifier
        album_details = await self.album_instance._album_details_by_name_or_id(identifier, **kwargs)
        song_list = []
        if "songs" in album_details:
            for song_info in album_details['songs']:
                song_data = song_info.get('song', {})
                song_id = song_data.get('id')
                song_name = song_info.get('name')
                if song_id and song_name:
                    song_list.append({"id": song_id, "name": song_name})
                    print(f"Processing : {song_name}")
                    await self._song_details(song_id)
        return song_list





async def test_song_details():
    songs_instance = Songs()
    song_name = "Feel The Flow"  # Replace with the song name you want to test
    album_name= 'Foreground Eclipse Demo CD Vol.01'
    
    
    await songs_instance.song_list_by_album(album_name)
    #await songs_instance.search_song_name(song_name)
    #await songs_instance.fetch_lyrics("White Wind")

if __name__ == "__main__":
    asyncio.run(test_song_details())

