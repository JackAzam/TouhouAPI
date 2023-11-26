import os

class TouhouAPI:
    TO_JSON = True
    SAVE_IMAGE = True
    FULL_SEARCH = True

    @classmethod
    def mkfile(cls, dir_path):
        dir_path = os.path.join(os.getcwd(), 'Artist Data')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    @classmethod
    def save_img(cls, save_image=None):
        if save_image is not None:
            cls.SAVE_IMAGE = save_image

    @classmethod
    def save_json(cls, _json=None):
        if _json is not None:
            cls.TO_JSON = _json

    @classmethod
    def full_search(cls, full_search=None):
        if full_search is not None:
            cls.FULL_SEARCH = full_search

    @classmethod
    def verbose(cls, verbose=True):
        if verbose is not None:
            cls.VERBOSE = verbose


class CircleConfig:
    MAX_RESULTS = 10
    ALLOW_BASE_VOICEBANKS = False
    CHILD_TAGS = True
    START = 0
    GET_TOTAL_COUNT = True
    VERBOSE = True

    @classmethod
    def configure(cls, max_results=None, allow_base_voicebanks=None, child_tags=None,
                  start=None, get_total_count=None):
        if max_results is not None:
            cls.MAX_RESULTS = max_results
        if allow_base_voicebanks is not None:
            cls.ALLOW_BASE_VOICEBANKS = allow_base_voicebanks
        if child_tags is not None:
            cls.CHILD_TAGS = child_tags
        if start is not None:
            cls.START = start
        if get_total_count is not None:
            cls.GET_TOTAL_COUNT = get_total_count


class AlbumConfig:
    pass


class SongsConfig:
    pass
