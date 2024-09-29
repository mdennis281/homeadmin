import requests,time, json
from typing import Dict, Optional, Any, List
from homebridge.models import Device, Room
from datetime import datetime, timedelta
import threading


class HomeBridgeCredential:
    def __init__(self,creds):
        self.access_token = creds['access_token']
        self.token_type = creds['token_type']
        self.expires = creds['expires_in'] + time.time()

    def is_expired(self):
        if time.time() > self.expires:
            return True
        return False

class HomeBridgeAPI:
    """
    Generalized API interface to simplify credential management
    """
    def __init__(self, host: str, user: str, password: str, cache_expiration: int = 300):
        self.host: str = host
        self.user: str = user
        self.password: str = password
        self.credential: Optional[HomeBridgeCredential] = None

        # In-memory cache: stores (response, timestamp) pairs
        self.cache: Dict[str, (Dict[str, Any], datetime)] = {}
        self.cache_expiration = timedelta(seconds=cache_expiration)

    def get_token(self) -> str:
        if not self.credential or self.credential.is_expired():
            self._get_credential()

        return self.credential.access_token

    def _get_credential(self):
        url = f'{self.host}/api/auth/login'
        payload = {
            'username': self.user,
            'password': self.password,
            'otp': ''
        }
        ans = requests.post(url, json=payload)
        ans.raise_for_status()
        if ans.status_code == 201:
            self.credential = HomeBridgeCredential(ans.json())

    def get(self, uri: str, headers: Optional[Dict[str, str]] = None, fresh=True) -> Dict[str, Any]:
        cache_key = uri  # Using the URI as the cache key
        now = datetime.now()

        # Check if the data is cached and still valid
        if cache_key in self.cache and not fresh:
            cached_data, timestamp = self.cache[cache_key]
            if now - timestamp < self.cache_expiration:
                # Serve the cached data immediately
                self._update_cache_in_background(uri, headers)  # Refresh cache in the background
                return cached_data

        # If not cached or expired, fetch from the API and update the cache
        response_data = self._fetch_and_cache(uri, headers)
        return response_data

    def _fetch_and_cache(self, uri: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Fetch the data from the API and store it in the cache."""
        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.get_token()}'
        response = requests.get(f'{self.host}{uri}', headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # Update the cache with the new data and the current timestamp
        self.cache[uri] = (response_data, datetime.now())
        return response_data

    def _update_cache_in_background(self, uri: str, headers: Optional[Dict[str, str]] = None):
        """Start a thread to update the cache in the background."""
        thread = threading.Thread(target=self._fetch_and_cache, args=(uri, headers))
        thread.daemon = True  # Daemon thread will not block program exit
        thread.start()

    def post(self, uri: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.get_token()}'
        response = requests.post(f'{self.host}{uri}', json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def put(self, uri: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.get_token()}'
        response = requests.put(f'{self.host}{uri}', json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def patch(self, uri: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.get_token()}'
        response = requests.patch(f'{self.host}{uri}', json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete(self, uri: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        headers = headers or {}
        headers['Authorization'] = f'Bearer {self.get_token()}'
        response = requests.delete(f'{self.host}{uri}', headers=headers)
        response.raise_for_status()
        return response.json()


class HomeBridgeClient:
    def __init__(self,host, user,password):
        self.api = HomeBridgeAPI(host,user,password)

    def get_pairings(self):
        return self.api.get('/api/server/pairings')
    
    def get_accessories(self) -> List[Device]:
        response = self.api.get('/api/accessories')
        return [Device.from_dict(device_json) for device_json in response]
    
    def get_accessory(self,uniqueId:str):
        return Device.from_dict(self.api.get(f'/api/accessories/{uniqueId}'))
    
    def update_accessory_characteristic(self,device: Device):
        for c in device.get_changed_characteristics():
            self.api.put(f'/api/accessories/{device.uniqueId}',c)
        return self.get_accessory(device.uniqueId)

            
        
    
    def get_accessories_layout(self):
        response = self.api.get('/api/accessories/layout')
        return [Room.from_dict(room_json) for room_json in response]