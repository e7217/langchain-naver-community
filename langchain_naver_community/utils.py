"""Util that calls Naver Search API.

In order to set this up, follow instructions at:
https://developers.naver.com/docs/serviceapi/search/news/news.md
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

import aiohttp
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

NAVER_API_URL = "https://openapi.naver.com/v1/search"

SEARCH_TYPE_MAP = {
    "news": "news",
    "blog": "blog",
    "web": "web",
    "webkr": "webkr",
}


class NaverSearchAPIWrapper(BaseModel):
    """Wrapper for Naver Search API."""

    naver_client_id: SecretStr
    naver_client_secret: SecretStr

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate that api key and endpoint exists in environment."""
        naver_client_id = get_from_dict_or_env(
            values, "naver_client_id", "NAVER_CLIENT_ID"
        )
        naver_client_secret = get_from_dict_or_env(
            values, "naver_client_secret", "NAVER_CLIENT_SECRET"
        )
        values["naver_client_id"] = naver_client_id
        values["naver_client_secret"] = naver_client_secret

        return values

    def raw_results(
        self,
        query: str,
        search_type: str = "news",
        display: int | None = 10,
        start: int | None = 1,
        sort: str | None = "sim",  # sim (similarity) or date
    ) -> dict[str, Any]:
        """Get raw results from the Naver Search API."""
        enc_text = urllib.parse.quote(query, encoding="utf-8")
        url = f"{NAVER_API_URL}/{search_type}.json?query={enc_text}&display={display}&start={start}&sort={sort}"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.naver_client_id.get_secret_value())
        request.add_header(
            "X-Naver-Client-Secret", self.naver_client_secret.get_secret_value()
        )

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        if response_code == 200:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
        msg = f"Error Code: {response_code}"
        raise Exception(msg)

    def results(
        self,
        query: str,
        search_type: str = "news",
        display: int | None = 10,
        start: int | None = 1,
        sort: str | None = "sim",
    ) -> list[dict[str, Any]]:
        """Run query through Naver Search and return cleaned results.

        Args:
            query: The query to search for.
            search_type: The type of search (news, blog, webkr, etc.)
            display: The number of results to return (max 100).
            start: The starting position for results.
            sort: The sort order (sim for similarity, date for date).

        Returns:
            A list of dictionaries containing the cleaned search results.
        """
        raw_search_results = self.raw_results(
            query,
            search_type=search_type,
            display=display,
            start=start,
            sort=sort,
        )
        return self.clean_results(raw_search_results["items"])

    async def raw_results_async(
        self,
        query: str,
        search_type: str = "news",
        display: int | None = 10,
        start: int | None = 1,
        sort: str | None = "sim",
    ) -> dict[str, Any]:
        """Get results from the Naver Search API asynchronously."""
        enc_text = urllib.parse.quote(query)
        url = f"{NAVER_API_URL}/{search_type}.json?query={enc_text}&display={display}&start={start}&sort={sort}"

        async def fetch() -> str:
            headers = {
                "X-Naver-Client-Id": self.naver_client_id.get_secret_value(),
                "X-Naver-Client-Secret": self.naver_client_secret.get_secret_value(),
            }

            async with (
                aiohttp.ClientSession() as session,
                session.get(url, headers=headers) as response,
            ):
                if response.status == 200:
                    return await response.text()
                msg = f"Error {response.status}: {response.reason}"
                raise Exception(msg)

        results_json_str = await fetch()
        return json.loads(results_json_str)

    async def results_async(
        self,
        query: str,
        search_type: str = "news",
        display: int | None = 10,
        start: int | None = 1,
        sort: str | None = "sim",
    ) -> list[dict[str, Any]]:
        """Get cleaned results from Naver Search API asynchronously."""
        results_json = await self.raw_results_async(
            query=query,
            search_type=search_type,
            display=display,
            start=start,
            sort=sort,
        )
        return self.clean_results(results_json["items"])

    def clean_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Clean results from Naver Search API."""
        clean_results: list[dict[str, Any]] = []
        for result in results:
            # Remove HTML tags from title and description
            title = result.get("title", "").replace("<b>", "").replace("</b>", "")
            description = (
                result.get("description", "").replace("<b>", "").replace("</b>", "")
            )

            clean_result = {
                "title": title,
                "link": result.get("link", ""),
                "description": description,
            }

            # Add optional fields if they exist
            for field in ["bloggername", "postdate", "pubDate"]:
                if field in result:
                    clean_result[field] = result[field]

            clean_results.append(clean_result)
        return clean_results
