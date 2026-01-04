# normalize.py
# Text normalization utilities for regex moderation

import re
import unicodedata

_LEET_MAP = str.maketrans({
    "0": "o",
    "1": "i",
    "2": "z",
    "3": "e",
    "4": "a",
    "5": "s",
    "6": "g",
    "7": "t",
    "8": "b",
    "9": "g",
    "@": "a",
    "$": "s",
    "*": "",
    "!": "",
    "?": "",
})

def normalize_text(s: str) -> str:
    """Normalize text for more robust regex matching."""
    if not s:
        return ""

    # Unicode normalize + strip diacritics
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    # Lowercase
    s = s.lower()

    # Common leetspeak substitutions
    s = s.translate(_LEET_MAP)

    # Remove zero-width characters
    s = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", s)

    # Collapse multiple spaces to single space
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n+", "\n", s)

    # Remove separators between SINGLE characters (to catch obfuscated words like "s e x", "s-e-x", "s.e.x", "T.e.l.e")
    # Strategy: detect sequences of single-char words separated by spaces/symbols, then collapse them
    # Use iterative approach to handle variable-length obfuscation
    prev = ""
    max_iter = 30
    iter_count = 0
    while s != prev and iter_count < max_iter:
        prev = s
        iter_count += 1
        # Pattern 1: word boundary + single char + separator(s) + single char + word boundary
        # This handles "s e x", "s-e-x", "s.e.x" -> "sex"
        new_s = re.sub(r"\b(\w)[\s\-\._~]+(\w)\b", lambda m: m.group(1) + m.group(2) if len(m.group(1)) == 1 and len(m.group(2)) == 1 else m.group(0), s)
        if new_s == s:
            # Pattern 2: single char (word boundary) + separator + single char (word boundary) - more flexible
            new_s = re.sub(r"(\b\w\b)[\s\-\._~]+(\b\w\b)", lambda m: m.group(1) + m.group(2) if len(m.group(1)) == 1 and len(m.group(2)) == 1 else m.group(0), s)
        if new_s == s:
            break
        s = new_s

    return s.strip()

