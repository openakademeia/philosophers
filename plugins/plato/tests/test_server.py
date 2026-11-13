import asyncio

from mcp import Client

from plato.pedagogy import ProtocolError
from plato.server import BANNER_PATH, build_server

PROTOCOL = "# Tutor protocol\n\nYou are a tutor."


def fake_protocol() -> str:
    return PROTOCOL


def unreachable_protocol() -> str:
    raise ProtocolError("offline")


def test_server_exposes_the_plato_tools_and_instructions():
    server = build_server(fetch_protocol=fake_protocol)

    names = {tool.name for tool in asyncio.run(server.list_tools())}

    assert names == {"pedagogy_protocol", "list_courses", "start_course", "next_lesson", "record_attempt", "progress"}
    assert "# Plato" in server.instructions
    assert BANNER_PATH.read_text().rstrip() in server.instructions
    assert server.instructions.endswith(PROTOCOL)


def test_instructions_point_to_the_tool_when_the_protocol_is_unreachable():
    server = build_server(fetch_protocol=unreachable_protocol)

    assert "Call `pedagogy_protocol` before teaching." in server.instructions


def test_pedagogy_protocol_tool_returns_the_tutor_protocol():
    server = build_server(fetch_protocol=fake_protocol)

    async def call():
        async with Client(server) as client:
            return await client.call_tool("pedagogy_protocol", {})

    result = asyncio.run(call())

    assert result.content[0].text == PROTOCOL


def test_initialize_carries_the_banner_and_icon():
    server = build_server(fetch_protocol=fake_protocol)

    async def handshake():
        async with Client(server) as client:
            return client.server_info, client.instructions

    info, instructions = asyncio.run(handshake())

    assert info.name == "openakademeia-plato"
    assert info.icons[0].src.startswith("data:image/png;base64,")
    assert "P L A T O" in instructions
