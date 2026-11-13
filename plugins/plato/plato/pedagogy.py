"""Fetch the OpenPedagogy tutor protocol, the teaching method Plato follows, from GitHub."""

import os
import re

import httpx

DEFAULT_PROTOCOL_URL = "https://raw.githubusercontent.com/openakademeia/openpedagogy/main/PROTOCOL.md"
START_MARKER = "<!-- tutor-protocol:start -->"
END_MARKER = "<!-- tutor-protocol:end -->"
# Markers count only on a line of their own; PROTOCOL.md also quotes them inline when describing the span.
SPAN = re.compile(rf"^{re.escape(START_MARKER)}$(.*?)^{re.escape(END_MARKER)}$", re.MULTILINE | re.DOTALL)


class ProtocolError(Exception):
    """The protocol could not be fetched or has no tutor-protocol span."""


def protocol_url() -> str:
    return os.environ.get("OPENPEDAGOGY_PROTOCOL_URL", DEFAULT_PROTOCOL_URL)


def extract_tutor_protocol(document: str) -> str:
    """The self-contained span PROTOCOL.md marks for tutors; the builder-facing parts stay out of the agent's context."""
    match = SPAN.search(document)
    if match is None:
        raise ProtocolError("PROTOCOL.md has no tutor-protocol span")
    return match.group(1).strip()


def fetch_tutor_protocol(http: httpx.Client | None = None, url: str | None = None) -> str:
    http = http or httpx.Client(timeout=10, follow_redirects=True)
    url = url or protocol_url()
    try:
        response = http.get(url)
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise ProtocolError(f"could not fetch {url}: {error}") from error
    return extract_tutor_protocol(response.text)
