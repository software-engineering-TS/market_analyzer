import requests
import streamlit as st
from utils.logger import logger

from config.settings import API_BASE_URL, API_TIMEOUT


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL.rstrip("/")

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        token = st.session_state.get("token")

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _handle_response(self, response: requests.Response) -> dict:
        """Return JSON for successful responses and safe errors otherwise."""
        try:
            response.raise_for_status()
        except requests.HTTPError:
            return {
                "status": "error",
                "message": f"Request failed (HTTP {response.status_code}).",
                "status_code": response.status_code,
            }

        try:
            payload = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            return {
                "status": "error",
                "message": "The server returned an invalid response. Please try again.",
                "status_code": response.status_code,
            }

        if not isinstance(payload, dict):
            return {
                "status": "error",
                "message": "The server returned an unexpected response. Please try again.",
                "status_code": response.status_code,
            }

        return payload

    def _request(self, method: str, endpoint: str, *, params=None, data=None) -> dict:
        """Send an API request with consistent timeout and safe error handling."""
        try:
            logger.info("Sending %s API request", method)
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self._headers(),
                params=params,
                json=data,
                timeout=API_TIMEOUT,
            )
            return self._handle_response(response)

        except requests.Timeout:
            logger.warning("API request timed out")
            return {
                "status": "error",
                "message": "The server took too long to respond. Please try again.",
            }
        except requests.ConnectionError:
            logger.warning("Unable to connect to API server")
            return {
                "status": "error",
                "message": "Unable to connect to the server. Check your connection and try again.",
            }
        except requests.RequestException:
            logger.error("API request failed")
            return {
                "status": "error",
                "message": "Unable to complete the request. Please try again.",
            }

    def get(self, endpoint: str, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data=None):
        return self._request("POST", endpoint, data=data)

    def delete(self, endpoint: str):
        return self._request("DELETE", endpoint)


api_client = APIClient()
