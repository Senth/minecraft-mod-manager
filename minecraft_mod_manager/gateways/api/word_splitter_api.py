from ..http import Http

_base_url = "https://word-splitter-5p3pi6z2ma-ew.a.run.app"


class WordSplitterApi:
    def __init__(self, http: Http) -> None:
        self.http = http

    def split_words(self, text: str) -> str:
        return self.http.get(f"{_base_url}/{text}")
