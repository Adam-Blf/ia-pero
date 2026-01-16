"""
L'IA Pero - Utility functions
"""


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text with ellipsis if too long.

    Args:
        text: Input text string
        max_length: Maximum length before truncation

    Returns:
        Truncated text with '...' if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def parse_multiline_input(text: str) -> list[str]:
    """
    Parse multiline text input into list of non-empty lines.

    Args:
        text: Multiline text string

    Returns:
        List of stripped, non-empty lines
    """
    return [line.strip() for line in text.strip().split("\n") if line.strip()]


def format_similarity_score(score: float) -> str:
    """
    Format similarity score as percentage.

    Args:
        score: Similarity score between 0 and 1

    Returns:
        Formatted percentage string
    """
    return f"{score:.1%}"
