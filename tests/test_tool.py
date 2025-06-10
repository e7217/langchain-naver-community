"""Tests for Naver search tools."""

from unittest.mock import AsyncMock, Mock
import pytest

from langchain_naver_community.tool import (
    NaverSearchResults,
    NaverNewsSearch,
    NaverBlogSearch,
    NaverWebSearch,
    NaverBookSearch,
)
from langchain_naver_community.utils import NaverSearchAPIWrapper


class TestNaverSearchResults:
    """Test cases for NaverSearchResults tool."""

    @pytest.fixture
    def mock_api_wrapper(self):
        """Create a mock API wrapper."""
        wrapper = Mock(spec=NaverSearchAPIWrapper)
        wrapper.results.return_value = [
            {
                "title": "Test Title",
                "link": "https://example.com",
                "description": "Test Description",
            }
        ]
        wrapper.results_async = AsyncMock(
            return_value=[
                {
                    "title": "Test Title Async",
                    "link": "https://example.com",
                    "description": "Test Description Async",
                }
            ]
        )
        return wrapper

    @pytest.fixture
    def search_tool(self, mock_api_wrapper):
        """Create a NaverSearchResults instance with mocked API wrapper."""
        tool = NaverSearchResults()
        tool.api_wrapper = mock_api_wrapper
        return tool

    def test_tool_initialization(self):
        """Test that the tool initializes with correct default values."""
        tool = NaverSearchResults()
        assert tool.name == "naver_search_results_json"
        assert tool.search_type == "news"
        assert tool.display == 10
        assert tool.start == 1
        assert tool.sort == "sim"

    def test_tool_initialization_with_params(self):
        """Test tool initialization with custom parameters."""
        tool = NaverSearchResults(search_type="blog", display=20, start=5, sort="date")
        assert tool.search_type == "blog"
        assert tool.display == 20
        assert tool.start == 5
        assert tool.sort == "date"

    def test_run_success(self, search_tool, mock_api_wrapper):
        """Test successful synchronous search."""
        result = search_tool._run("test query")

        mock_api_wrapper.results.assert_called_once_with(
            "test query", search_type="news", display=10, start=1, sort="sim"
        )
        assert result == [
            {
                "title": "Test Title",
                "link": "https://example.com",
                "description": "Test Description",
            }
        ]

    def test_run_exception(self, search_tool, mock_api_wrapper):
        """Test handling of exceptions during synchronous search."""
        mock_api_wrapper.results.side_effect = Exception("API Error")

        result = search_tool._run("test query")
        assert result == "Exception('API Error')"

    @pytest.mark.asyncio
    async def test_arun_success(self, search_tool, mock_api_wrapper):
        """Test successful asynchronous search."""
        result = await search_tool._arun("test query")

        mock_api_wrapper.results_async.assert_called_once_with(
            "test query", search_type="news", display=10, start=1, sort="sim"
        )
        assert result == [
            {
                "title": "Test Title Async",
                "link": "https://example.com",
                "description": "Test Description Async",
            }
        ]

    @pytest.mark.asyncio
    async def test_arun_exception(self, search_tool, mock_api_wrapper):
        """Test handling of exceptions during asynchronous search."""
        mock_api_wrapper.results_async.side_effect = Exception("Async API Error")

        result = await search_tool._arun("test query")
        assert result == "Exception('Async API Error')"

    def test_invoke_with_dict(self, search_tool):
        """Test invoking the tool with a dictionary input."""
        result = search_tool.invoke({"query": "test query"})
        assert isinstance(result, list)

    def test_invoke_with_string(self, search_tool):
        """Test invoking the tool with a string input."""
        result = search_tool.invoke("test query")
        assert isinstance(result, list)


class TestSpecializedSearchTools:
    """Test cases for specialized search tools."""

    def test_naver_news_search(self):
        """Test NaverNewsSearch initialization."""
        tool = NaverNewsSearch()
        assert tool.name == "naver_news_search"
        assert tool.search_type == "news"
        assert "news" in tool.description.lower()

    def test_naver_blog_search(self):
        """Test NaverBlogSearch initialization."""
        tool = NaverBlogSearch()
        assert tool.name == "naver_blog_search"
        assert tool.search_type == "blog"
        assert "blog" in tool.description.lower()

    def test_naver_web_search(self):
        """Test NaverWebSearch initialization."""
        tool = NaverWebSearch()
        assert tool.name == "naver_web_search"
        assert tool.search_type == "webkr"
        assert "web" in tool.description.lower()

    def test_naver_book_search(self):
        """Test NaverBookSearch initialization."""
        tool = NaverBookSearch()
        assert tool.name == "naver_book_search"
        assert tool.search_type == "book"
        assert "book" in tool.description.lower()

    @pytest.fixture
    def mock_api_wrapper(self):
        """Create a mock API wrapper for specialized tools."""
        wrapper = Mock(spec=NaverSearchAPIWrapper)
        wrapper.results.return_value = [{"title": "Specialized Result"}]
        return wrapper

    def test_specialized_tools_inherit_functionality(self, mock_api_wrapper):
        """Test that specialized tools inherit base functionality."""
        tools = [
            NaverNewsSearch(),
            NaverBlogSearch(),
            NaverWebSearch(),
            NaverBookSearch(),
        ]

        for tool in tools:
            tool.api_wrapper = mock_api_wrapper
            result = tool._run("test query")
            assert result == [{"title": "Specialized Result"}]
