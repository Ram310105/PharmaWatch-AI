from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Tuple, TypeVar

T = TypeVar("T")
R = TypeVar("R")


# ==========================================================
# Concurrency cap
# ==========================================================
#
# Groq's free tier is rate-limited to 30 requests per minute
# at the organization level (~1 request every 2 seconds
# sustained). A concurrency of 4-5 workers is enough to
# meaningfully overlap network I/O wait time (each Groq/
# Tavily call is typically 1-3 seconds) without bursting
# past that ceiling and triggering repeated 429 retries,
# which would add latency right back.
#
# If you're on Groq's paid Developer tier (10x higher RPM),
# this can safely be raised — e.g. to 8-10.

DEFAULT_MAX_WORKERS = 4


def run_parallel(
    items: List[T],
    fn: Callable[[T], R],
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> List[Tuple[int, T, R | None, Exception | None]]:
    """
    Run `fn(item)` for every item in `items`, in parallel,
    capped at `max_workers` concurrent calls.

    Results are returned in the SAME ORDER as the input list
    (not completion order), as a list of tuples:

        (original_index, item, result_or_None, exception_or_None)

    This lets callers preserve their existing per-item
    try/except + print logging exactly as before, just
    driven by a parallel map instead of a sequential loop.
    """

    results: List[Tuple[int, T, R | None, Exception | None]] = [
        (i, item, None, None) for i, item in enumerate(items)
    ]

    if not items:
        return results

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        future_to_index = {
            executor.submit(fn, item): i
            for i, item in enumerate(items)
        }

        for future in as_completed(future_to_index):

            index = future_to_index[future]
            item = items[index]

            try:
                result = future.result()
                results[index] = (index, item, result, None)

            except Exception as e:
                results[index] = (index, item, None, e)

    return results