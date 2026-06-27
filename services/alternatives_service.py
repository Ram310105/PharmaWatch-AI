from tavily import TavilyClient

from config import TAVILY_API_KEY_ALTERNATIVES


class AlternativesService:
    """
    Collects web evidence about therapeutic alternatives
    for a given medicine.

    Uses a dedicated Tavily key (TAVILY_API_KEY_ALTERNATIVES)
    so that Drug Alternatives lookups cannot exhaust the
    Tavily credit pool relied on by the core Research Agent.
    """

    MIN_SCORE = 0.30
    MAX_RESULTS = 6
    MAX_CONTENT_LENGTH = 800

    def __init__(self):

        self.client = TavilyClient(
            api_key=TAVILY_API_KEY_ALTERNATIVES
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def collect(
        self,
        medicine_name: str,
    ) -> str:
        """
        Complete retrieval pipeline.

        Medicine name
            ↓
        Tavily Search
            ↓
        Filter
            ↓
        Sort
            ↓
        Format

        Returns formatted evidence ready for the LLM.
        """

        results = self.search(medicine_name)

        return self.format_results(results)

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        medicine_name: str,
    ) -> list[dict]:

        query = self._build_query(medicine_name)

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=self.MAX_RESULTS,
            include_answer=False,
        )

        results = response.get("results", [])

        return self._filter_results(results)

    # ==========================================================
    # QUERY BUILDER
    # ==========================================================

    def _build_query(
        self,
        medicine_name: str,
    ) -> str:

        return (
            f"{medicine_name} therapeutic alternatives "
            f"substitute drug class generic equivalent"
        )

    # ==========================================================
    # FILTER RESULTS
    # ==========================================================

    def _filter_results(
        self,
        results: list[dict],
    ) -> list[dict]:

        filtered = []

        for result in results:

            score = result.get("score", 0)

            if score < self.MIN_SCORE:
                continue

            filtered.append(
                {
                    "title": result.get("title", ""),

                    "url": result.get("url", ""),

                    "score": score,

                    "content": result.get(
                        "content",
                        ""
                    )[: self.MAX_CONTENT_LENGTH],
                }
            )

        filtered.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return filtered

    # ==========================================================
    # FORMAT RESULTS
    # ==========================================================

    def format_results(
        self,
        results: list[dict],
    ) -> str:

        if not results:

            return (
                "No reliable web evidence found "
                "for this medicine."
            )

        formatted = []

        for i, result in enumerate(
            results,
            start=1,
        ):

            formatted.append(
                f"""
================ SOURCE {i} ================

Title:
{result['title']}

Content:
{result['content']}

Source:
{result['url']}

Relevance Score:
{result['score']:.2f}
"""
            )

        return "\n".join(formatted)


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":

    service = AlternativesService()

    evidence = service.collect("Amoxicillin")

    print(evidence)