# bungie.py
import os
import base64
import requests

BUNGIE_ROOT = 'https://www.bungie.net/Platform'
AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'

class BungieClient:
    def __init__(self):
        self.api_key = os.environ.get('BUNGIE_API_KEY', '')
        self.client_id = os.environ.get('BUNGIE_CLIENT_ID', '')
        self.client_secret = os.environ.get('BUNGIE_CLIENT_SECRET', '')
        self.base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')

    def _headers(self, access_token=None):
        h = {'X-API-Key': self.api_key}
        if access_token:
            h['Authorization'] = f'Bearer {access_token}'
        return h

    def get_auth_url(self):
        redirect_uri = f"{self.base_url}/auth/callback"
        return (
            f"{AUTH_URL}?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={requests.utils.quote(redirect_uri, safe='')}"
        )

    def exchange_code(self, code):
        redirect_uri = f"{self.base_url}/auth/callback"
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-Key': self.api_key,
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
        }
        resp = requests.post(TOKEN_URL, headers=headers, data=data)
        resp.raise_for_status()
        return resp.json()

    def get_memberships(self, access_token):
        url = f"{BUNGIE_ROOT}/User/GetMembershipsForCurrentUser/"
        resp = requests.get(url, headers=self._headers(access_token))
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 0) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result.get('Response', {})

    def get_characters(self, access_token, membership_type, membership_id):
        components = '100,200,201,202,204,300,301,302,304,900'
        url = (
            f"{BUNGIE_ROOT}/Destiny2/{membership_type}/Profile/{membership_id}/"
            f"?components={components}"
        )
        resp = requests.get(url, headers=self._headers(access_token))
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 0) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result

    def get_activity_history(self, access_token, membership_type, membership_id, character_id):
        url = (
            f"{BUNGIE_ROOT}/Destiny2/{membership_type}/Account/{membership_id}/"
            f"Character/{character_id}/Stats/Activities/?count=10"
        )
        resp = requests.get(url, headers=self._headers(access_token))
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 0) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result.get('Response', {})
