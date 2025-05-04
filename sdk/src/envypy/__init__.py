__version__ = "0.0.3"
from edge_functions import EdgeFunctions


class Envypy:
    def __init__(self, api_url, api_key=None):
        self.functions = EdgeFunctions(api_key, api_url)
