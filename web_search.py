"""DuckDuckGo text search wrapper."""

from ddgs import DDGS


def search_results(query, max_results=5):
    """Return structured search results; return an empty list on failure."""
    query = query.strip()
    if not query:
        return []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        cleaned = []
        for item in results:
            cleaned.append({
                "title": str(item.get("title") or "Untitled"),
                "url": str(item.get("href") or ""),
                "summary": str(item.get("body") or "No summary available."),
            })
        return cleaned
    except Exception:
        return []


def format_results(query, results):
    if not results:
        return f"No web results were found for: {query}. Check your connection or try another query."
    lines = [f"Web search results for: {query}"]
    for i, item in enumerate(results, 1):
        lines.append(f"\n{i}. {item['title']}\n   URL: {item['url']}\n   Summary: {item['summary']}")
    return "\n".join(lines)


def search_web(query, max_results=5):
    """Search the web and return readable results."""
    if not query.strip():
        return "Please enter a search query."
    results = search_results(query, max_results=max_results)
    return format_results(query, results)


if __name__ == "__main__":
    print(search_web(input("Search the web for: ").strip()))
