"""Parse semicolon-delimited IIDS applicant_name fields."""
from __future__ import annotations


def iter_applicant_names(raw: str) -> list[str]:
    """Return non-empty applicant tokens in filing order."""
    text = str(raw or "").strip()
    if not text:
        return []
    names: list[str] = []
    for chunk in text.replace("|", ";").split(";"):
        for part in chunk.split(","):
            name = part.strip()
            if name:
                names.append(name)
    return names


def first_applicant_name(raw: str) -> str:
    names = iter_applicant_names(raw)
    return names[0] if names else ""
