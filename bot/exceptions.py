class ExtractionError(Exception):
    def __init__(self, site, url, reason):
        self.site   = site
        self.url    = url
        self.reason = reason
        super().__init__(f"Failed to extract data from {site} ({url}): {reason}")

class FetchingError(Exception):
    def __init__(self, site, url, reason):
        self.site   = site
        self.url    = url
        self.reason = reason
        super().__init__(f"Failed to fetch data from {site} ({url}): {reason}")
