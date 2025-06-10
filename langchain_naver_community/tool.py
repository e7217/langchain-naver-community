"""Tool for the Naver search API."""

from __future__ import annotations

from datetime import datetime
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


class NaverNewsInput(BaseModel):
    """Input for the Naver news search tool with date filtering."""

    query: str = Field(description="search query to look up")
    target_date: str | None = Field(
        default=None,
        description="target date to filter news (YYYY-MM-DD format). If provided, only news from this date will be returned.",
    )
    min_results: int = Field(
        default=10,
        description="minimum number of results to return. The tool will keep searching until this number is reached or no more results are available.",
    )


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
    max_search_attempts: int = (
        10  # Maximum number of API calls to prevent infinite loops
    )

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
    """Tool specialized for Naver News search with date filtering."""

    name: str = "naver_news_search"
    description: str = (
        "A search engine for Korean news using Naver's search API with date filtering support. "
        "Useful for when you need to answer questions about current events in Korea. "
        "Input should include a search query and optionally a target date (YYYY-MM-DD) and minimum results count."
    )
    args_schema: type[BaseModel] = NaverNewsInput
    search_type: str = "news"

    def _run(
        self,
        query: str,
        target_date: str | None = None,
        min_results: int = 10,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> list[dict] | str:
        """Use the tool with date filtering."""
        try:
            return self._search_with_date_filter(query, target_date, min_results)
        except Exception as e:  # noqa: BLE001
            return repr(e)

    async def _arun(
        self,
        query: str,
        target_date: str | None = None,
        min_results: int = 10,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> list[dict] | str:
        """Use the tool asynchronously with date filtering."""
        try:
            return await self._search_with_date_filter_async(
                query, target_date, min_results
            )
        except Exception as e:  # noqa: BLE001
            return repr(e)

    def _search_with_date_filter(
        self, query: str, target_date: str | None, min_results: int
    ) -> list[dict]:
        """Search with date filtering and duplicate removal."""
        if target_date is None:
            # No date filtering, use original logic
            return self.api_wrapper.results(
                query,
                search_type=self.search_type,
                display=min_results,
                start=self.start,
                sort=self.sort,
            )

        # Parse target date
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}") from e

        all_results = []
        seen_links = set()
        start_pos = 1
        max_display = 100  # Naver API max

        while len(all_results) < min_results:
            # Get results from API
            batch_results = self.api_wrapper.results(
                query,
                search_type=self.search_type,
                display=max_display,
                start=start_pos,
                sort="date",  # Sort by date for better date filtering
            )

            if not batch_results:
                break  # No more results

            # Filter by date and remove duplicates
            filtered_results = []
            for result in batch_results:
                # Skip duplicates
                if result.get("link") in seen_links:
                    continue

                # Check date if pubDate is available
                if "pubDate" in result:
                    try:
                        # pubDate format: "Tue, 10 Dec 2024 09:30:00 +0900"
                        pub_date_str = result["pubDate"]
                        # Parse the date part only
                        pub_date = datetime.strptime(
                            pub_date_str.split(",")[1].split("+")[0].strip(),
                            "%d %b %Y %H:%M:%S",
                        ).date()
                        if pub_date == target_date_obj:
                            filtered_results.append(result)
                            seen_links.add(result.get("link", ""))
                    except (ValueError, IndexError):
                        # If date parsing fails, include the result (fallback)
                        filtered_results.append(result)
                        seen_links.add(result.get("link", ""))
                else:
                    # If no pubDate, include the result
                    filtered_results.append(result)
                    seen_links.add(result.get("link", ""))

            all_results.extend(filtered_results)

            # If we got fewer results than max_display, we've reached the end
            if len(batch_results) < max_display:
                break

            start_pos += max_display

        return all_results[:min_results]

    async def _search_with_date_filter_async(
        self, query: str, target_date: str | None, min_results: int
    ) -> list[dict]:
        """Search with date filtering and duplicate removal (async)."""
        if target_date is None:
            # No date filtering, use original logic
            return await self.api_wrapper.results_async(
                query,
                search_type=self.search_type,
                display=min_results,
                start=self.start,
                sort=self.sort,
            )

        # Parse target date
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}") from e

        all_results = []
        seen_links = set()
        start_pos = 1
        max_display = 100  # Naver API max

        while len(all_results) < min_results:
            # Get results from API
            batch_results = await self.api_wrapper.results_async(
                query,
                search_type=self.search_type,
                display=max_display,
                start=start_pos,
                sort="date",  # Sort by date for better date filtering
            )

            if not batch_results:
                break  # No more results

            # Filter by date and remove duplicates
            filtered_results = []
            for result in batch_results:
                # Skip duplicates
                if result.get("link") in seen_links:
                    continue

                # Check date if pubDate is available
                if "pubDate" in result:
                    try:
                        # pubDate format: "Tue, 10 Dec 2024 09:30:00 +0900"
                        pub_date_str = result["pubDate"]
                        # Parse the date part only
                        pub_date = datetime.strptime(
                            pub_date_str.split(",")[1].split("+")[0].strip(),
                            "%d %b %Y %H:%M:%S",
                        ).date()
                        if pub_date == target_date_obj:
                            filtered_results.append(result)
                            seen_links.add(result.get("link", ""))
                    except (ValueError, IndexError):
                        # If date parsing fails, include the result (fallback)
                        filtered_results.append(result)
                        seen_links.add(result.get("link", ""))
                else:
                    # If no pubDate, include the result
                    filtered_results.append(result)
                    seen_links.add(result.get("link", ""))

            all_results.extend(filtered_results)

            # If we got fewer results than max_display, we've reached the end
            if len(batch_results) < max_display:
                break

            start_pos += max_display

        return all_results[:min_results]


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
