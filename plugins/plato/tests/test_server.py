import asyncio

from mcp import Client

from plato.server import BANNER_PATH, build_server


def test_server_exposes_the_plato_tools_and_the_protocol_as_instructions():
    server = build_server()

    names = {tool.name for tool in asyncio.run(server.list_tools())}

    assert names == {"list_courses", "start_course", "next_lesson", "record_attempt", "progress"}
    assert "# Plato" in server.instructions
    assert BANNER_PATH.read_text().rstrip() in server.instructions


def test_initialize_carries_the_banner_and_icon():
    server = build_server()

    async def handshake():
        async with Client(server) as client:
            return client.server_info, client.instructions

    info, instructions = asyncio.run(handshake())

    assert info.name == "openakademeia-plato"
    assert info.icons[0].src.startswith("data:image/png;base64,")
    assert "P L A T O" in instructions
