def normalize_to_solution_url(url: str) -> str:
    """
    force SHL URLs into the ground-truth-compatible format:
    https://www.shl.com/solutions/products/...
    """
    if not isinstance(url, str):
        return url

    url = url.strip()

    if url.startswith("https://www.shl.com/products/"):
        return url.replace(
            "https://www.shl.com/products/",
            "https://www.shl.com/solutions/products/"
        )

    return url
