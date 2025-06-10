"""Tests for Naver Search API utils."""

import json
from unittest.mock import AsyncMock, Mock, patch
import pytest

from langchain_naver_community.utils import NaverSearchAPIWrapper


class TestNaverSearchAPIWrapper:
    """Test cases for NaverSearchAPIWrapper."""

    @pytest.fixture
    def api_wrapper(self):
        """Create API wrapper with test credentials."""
        return NaverSearchAPIWrapper(
            naver_client_id="test_client_id",
            naver_client_secret="test_client_secret"
        )

    @pytest.fixture
    def mock_response_data(self):
        """Mock response data from Naver API."""
        return {
            "items": [
                {
                    "title": "Test <b>News</b> Title",
                    "link": "https://example.com/news/1",
                    "description": "Test <b>news</b> description",
                    "pubDate": "Thu, 01 Jan 2024 00:00:00 +0900"
                },
                {
                    "title": "Another <b>Article</b>",
                    "link": "https://example.com/news/2",
                    "description": "Another <b>test</b> description",
                    "pubDate": "Fri, 02 Jan 2024 00:00:00 +0900"
                }
            ]
        }

    def test_initialization_with_env_vars(self):
        """Test initialization using environment variables."""
        with patch.dict('os.environ', {
            'NAVER_CLIENT_ID': 'env_client_id',
            'NAVER_CLIENT_SECRET': 'env_client_secret'
        }):
            wrapper = NaverSearchAPIWrapper()
            assert wrapper.naver_client_id.get_secret_value() == 'env_client_id'
            assert wrapper.naver_client_secret.get_secret_value() == 'env_client_secret'

    def test_initialization_with_direct_params(self, api_wrapper):
        """Test initialization with direct parameters."""
        assert api_wrapper.naver_client_id.get_secret_value() == "test_client_id"
        assert api_wrapper.naver_client_secret.get_secret_value() == "test_client_secret"

    @patch('urllib.request.urlopen')
    def test_raw_results_success(self, mock_urlopen, api_wrapper, mock_response_data):
        """Test successful raw_results call."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode('utf-8')
        mock_urlopen.return_value = mock_response

        result = api_wrapper.raw_results("test query")
        
        assert result == mock_response_data
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_raw_results_error(self, mock_urlopen, api_wrapper):
        """Test raw_results with API error."""
        mock_response = Mock()
        mock_response.getcode.return_value = 400
        mock_urlopen.return_value = mock_response

        with pytest.raises(Exception, match="Error Code: 400"):
            api_wrapper.raw_results("test query")

    @patch('urllib.request.urlopen')
    def test_results_with_different_params(self, mock_urlopen, api_wrapper, mock_response_data):
        """Test results method with different parameters."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_data).encode('utf-8')
        mock_urlopen.return_value = mock_response

        result = api_wrapper.results(
            "test query",
            search_type="blog",
            display=20,
            start=5,
            sort="date"
        )
        
        assert len(result) == 2
        assert result[0]["title"] == "Test News Title"  # HTML tags removed
        assert result[0]["description"] == "Test news description"  # HTML tags removed

    def test_clean_results(self, api_wrapper):
        """Test clean_results method."""
        raw_results = [
            {
                "title": "Test <b>Title</b>",
                "link": "https://example.com",
                "description": "Test <b>description</b>",
                "pubDate": "Thu, 01 Jan 2024 00:00:00 +0900",
                "bloggername": "TestBlogger"
            },
            {
                "title": "Another <b>Title</b>",
                "link": "https://example2.com",
                "description": "Another <b>description</b>"
            }
        ]

        cleaned = api_wrapper.clean_results(raw_results)
        
        assert len(cleaned) == 2
        assert cleaned[0]["title"] == "Test Title"
        assert cleaned[0]["description"] == "Test description"
        assert cleaned[0]["link"] == "https://example.com"
        assert cleaned[0]["pubDate"] == "Thu, 01 Jan 2024 00:00:00 +0900"
        assert cleaned[0]["bloggername"] == "TestBlogger"
        assert cleaned[1]["title"] == "Another Title"
        assert "pubDate" not in cleaned[1]  # Optional field not present
        assert "bloggername" not in cleaned[1]  # Optional field not present

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_raw_results_async_success(self, mock_get, api_wrapper, mock_response_data):
        """Test successful async raw_results call."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(mock_response_data))
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await api_wrapper.raw_results_async("test query")
        
        assert result == mock_response_data

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_raw_results_async_error(self, mock_get, api_wrapper):
        """Test async raw_results with API error."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.reason = "Bad Request"
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(Exception, match="Error 400: Bad Request"):
            await api_wrapper.raw_results_async("test query")

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_results_async(self, mock_get, api_wrapper, mock_response_data):
        """Test async results method."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(mock_response_data))
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await api_wrapper.results_async("test query")
        
        assert len(result) == 2
        assert result[0]["title"] == "Test News Title"
        assert result[1]["title"] == "Another Article"

    def test_url_encoding(self, api_wrapper):
        """Test that queries are properly URL encoded."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.getcode.return_value = 200
            mock_response.read.return_value = b'{"items": []}'
            mock_urlopen.return_value = mock_response

            # Test with special characters and Korean text
            api_wrapper.raw_results("테스트 쿼리 with spaces & symbols")
            
            # Verify the URL was properly encoded
            call_args = mock_urlopen.call_args[0][0]
            assert "테스트" not in call_args.full_url  # Korean characters should be encoded
            assert "%20" in call_args.full_url or "+" in call_args.full_url  # Spaces should be encoded

    def test_search_type_parameter(self, api_wrapper):
        """Test different search types in URL construction."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.getcode.return_value = 200
            mock_response.read.return_value = b'{"items": []}'
            mock_urlopen.return_value = mock_response

            search_types = ["news", "blog", "webkr", "book"]
            
            for search_type in search_types:
                api_wrapper.raw_results("test", search_type=search_type)
                call_args = mock_urlopen.call_args[0][0]
                assert f"/{search_type}.json" in call_args.full_url

    def test_headers_in_request(self, api_wrapper):
        """Test that proper headers are set in the request."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.getcode.return_value = 200
            mock_response.read.return_value = b'{"items": []}'
            mock_urlopen.return_value = mock_response

            api_wrapper.raw_results("test")
            
            request = mock_urlopen.call_args[0][0]
            headers = request.headers
            assert headers.get('X-naver-client-id') == 'test_client_id'
            assert headers.get('X-naver-client-secret') == 'test_client_secret'