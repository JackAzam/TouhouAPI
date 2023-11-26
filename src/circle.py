# src/circle.py
import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



import aiohttp
import asyncio
import json
from urls import TDB_USAGE_URL
from util.general import CircleConfig

class CircleIdentifier:
    ARTIST_ID = None
    ARTIST_NAME = None

class Circle:
    def __init__(self, config=None):
        self.circle_identifier = CircleIdentifier()
        self.config = config or CircleConfig()

    async def _circle_details_by_name_or_id(self, identifier, **kwargs):
        if isinstance(identifier, int):
            return await self.search_by_id(identifier, **kwargs)
        else:
            return await self.search_by_name(identifier, **kwargs)

    async def search_by_name(self, artist_name, **kwargs):
        url = TDB_USAGE_URL.search_artist_id_by_name(artist_name)
        params = {
            'query': artist_name,
            'allowBaseVoicebanks': str(self.config.ALLOW_BASE_VOICEBANKS),
            'childTags': str(self.config.CHILD_TAGS),
            'start': str(self.config.START),
            'maxResults': str(self.config.MAX_RESULTS),
            'getTotalCount': str(self.config.GET_TOTAL_COUNT),
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, params=params, headers=TDB_USAGE_URL.HEADERS)
            if response.status == 200:
                data = await response.json()
                items = data.get('items', [])
                if items:
                    artist_id = items[0]['id']
                    self.circle_identifier.ARTIST_NAME = artist_name
                    self.circle_identifier.ARTIST_ID = artist_id
                    return await self.search_by_id(artist_id)
            return response

    async def search_by_id(self, artist_id=None):
        if artist_id is None:
            raise ValueError("artist_id is required")

        url = TDB_USAGE_URL.get_artist_details(artist_id)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=TDB_USAGE_URL.HEADERS)
            if response.status == 200 and 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                return await response.json()
            else:
                # Handle non-JSON responses, e.g., HTML error page
                return {"error": f"Failed to fetch artist details. Status code: {response.status}"}

async def test_circle_details():
    circle_config = CircleConfig()
    circle_instance = Circle(config=circle_config)
    circle_name = "FELT"  # Replace with the circle name you want to search

    circle_details = await circle_instance._circle_details_by_name_or_id(circle_name)
    print("Circle Details:", json.dumps(circle_details, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    asyncio.run(test_circle_details())
