"""String utilities."""

from typing import Any
import unidecode


def normalize(s: Any) -> Any:
    """Normalize a string for indexing: unidecode and lowercase."""
    if not isinstance(s, str):
        return s
    return unidecode.unidecode(s).lower().strip()
