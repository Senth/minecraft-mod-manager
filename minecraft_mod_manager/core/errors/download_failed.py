class DownloadFailed(Exception):
    def __init__(self, status_code: int, reason: str, body: str) -> None:
        self.status_code = status_code
        self.reason = reason
        self.body = body

    def __str__(self) -> str:
        return f"Status code: {self.status_code}, {self.reason}"
