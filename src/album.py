# album.py
import asyncio
import aiohttp
from urls import TDB_USAGE_URL
from circle import Circle, CircleIdentifier
import json

class AlbumIdentifier:
    """
    Helper class to store the identifier (ID and name) of a Touhou music album.
    """
    CIRCLE_NAME = CircleIdentifier.ARTIST_NAME
    CIRCLE_ID = CircleIdentifier.ARTIST_ID
    ALBUM_NAME = None
    ALBUM_ID = None
    ALBUM_LIST = {
        'album name': ALBUM_NAME,
        'album ID': ALBUM_ID
    }
class Album:
    """
    Main class for interacting with the TDB API to fetch details about Touhou music albums.

    Attributes:
        - `circle_instance`: An instance of the `Circle` class.
        - `album_identifier`: An instance of `AlbumIdentifier` to store the current album's identifier.
    """
    def __init__(self, circle_instance):
        self.circle_instance = circle_instance
        self.album_identifier = AlbumIdentifier

    async def _search_album_by_circle(self, artist_identifier, **kwargs):
        """
        Search for Touhou music albums associated with a specific circle.

        Args:
            - `artist_identifier`: The name or ID of the circle.
            - `kwargs`: Additional parameters for the search.

        Returns:
            A dictionary containing details about the albums.
        """
        circle_details = await self.circle_instance._circle_details_by_name_or_id(artist_identifier)
        
        if 'error' in circle_details:
            return circle_details

        circle_id = circle_details.get('id')
        if circle_id:
            return await self._album_list(circle_id, **kwargs)
        else:
            return {"error": f"No circle found for {artist_identifier}"}

    async def _album_details_by_name_or_id(self, identifier, **kwargs):
        """
        Internal method to fetch album details either by name or ID.

        Args:
            - `identifier`: The name or ID of the album.
            - `kwargs`: Additional parameters for the search.

        Returns:
            A dictionary containing details about the album.
        """
        if isinstance(identifier, int):
            return await self._album_details_by_id(identifier, **kwargs)
        else:
            return await self._album_details_by_name(identifier, **kwargs)

    async def _album_details_by_name(self, album_name, **kwargs):
        """
        Search for a Touhou music album by name.

        Args:
            - `album_name`: The name of the album.
            - `kwargs`: Additional parameters for the search.

        Returns:
            A dictionary containing details about the album.
        """
        album_search_url = TDB_USAGE_URL.search_album_id_by_name(album_name)
        async with aiohttp.ClientSession() as session:
            response = await session.get(album_search_url, headers=TDB_USAGE_URL.HEADERS)
            if response.status == 200:
                data = await response.json()
                albums = data.get('items', [])
                if albums:
                    album_id = albums[0]['id']
                    return await self._album_details(album_id, **kwargs)
                else:
                    return {"error": f"No album found for {album_name}"}
            else:
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

    async def _album_details_by_id(self, album_id, **kwargs):
        """
        Search for a Touhou music album by ID.

        Args:
            - `album_id`: The ID of the album.

        Returns:
            A dictionary containing details about the album.
        """
        return await self._album_details(album_id, **kwargs)
    
#///////////////////////////main_scrap//////////////////////////////////////////////////////////////////////////
    async def fetch_album_details(self, artist_identifier, **kwargs):
        """
        Fetch details about Touhou music albums associated with a specific circle.

        Args:
            - `artist_identifier`: The name or ID of the circle.
            - `kwargs`: Additional parameters for the search.

        Returns:
            A dictionary containing details about the albums.
        """
        artist_details = await self.circle_instance._circle_details_by_name_or_id(artist_identifier, **kwargs)

        if artist_details:
            artist_id = artist_details.get('id')
            if artist_id is not None:
                self.circle_instance.album_list[artist_identifier] = artist_id
                return await self._album_list(artist_id, **kwargs)
            else:
                return {"error": f"No artist ID found for {artist_identifier}"}
        else:
            return {"error": f"Failed to fetch artist details for {artist_identifier}"}

    async def _album_list(self, artist_id, **kwargs):
        """
        Fetch a list of Touhou music albums associated with a specific circle.

        Args:
            - `artist_id`: The ID of the circle.
            - `kwargs`: Additional parameters for the search.

        Returns:
            A dictionary containing details about the albums.
        """
        url_instance = TDB_USAGE_URL()
        album_list_url = f'{url_instance.URL}api/albums?'

        params = {
            "start": "0",
            "getTotalCount": "True",
            "maxResults": "20",
            "query": "",
            "fields": "AdditionalNames,MainPicture,ReleaseEvent",
            "lang": "Default",
            "nameMatchMode": "Auto",
            "sort": "Name",
            "discTypes": "Unknown",
            "artistParticipationStatus": "OnlyMainAlbums",
            "childVoicebanks": "false",
            "deleted": "false",
        }

        if artist_id is not None:
            album_list_url += f'&artistId[]={artist_id}'

        async with aiohttp.ClientSession() as session:
            response = await session.get(album_list_url, params=params, headers=TDB_USAGE_URL.HEADERS)

            if response.status == 200:
                data = await response.json()

                for album in data.get('items', []):
                    print(f"  Album Title: {album.get('defaultName')}")
                    print(f"  Album ID: {album.get('id')}")
                    await self._album_details(album.get('id'))

                return data
            else:
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

    async def _album_details(self, album_id):
        """
        Fetch details about a specific Touhou music album.

        Args:
            - `album_id`: The ID of the album.

        Returns:
            A dictionary containing details about the album.
        """
        album_details_url= TDB_USAGE_URL.get_album_details(album_id)
        async with aiohttp.ClientSession() as session:
            response = await session.get(album_details_url, headers=TDB_USAGE_URL.HEADERS)
            if response.status == 200 and 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                detailed_info = await response.json()
                print(json.dumps(detailed_info, ensure_ascii=False, indent=4))
                return detailed_info
            else:
                print(f"Failed to fetch album details. Status code: {response.status}")
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

#//////////////////////////////////////end of Main Method Scrap////////////////////////////////////////////////////////////////////////////////////////
async def test_album_details():
    circle_instance = Circle()
    album_instance = Album(circle_instance)
    album_name = 4468  # Replace with the album name you want to search
    artist_identifier='Foreground Eclipse'

    album_details = await album_instance._search_album_by_circle(artist_identifier)

if __name__ == "__main__":
    asyncio.run(test_album_details())
