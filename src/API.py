import aiohttp
import asyncio
import json
import logging


class TDB_URL:
    """
    A class defining constants for the TouhouDB API URL and headers.
    """
    DB_BASE= 'https://touhoudb.com/'
    HEADERS= {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

class Circle:
    circle_identifier={}
    album_list={}
    song_list={}


    async def _circle_details_by_name_or_id(self, identifier, **kwargs):
        """
        Get circle information by name or ID.

        Args:
            identifier (str or int): The name or ID of the circle.
            **kwargs: Additional parameters for the request.

        Returns:
            dict or str: The circle information or an error message.

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request.
        """
        if isinstance(identifier, int):
            return await self.search_by_name(identifier, **kwargs)
        else:
            return await self.search_by_id(identifier, **kwargs)

    async def search_by_name(self, artist_name, **kwargs):
        url = f'{TDB_URL.DB_BASE}api/artists?'

        params = {
            'query': artist_name,
            'allowBaseVoicebanks': str(kwargs.get('allow_base_voicebanks', False)),
            'childTags': str(kwargs.get('child_tags', True)),
            'start': str(kwargs.get('start', 0)),
            'maxResults': str(kwargs.get('max_results', 10)),
            'getTotalCount': str(kwargs.get('get_total_count', True)),
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, params=params, headers=TDB_URL.HEADERS)
            if response.status == 200:
                data = await response.json()
                items = data.get('items', [])
                if items:
                    artist_id = items[0]['id']
                    self.circle_identifier[artist_name] = artist_id  # Store in the dictionary
                    return await self.search_by_id(artist_id)
            return response

    async def search_by_id(self, artist_id=None):
        if artist_id is None:
            raise ValueError("artist_id is required")

        url = f'{TDB_URL.DB_BASE}api/artists/{artist_id}/details'
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=TDB_URL.HEADERS)

            if response.status == 200 and 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                return await response.json()
            else:
                # Handle non-JSON responses, e.g., HTML error page
                return {"error": f"Failed to fetch artist details. Status code: {response.status}"}


class Album:

    def __init__(self, circle_instance):
        """
        Initialize an Album instance.

        Args:
            circle_instance (Circle): An instance of the Circle class for circle-related operations.
        """
        self.circle_instance = circle_instance

    async def fetch_album_details(self, artist_identifier, **kwargs):
        """
        Fetch album details for a given artist identifier.

        Args:
            artist_identifier (str or int): The name or ID of the artist.
            **kwargs: Additional parameters for the request.

        Returns:
            dict or aiohttp.ClientResponse: The album details or the HTTP response.

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request.
        """
        artist_details = await self.circle_instance._circle_details_by_name_or_id(artist_identifier, **kwargs)

        if artist_details:
            artist_id = artist_details.get('id')
            if artist_id is not None:
                self.circle_instance.album_list[artist_identifier] = artist_id  # Store in the dictionary
                return await self._album_list(artist_id, **kwargs)
            else:
                return {"error": f"No artist ID found for {artist_identifier}"}
        else:
            return {"error": f"Failed to fetch artist details for {artist_identifier}"}

    async def _album_list(self, artist_id, **kwargs):
        """
        Get album details using the TouhouDB API.

        Args:
            artist_id (int): The ID of the artist.

        Returns:
            dict or aiohttp.ClientResponse: The album details or the HTTP response.

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request.
        """
        url_instance = TDB_URL()
        album_list_url = f'{url_instance.DB_BASE}api/albums?'

        params = {
            "start": 0,
            "getTotalCount": "true",
            "maxResults": 20,
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

        # Include "artistId" directly in the URL
        if artist_id is not None:
            album_list_url += f'&artistId[]={artist_id}'

        async with aiohttp.ClientSession() as session:
            response = await session.get(album_list_url, params=params, headers=TDB_URL.HEADERS)

            if response.status == 200:
                data = await response.json()

                # Process each album in the response
                for album in data.get('items', []):
                    print(f"  Album Title: {album.get('defaultName')}")
                    print(f"  Album ID: {album.get('id')}")

                    # Call _album_details to get more detailed information for each album
                    await self._album_details(album.get('id'))

                return data
            else:
                # Handle error cases
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

    async def _album_details(self, album_id):
        """
        Get detailed information for a specific album using the TouhouDB API.

        Args:
            album_id (int): The ID of the album.

        Returns:
            dict or aiohttp.ClientResponse: The album details or the HTTP response.

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request.
        """
        album_details_url = f'{TDB_URL.DB_BASE}api/albums/{album_id}/details'
        print(album_details_url)
        async with aiohttp.ClientSession() as session:
            response = await session.get(album_details_url, headers=TDB_URL.HEADERS)

            if response.status == 200 and 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                detailed_info = await response.json()
                # print(f"Detailed Album Information:{json.dumps(detailed_info, ensure_ascii=False, indent=4)} ")

                # Extract songs from the album details
                self.circle_instance.song_list = {}
                for track in detailed_info.get('songs', []):
                    title = track.get('name', 'Unknown Title')
                    song_id = track.get('id', None)
                    if title and song_id is not None:
                        self.circle_instance.song_list[title] = song_id

                print("Songs in the Album:")
                for title, song_id in self.circle_instance.song_list.items():
                    print(f"  {title}: {song_id}")

                return self.circle_instance.song_list
            else:
                print(f"Failed to fetch album details. Status code: {response.status}")
                return {"error": f"Failed to fetch album details. Status code: {response.status}"}

class Songs:
    def __init__(self, album_instance):
        self.album_instance = album_instance
        self.song_list = {}

    async def _songs_for_album(self, album_id):
        # Iterate over the songs in the album and fetch details
        for song_title, song_id in self.album_instance.circle_instance.song_list.items():
            song_details = await self._song_details(song_id, album_id)
            # Add the song details to the song_list dictionary
            self.song_list[song_title] = song_details

    async def _song_details(self, song_id, album_id):
        song_details_url = f'{TDB_URL.DB_BASE}api/songs/{song_id}/details?albumId={album_id}'
        async with aiohttp.ClientSession() as session:
            response = await session.get(song_details_url, headers=TDB_URL.HEADERS)

            if response.status == 200 and 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                detailed_info = await response.json()
                print(f"Detailed Song Information for {song_id}: {json.dumps(detailed_info, ensure_ascii=False, indent=4)} ")
                return detailed_info
            else:
                print(f"Failed to fetch song details. Status code: {response.status}")
                return {"error": f"Failed to fetch song details. Status code: {response.status}"}

async def main():
    circle_instance = Circle()
    album_instance = Album(circle_instance)
    song_instance = Songs(album_instance)

    artist_identifier = "404"
    await album_instance.fetch_album_details(artist_identifier)
    for album_name, album_id in album_instance.circle_instance.album_list.get(artist_identifier):
        print(album_instance.circle_instance.album_list)  # Print the value
        print(type(album_instance.circle_instance.album_list))  # Print the type

        await song_instance._songs_for_album(album_id)

    print(song_instance.song_list)

# Run the event loop
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
