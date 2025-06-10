"""Pytest configuration for langchain-naver-community tests."""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["NAVER_CLIENT_ID"] = "test_client_id"
    os.environ["NAVER_CLIENT_SECRET"] = "test_client_secret"