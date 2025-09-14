import requests
from agno.tools import tool


@tool(show_result=True)
def search_events(location: str, start_date: str = "", end_date: str = "") -> str:
    """Search public events for a location and optional date range using a simple web API (stub with DuckDuckGo)."""
    q = f"events in {location} {start_date} {end_date}".strip()
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": q}, timeout=10)
        if r.ok:
            # naive slice of content
            return r.text[:5000]
        return f"search failed: {r.status_code}"
    except Exception as e:
        return f"search error: {e}"


@tool(show_result=True)
def get_weather(location: str, month: str = "") -> str:
    """Fetch brief climate info for a location (stub via DuckDuckGo)."""
    q = f"{location} average weather {month}".strip()
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": q}, timeout=10)
        if r.ok:
            return r.text[:5000]
        return f"weather failed: {r.status_code}"
    except Exception as e:
        return f"weather error: {e}"


