import requests


class Nessie:
    API_KEY: str
    API_BASE = "http://api.nessieisreal.com"

    def __init__(self, api_key=""):
        """
        Constructor for the Nessie client class.
        Initializes the API key and session headers.

        Args:
            api_key: The API key for the Nessie API.
        """
        self.API_KEY = api_key
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/json",
            "Origin": "http://api.nessieisreal.com",
            "Content-Type": "application/json",
        }

    def set_key(self, api_key: str):
        """
        Sets the API key for the Nessie API.

        Args:
            api_key: The API key for the Nessie API.
        """
        self.API_KEY = api_key

    def get(self, url: str):
        """
        Makes a GET request to the Nessie API.

        Args:
            url: The URL to make the request to.

        Returns:
            The response from the Nessie API.

        """
        return self.session.get(f"{self.API_BASE}{url}?key={self.API_KEY}")

    def post(self, url: str, data: dict):
        """
        Makes a POST request to the Nessie API.

        Args:
            url: The URL to make the request to.
            data: The data to send in the request.

        Returns:
            The response from the Nessie API.
        """
        return self.session.post(f"{self.API_BASE}{url}?key={self.API_KEY}", json=data)

    def put(self, url: str, data: dict):
        """
        Makes a PUT request to the Nessie API

        Args:
            url: The URL to make the request to.
            data: The data to send in the request.

        Returns:
            The response from the Nessie API.

        """
        return self.session.put(f"{self.API_BASE}{url}?key={self.API_KEY}", json=data)
