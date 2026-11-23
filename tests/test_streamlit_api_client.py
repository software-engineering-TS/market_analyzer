"""Regression tests for safe Streamlit API client responses."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "streamlit-app"))

from api import client as api_client_module


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setattr(api_client_module.st, "session_state", {})
    return api_client_module.APIClient()


def response(status_code=200, payload=None, json_error=None, text=""):
    result = Mock()
    result.status_code = status_code
    result.text = text
    if json_error is not None:
        result.json.side_effect = json_error
    else:
        result.json.return_value = payload
    if status_code >= 400:
        result.raise_for_status.side_effect = requests.HTTPError("private server detail")
    return result


def test_successful_json_response_is_returned(api_client, monkeypatch):
    expected = {"status": "success", "data": [1, 2]}
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(return_value=response(payload=expected)),
    )

    assert api_client.get("/stocks") == expected


@pytest.mark.parametrize("method", ["GET", "POST", "DELETE"])
def test_all_methods_use_configured_timeout(api_client, monkeypatch, method):
    request = Mock(return_value=response(payload={"status": "success"}))
    monkeypatch.setattr(api_client_module.requests, "request", request)
    monkeypatch.setattr(api_client_module, "API_TIMEOUT", 17)

    getattr(api_client, method.lower())("/resource")

    assert request.call_args.kwargs["timeout"] == 17


def test_http_error_does_not_expose_response_body(api_client, monkeypatch):
    failed = response(status_code=500, text="private database password")
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(return_value=failed),
    )

    result = api_client.get("/resource")

    assert result == {
        "status": "error",
        "message": "Request failed (HTTP 500).",
        "status_code": 500,
    }
    assert "private database password" not in str(result)


def test_invalid_json_response_returns_safe_message(api_client, monkeypatch):
    invalid = response(json_error=ValueError("private response content"))
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(return_value=invalid),
    )

    result = api_client.get("/resource")

    assert result["status"] == "error"
    assert "invalid response" in result["message"].lower()
    assert "private response content" not in str(result)


def test_non_object_json_response_is_rejected(api_client, monkeypatch):
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(return_value=response(payload=["unexpected"])),
    )

    result = api_client.get("/resource")

    assert result["status"] == "error"
    assert "unexpected response" in result["message"].lower()


def test_timeout_returns_friendly_message_without_exception_details(
    api_client, monkeypatch, caplog
):
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(side_effect=requests.Timeout("private host detail")),
    )

    result = api_client.get("/resource")

    assert result["status"] == "error"
    assert "too long" in result["message"].lower()
    assert "private host detail" not in str(result)
    assert "private host detail" not in caplog.text


def test_connection_error_returns_friendly_message(api_client, monkeypatch):
    monkeypatch.setattr(
        api_client_module.requests,
        "request",
        Mock(side_effect=requests.ConnectionError("private host detail")),
    )

    result = api_client.post("/resource", {"value": 1})

    assert result["status"] == "error"
    assert "unable to connect" in result["message"].lower()
    assert "private host detail" not in str(result)


def test_authorization_header_is_attached(api_client, monkeypatch):
    monkeypatch.setattr(api_client_module.st, "session_state", {"token": "test-token"})
    request = Mock(return_value=response(payload={"status": "success"}))
    monkeypatch.setattr(api_client_module.requests, "request", request)

    api_client.get("/me")

    assert request.call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
