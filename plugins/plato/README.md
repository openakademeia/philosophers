# Plato

An openakademeia tutor as a plugin. Its teaching method is the [OpenPedagogy](https://github.com/openakademeia/openpedagogy) tutor protocol, fetched from `PROTOCOL.md` on GitHub; its content is the openakademeia course book. The MCP server exposes `pedagogy_protocol` plus five tools over the openakademeia HTTP API (`list_courses`, `start_course`, `next_lesson`, `record_attempt`, `progress`). The `plato` skill maps the protocol onto those tools and adds no method of its own. The server sends the skill and the protocol as its MCP instructions, so clients that load only the MCP server get both. Course text and progress stay on the openakademeia server; the only local file is a learner token in `~/.openakademeia/<host>.token`.

## Layout

| Path | Purpose |
|---|---|
| `.claude-plugin/plugin.json` | Claude Code and Codex manifest |
| `plugin.json` | Agent Plugins 1.0.0 manifest (Cursor and other agent-plugins.org clients) |
| `.mcp.json` | Starts the server with `uvx` from this repo's git subdirectory |
| `skills/plato/` | How to run the protocol over the tools, and `references/setup.md` for connection trouble |
| `plato/` | The Python MCP server (`openakademeia-plato`); `pedagogy.py` fetches the protocol |

## Configure

Needs [uv](https://docs.astral.sh/uv/). Environment: `OPENAKADEMEIA_URL` (default `http://localhost:8080`), optionally `OPENAKADEMEIA_TOKEN`, and optionally `OPENPEDAGOGY_PROTOCOL_URL` to pin or override the protocol (default: `PROTOCOL.md` on openpedagogy's `main`). Without a token, the server creates a free learner on first use and saves its token.

Without the plugin, add the server to any MCP client by hand:

```
uvx --from "git+https://github.com/openakademeia/philosophers#subdirectory=plugins/plato" openakademeia-plato
```

claude.ai and ChatGPT need a hosted server over streamable HTTP, which does not exist yet.

Install it from this repo's marketplace:

```
/plugin marketplace add openakademeia/philosophers
/plugin install plato@philosophers
```

Codex and Cursor steps are in the [root README](../../README.md#install). Then say "Start a course."

## Develop

```
cd plugins/plato
uv run --with pytest --with-requirements ../../../openakademeia/src/requirements.txt pytest
```

Client tests run the real openakademeia server in-process on a temporary database. They look for an `openakademeia` checkout next to this repo; set `OPENAKADEMEIA_REPO` to point elsewhere. Without one they skip.
