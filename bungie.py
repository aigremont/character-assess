import os
import base64
import requests


class BungieClient:
    BASE_URL = 'https://www.bungie.net/Platform'
    AUTH_URL = 'https://www.bungie.net/en/OAuth/Authorize'
    TOKEN_URL = 'https://www.bungie.net/platform/app/oauth/token/'

    def __init__(self):
        self.api_key = os.environ.get('BUNGIE_API_KEY', '')
        self.client_id = os.environ.get('BUNGIE_CLIENT_ID', '')
        self.client_secret = os.environ.get('BUNGIE_CLIENT_SECRET', '')
        self.base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')

    def _headers(self, access_token=None):
        headers = {'X-API-Key': self.api_key}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        return headers

    def get_auth_url(self):
        redirect_uri = f'{self.base_url}/auth/callback'
        return (
            f'{self.AUTH_URL}'
            f'?client_id={self.client_id}'
            f'&response_type=code'
        )

    def exchange_code(self, code):
        credentials = base64.b64encode(
            f'{self.client_id}:{self.client_secret}'.encode()
        ).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-API-Key': self.api_key,
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
        }
        resp = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_memberships(self, access_token):
        url = f'{self.BASE_URL}/User/GetMembershipsForCurrentUser/'
        resp = requests.get(url, headers=self._headers(access_token), timeout=15)
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 1) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result.get('Response', {})

    def get_characters(self, access_token, membership_type, membership_id):
        components = '100,200,201,202,204,300,301,302,304,900'
        url = (
            f'{self.BASE_URL}/Destiny2/{membership_type}/Profile/{membership_id}/'
            f'?components={components}'
        )
        resp = requests.get(url, headers=self._headers(access_token), timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 1) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result

    def get_activity_history(self, access_token, membership_type, membership_id, character_id):
        url = (
            f'{self.BASE_URL}/Destiny2/{membership_type}/Account/{membership_id}/'
            f'Character/{character_id}/Stats/Activities/?count=10'
        )
        resp = requests.get(url, headers=self._headers(access_token), timeout=15)
        resp.raise_for_status()
        result = resp.json()
        if result.get('ErrorCode', 1) != 1:
            raise Exception(f"Bungie API error: {result.get('Message', 'Unknown error')}")
        return result.get('Response', {})
