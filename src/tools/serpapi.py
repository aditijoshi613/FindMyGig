"""SerpAPI tool for searching the web (places, events, music-related reviews)."""
import os
from typing import Optional

import httpx
from langchain_core.tools import tool

SERPAPI_BASE = "https://serpapi.com/search"


def _get_api_key() -> str:
    key = os.environ.get("SERPAPI_API_KEY") or os.environ.get("SERPAPI_KEY")
    if not key:
        raise ValueError("Set SERPAPI_API_KEY (or SERPAPI_KEY) in .env")
    return key


@tool
def search_serpapi(
    query: str,
    location: Optional[str] = None,
    num: int = 10,
) -> str:
    """Search the web via SerpAPI (Google results).
    Use for places (venues), events (concerts, gigs), and mentions of music events in reviews.
    query: Search query (e.g. 'live music jazz Washington DC venue', 'jazz concert DC review').
    location: Optional city/region (e.g. 'Washington, DC', 'Brooklyn') to bias results locally.
    num: Max number of results to return (default 10, max 100).
    """
    api_key = _get_api_key()
    params: dict = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": min(num, 100),
    }
    if location:
        params["location"] = location

    with httpx.Client(timeout=20.0) as client:
        resp = client.get(SERPAPI_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("organic_results") or []
    if not results:
        return f"No search results for: {query}"

    out = []
    for r in results[:num]:
        title = r.get("title", "?")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        out.append(f"- {title}\n  {link}\n  {snippet}")
    return "Search results:\n" + "\n\n".join(out)
