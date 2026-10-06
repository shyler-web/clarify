from tavily import TavilyClient

from paydown.config import get_env


def lookup_docs(query: str) -> str:
    api_key = get_env("TAVILY_API_KEY")
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=1)
    results = response.get("results", [])
    if not results:
        return ""
    return results[0].get("content", "")