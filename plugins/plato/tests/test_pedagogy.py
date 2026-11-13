import httpx
import pytest

from plato.pedagogy import END_MARKER, START_MARKER, ProtocolError, extract_tutor_protocol, fetch_tutor_protocol

DOCUMENT = f"# For builders\n\nThe span sits between `{START_MARKER}` and `{END_MARKER}`.\n\n{START_MARKER}\n\n# Tutor protocol\n\nYou are a tutor.\n\n{END_MARKER}\n\n# Appendix"


def serving(status: int, body: str) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, text=body)))


def test_extract_keeps_only_the_tutor_protocol_span():
    assert extract_tutor_protocol(DOCUMENT) == "# Tutor protocol\n\nYou are a tutor."


def test_extract_rejects_a_document_without_the_span():
    with pytest.raises(ProtocolError, match="no tutor-protocol span"):
        extract_tutor_protocol("# Something else")


def test_fetch_returns_the_span_from_the_served_document():
    assert fetch_tutor_protocol(serving(200, DOCUMENT), "https://example.test/PROTOCOL.md").startswith("# Tutor protocol")


def test_fetch_failure_raises_protocol_error():
    with pytest.raises(ProtocolError, match="could not fetch"):
        fetch_tutor_protocol(serving(404, "Not Found"), "https://example.test/PROTOCOL.md")
