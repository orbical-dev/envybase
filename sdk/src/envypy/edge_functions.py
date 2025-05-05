class EdgeFunctions:
    def __init__(self, api_key: str, base_url):
        self.api_key = api_key
        self.base_url = base_url
        if api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            self.headers = {"Content-Type": "application/json"}
