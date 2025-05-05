__version__ = "0.0.5"
from edge_functions import EdgeFunctions


class envypy:
    def __init__(self, api_url, api_key=None):
        self.functions = EdgeFunctions(api_key, api_url)
