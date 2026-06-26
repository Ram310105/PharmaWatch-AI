from typing import List
import httpx

from config import (
    NEWS_API_KEY,
    NEWS_LANGUAGE,
    NEWS_PAGE_SIZE,
    NEWS_QUERY,
    NEWS_SORT_BY,
    REQUEST_TIMEOUT,
)

from models.raw_article import RawArticle


class NewsService:
    """
    Fetches the latest news from NewsAPI.

    Responsibilities
    ----------------
    • Fetch latest news
    • Validate API response
    • Convert NewsAPI response into RawArticle objects
    """

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self):

        print("=" * 60)
        print("NewsService Initialization")
        print("=" * 60)
        print(f"NEWS_API_KEY imported = {NEWS_API_KEY}")
        print("=" * 60)
        print("NEWS_API_KEY imported in NewsService =", repr(NEWS_API_KEY))
        if not NEWS_API_KEY:
            raise ValueError(
                "NEWS_API_KEY not found in environment variables."
            )

        self.api_key = NEWS_API_KEY

    # =====================================================
    # Fetch News
    # =====================================================

    def fetch_latest_news(self) -> List[RawArticle]:

        params = {
            "q": NEWS_QUERY,
            "language": NEWS_LANGUAGE,
            "sortBy": NEWS_SORT_BY,
            "pageSize": NEWS_PAGE_SIZE,
            "apiKey": self.api_key,
        }

        try:

            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:

                response = client.get(
                    self.BASE_URL,
                    params=params,
                )

                response.raise_for_status()

                data = response.json()

            articles = data.get("articles", [])

            print(f"Fetched {len(articles)} articles from NewsAPI.")

            return [
                self._normalize(article)
                for article in articles
            ]

        except Exception as e:

            print("=" * 60)
            print("NewsAPI Error")
            print("=" * 60)
            print(e)
            print("=" * 60)

            return []

    # =====================================================
    # Normalize
    # =====================================================

    def _normalize(
        self,
        article: dict,
    ) -> RawArticle:

        return RawArticle(

            title=article.get("title", ""),

            description=article.get("description", ""),

            content=article.get("content"),

            source=article.get(
                "source",
                {},
            ).get(
                "name",
                "Unknown",
            ),

            url=article.get("url", ""),

            published_at=article.get(
                "publishedAt",
                "",
            ),
        )


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    service = NewsService()

    articles = service.fetch_latest_news()

    print("\n")

    for article in articles[:3]:

        print("-" * 60)
        print(article.title)
        print(article.source)