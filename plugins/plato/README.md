# Plato

The openakademeia teaching protocol as a plugin: an MCP server with five tools over the openakademeia HTTP API (`list_courses`, `start_course`, `next_lesson`, `record_attempt`, `progress`), plus the `plato` skill that teaches with them. The server also sends the skill text to the agent as its MCP instructions, so clients that load only the MCP server still get the protocol. Course text and progress stay on the openakademeia server; the only local file is a learner token in `~/.openacademy/<host>.token`.

## Layout

| Path | Purpose |
|---|---|
| `.claude-plugin/plugin.json` | Claude Code and Codex manifest |
| `plugin.json` | Agent Plugins 1.0.0 manifest (Cursor and other agent-plugins.org clients) |
| `.mcp.json` | Starts the server with `uvx` from this repo's git subdirectory |
| `skills/plato/` | The teaching protocol, a tool reference, and `references/setup.md` for connection trouble |
| `plato/` | The Python MCP server (`openacademy-plato`) |

## Configure

Needs [uv](https://docs.astral.sh/uv/). Environment: `OPENACADEMY_URL` (default `http://localhost:8080`) and, optionally, `OPENACADEMY_TOKEN`. Without a token, the server creates a free learner on first use and saves its token.

Without the plugin, add the server to any MCP client by hand:

```
uvx --from "git+https://github.com/openakademeia/philosophers#subdirectory=plugins/plato" openacademy-plato
```

claude.ai and ChatGPT need a hosted server over streamable HTTP, which does not exist yet.

Install it from this repo's marketplace:

```
/plugin install plato --marketplace openakademeia/philosophers
```

Codex and Cursor steps are in the [root README](../../README.md#install). Then say "Start a course."

## Develop

```
cd plugins/plato
uv run --with pytest --with-requirements ../../../openakademeia/src/requirements.txt pytest
```

Client tests run the real openakademeia server in-process on a temporary database. They look for an `openakademeia` checkout next to this repo; set `OPENAKADEMEIA_REPO` to point elsewhere. Without one they skip.
