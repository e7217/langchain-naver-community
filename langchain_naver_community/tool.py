"""Tool for the Naver search API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing_extensions import Literal

from langchain_naver_community.utils import NaverSearchAPIWrapper

if TYPE_CHECKING:
    from langchain_core.callbacks import (
        AsyncCallbackManagerForToolRun,
        CallbackManagerForToolRun,
    )


class NaverInput(BaseModel):
    """Input for the Naver search tool."""

    query: str = Field(description="search query to look up")


class NaverSearchResults(BaseTool):
    """Tool that queries the Naver Search API and gets back json.

    Setup:
        Set environment variables ``NAVER_CLIENT_ID`` and ``NAVER_CLIENT_SECRET``.

        .. code-block:: bash

            pip install -U langchain-naver-community
            export NAVER_CLIENT_ID="your-client-id"
            export NAVER_CLIENT_SECRET="your-client-secret"

    Instantiate:

        .. code-block:: python

            from langchain_naver_community.tool import NaverSearchResults

            tool = NaverSearchResults(
                search_type="news",  # Other options: "blog", "webkr", "image", etc.
                display=10,  # Number of results to return
                start=1,  # Starting position for results
                sort="sim",  # Sort by similarity, can also use "date"
            )

    Invoke:

        .. code-block:: python

            tool.invoke({'query': '최신 한국 뉴스'})  # For Korean news
    """

    name: str = "naver_search_results_json"
    description: str = (
        "A search engine for Korean content using Naver's search API. "
        "Useful for when you need to answer questions about Korean topics, news, blogs, etc. "
        "Input should be a search query in Korean or English."
    )
    args_schema: type[BaseModel] = NaverInput
    search_type: str = "news"
    display: int = 10
    start: int = 1
    sort: Literal["sim", "date"] = "sim"

    api_wrapper: NaverSearchAPIWrapper = Field(default_factory=NaverSearchAPIWrapper)

    def _run(
        self,
        query: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> list[dict] | str:
        """Use the tool."""
        try:
            return self.api_wrapper.results(
                query,
                search_type=self.search_type,
                display=self.display,
                start=self.start,
                sort=self.sort,
            )
        except Exception as e:  # noqa: BLE001
            return repr(e)

    async def _arun(
        self,
        query: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> list[dict] | str:
        """Use the tool asynchronously."""
        try:
            return await self.api_wrapper.results_async(
                query,
                search_type=self.search_type,
                display=self.display,
                start=self.start,
                sort=self.sort,
            )
        except Exception as e:  # noqa: BLE001
            return repr(e)


class NaverNewsSearch(NaverSearchResults):
    """Tool specialized for Naver News search."""

    name: str = "naver_news_search"
    description: str = (
        "A search engine for Korean news using Naver's search API. "
        "Useful for when you need to answer questions about current events in Korea. "
        "Input should be a search query in Korean or English."
    )
    search_type: str = "news"


class NaverBlogSearch(NaverSearchResults):
    """Tool specialized for Naver Blog search."""

    name: str = "naver_blog_search"
    description: str = (
        "A search engine for Korean blogs using Naver's search API. "
        "Useful for when you need to answer questions about Korean opinions, recipes, lifestyle, etc. "
        "Input should be a search query in Korean or English."
    )
    search_type: str = "blog"


class NaverWebSearch(NaverSearchResults):
    """Tool specialized for Naver Web search."""

    name: str = "naver_web_search"
    description: str = (
        "A general web search engine for Korean websites using Naver's search API. "
        "Useful for when you need to find Korean websites and general information. "
        "Input should be a search query in Korean or English."
    )
    search_type: str = "webkr"


class NaverBookSearch(NaverSearchResults):
    """Tool specialized for Naver Book search."""

    name: str = "naver_book_search"
    description: str = (
        "A search engine for Korean books using Naver's search API. "
        "Useful for when you need to find Korean books and general information. "
        "Input should be a search query in Korean or English."
    )
    search_type: str = "book"
