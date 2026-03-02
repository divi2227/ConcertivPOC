"""
HTTP client for external email service.

POC: calls Dummy Outlook on localhost:8001, authenticates with API key
Production: swap to Microsoft Graph API with OAuth token
"""

import os
import requests


class ThreadNotFoundError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class OutlookGraphClient:

    def __init__(self):
        self.base_url = os.environ.get(
            'OUTLOOK_SERVICE_URL', 'http://localhost:8001/api'
        )
        self.api_key = os.environ.get('OUTLOOK_API_KEY', '')

    def _headers(self) -> dict:
        """Build auth headers for every request."""
        return {'Authorization': f'Bearer {self.api_key}'}

    def _handle_auth_error(self, response):
        """Check for 401 and raise AuthenticationError."""
        if response.status_code == 401:
            error_data = response.json()
            raise AuthenticationError(
                error_data.get('error', 'Authentication failed — invalid API key')
            )

    def get_vendors(self) -> list:
        response = requests.get(
            f'{self.base_url}/vendors', headers=self._headers()
        )
        self._handle_auth_error(response)
        response.raise_for_status()
        data = response.json()
        return data.get('vendors', data)

    def get_clients(self) -> list:
        response = requests.get(
            f'{self.base_url}/clients', headers=self._headers()
        )
        self._handle_auth_error(response)
        response.raise_for_status()
        data = response.json()
        return data.get('clients', data)

    def fetch_thread(self, vendor: str, client: str) -> dict:
        response = requests.post(
            f'{self.base_url}/fetch',
            json={'vendor': vendor, 'client': client},
            headers=self._headers(),
        )
        self._handle_auth_error(response)
        if response.status_code == 404:
            error_data = response.json()
            raise ThreadNotFoundError(
                error_data.get('error', 'Thread not found')
            )
        response.raise_for_status()
        return response.json()
