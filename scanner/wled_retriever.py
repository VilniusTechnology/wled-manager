import requests
import sys
import os
import urllib3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.settings_service import get_setting

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WLEDRetriever:
    def __init__(self, ip, timeout=10.0):
        self.ip = ip
        self.timeout = timeout if timeout is not None else get_setting("info_timeout")
        
        # Configure session with retries
        self.session = requests.Session()
        pool_size = 1
        max_retries = get_setting("max_retries") or 3
        # IMPORTANT: Retry on 503 (Service Unavailable) which is common for busy WLED devices
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(self, endpoint):
        """Make a request to WLED device using HTTP only."""
        url = f"http://{self.ip}{endpoint}"
        
        try:
            # Make HTTP request with redirects enabled using the session
            r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 503:
                 # Should have been retried by adapter, but if we still get 503 here, raise error
                 raise Exception(f"Service Unavailable (503) after retries")
        except Exception as e:
            raise Exception(f"Failed to retrieve {endpoint} from {self.ip}: {str(e)}")
        finally:
            # We don't necessarily close session here if we want to reuse it for multiple calls (info, state, cfg)
            # relying on instance garbage collection or user can close?
            # Since WLEDRetriever usage pattern is: init -> get_info -> get_state -> get_cfg -> discard,
            # keeping session open is better for performance (keep-alive).
            pass

    def get_info(self):
        return self._make_request("/json/info")

    def get_state(self):
        return self._make_request("/json/state")

    def get_cfg(self):
        return self._make_request("/json/cfg")
