"""Pure-Python reference for the song merge: the spec the Rust port must match."""

import re

QUOTES = str.maketrans(
    {"’": "'", "‘": "'", "ʼ": "'", "“": '"', "”": '"'} | {"–": "-", "—": "-"}
)
BRACKET = re.compile(r"\s*[(\[]([^()\[\]]*)[)\]]")
FEAT_WORDS = {"feat", "feat.", "ft", "ft.", "featuring"}
ARTIST_STOPS = FEAT_WORDS | {"with", "x"}


REMASTER_FILLER = {"version", "digital"}


def _fold(text: str) -> str:
    return " ".join(text.translate(QUOTES).lower().split())


def _is_remaster(words: list[str]) -> bool:
    return any(w.startswith("remaster") for w in words) and all(
        w.startswith("remaster")
        or w in REMASTER_FILLER
        or (len(w) == 4 and w.isascii() and w.isdigit())
        for w in words
    )


def _is_noise(segment: str, *, in_brackets: bool) -> bool:
    words = segment.split()
    if not words:
        return False
    if _is_remaster(words):
        return True
    return words[0] in FEAT_WORDS or (in_brackets and words[0] == "with")


def _title(track: str) -> str:
    text = _fold(track)
    text = BRACKET.sub(
        lambda m: "" if _is_noise(m.group(1), in_brackets=True) else m.group(0), text
    )
    first, *rest = text.split(" - ")
    kept = [first] + [p for p in rest if not _is_noise(p, in_brackets=False)]
    return " - ".join(kept).strip() or _fold(track)


def _artist(artist: str) -> str:
    text = _fold(artist)
    cut = min((i for c in ",;&" if (i := text.find(c)) >= 0), default=len(text))
    words: list[str] = []
    for i, word in enumerate(text[:cut].split()):
        if i > 0 and word in ARTIST_STOPS:
            break
        words.append(word)
    return " ".join(words) or text


def song_key(track: str, artist: str) -> tuple[str, str]:
    return (_title(track), _artist(artist))
