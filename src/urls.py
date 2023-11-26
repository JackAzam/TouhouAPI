#urls.py

class TDB_USAGE_URL:
    URL = "https://touhoudb.com/"
    HEADERS= {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }

    @staticmethod
    def search_artist_id_by_name(artist_name):
        return f"{TDB_USAGE_URL.URL}api/artists?name={artist_name}"

    @staticmethod
    def get_artist_details(artist_id):
        return f"{TDB_USAGE_URL.URL}api/artists/{artist_id}/details"

    @staticmethod
    def search_album_id_by_name(album_name):
        return f"{TDB_USAGE_URL.URL}api/albums?query={album_name}"

    @staticmethod
    def get_album_details(album_id):
        return f"{TDB_USAGE_URL.URL}api/albums/{album_id}/details"

    @staticmethod
    def search_song_id_by_name(song_name):
        return f"{TDB_USAGE_URL.URL}api/songs?query={song_name}"

    @staticmethod
    def get_song_details(song_id):
        return f"{TDB_USAGE_URL.URL}api/songs/{song_id}/details"


class THWIKI:
    API_URL="https://en.touhouwiki.net/api.php?"
    TH_HEADERS= {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    
    @staticmethod
    def lyrics_search_by_song_title(song_title):
        PARAM={
	        "action": "parse",
	        "format": "json",
	        "page": f"Lyrics: {song_title}",
            "redirect":0,
	        "prop": "wikitext|properties",
	        "utf8": 1,
	        "formatversion": "2"
        }
        return PARAM