"""Plato MCP server: tools over the openakademeia API, instructed by the plato skill and the OpenPedagogy tutor protocol."""

import base64
from pathlib import Path
from typing import Callable, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import Icon

from plato.client import PlatoClient, connect
from plato.pedagogy import ProtocolError, fetch_tutor_protocol

PACKAGE_DIR = Path(__file__).resolve().parent
# Installed wheels carry SKILL.md inside the package; a source checkout reads it from skills/.
SKILL_PATH = next(
    path for path in (PACKAGE_DIR / "SKILL.md", PACKAGE_DIR.parent / "skills" / "plato" / "SKILL.md") if path.exists()
)
BANNER_PATH = PACKAGE_DIR / "banner.txt"
ICON_PATH = PACKAGE_DIR / "icon.png"


def skill_text() -> str:
    """SKILL.md without its frontmatter block."""
    text = SKILL_PATH.read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.lstrip()


def instructions_text(tutor_protocol: str | None) -> str:
    """The banner with an order to show it once, then the skill, then the tutor protocol, or a pointer to the tool when the fetch failed."""
    banner = BANNER_PATH.read_text().rstrip("\n")
    protocol = tutor_protocol or "The tutor protocol could not be fetched at startup. Call `pedagogy_protocol` before teaching."
    return (
        "In your first reply of every session, show the learner this banner verbatim in a code block, then continue.\n\n"
        f"```\n{banner}\n```\n\n{skill_text()}\n\n{protocol}"
    )


def icon() -> Icon:
    data = base64.b64encode(ICON_PATH.read_bytes()).decode()
    return Icon(src=f"data:image/png;base64,{data}", mime_type="image/png", sizes=["128x128"])


def build_server(client: PlatoClient | None = None, fetch_protocol: Callable[[], str] = fetch_tutor_protocol) -> MCPServer:
    try:
        tutor_protocol: str | None = fetch_protocol()
    except ProtocolError:
        tutor_protocol = None
    server = MCPServer("openakademeia-plato", title="Plato", instructions=instructions_text(tutor_protocol), icons=[icon()])
    state: dict[str, PlatoClient | None] = {"client": client}

    def plato() -> PlatoClient:
        if state["client"] is None:
            state["client"] = connect()
        return state["client"]

    @server.tool(description="The OpenPedagogy tutor protocol: how to teach. Call it if the server instructions did not include it.")
    def pedagogy_protocol() -> str:
        return tutor_protocol or fetch_protocol()

    @server.tool(description="List every course in the openakademeia catalog with its field, subfield, id, and tier.")
    def list_courses() -> list[dict]:
        return plato().list_courses()

    @server.tool(description="Enroll the learner in a course, or resume it, and return the next lesson with its full text and the concept it teaches from the course book.")
    def start_course(field: str, subfield: str, course: str) -> dict:
        return plato().start_course(field, subfield, course)

    @server.tool(description="Return the next unfinished lesson of an enrollment with its full text and the concept it teaches from the course book, or done: true.")
    def next_lesson(enrollment_id: int) -> dict:
        return plato().next_lesson(enrollment_id)

    @server.tool(
        description="Record a finished lesson: the learner's commit, confidence 1-4, outcome, whether the repair was given outright, and any artifact result line."
    )
    def record_attempt(
        enrollment_id: int,
        lesson_id: str,
        commit: str,
        confidence: int,
        outcome: Literal["correct", "wrong"],
        assisted: bool = False,
        artifact_result: str | None = None,
    ) -> dict:
        return plato().record_attempt(enrollment_id, lesson_id, commit, confidence, outcome, assisted, artifact_result)

    @server.tool(description="The learner's plan, weekly streak, and progress in every enrollment.")
    def progress() -> dict:
        return plato().progress()

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
