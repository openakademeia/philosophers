# Connecting the Plato MCP server

The plugin starts the server as `uvx --from "git+https://github.com/openakademeia/philosophers#subdirectory=plugins/plato" openakademeia-plato`. When the tools are missing, check these in order:

1. **`uv` is installed.** Run `uvx --version`. If it fails, have the learner install uv (https://docs.astral.sh/uv/), then restart the agent.
2. **The server starts.** Run the command above in a terminal. It should wait silently on stdin; press Ctrl-C to stop it. A traceback points to the failure.
3. **The openakademeia API is reachable.** The server calls `OPENAKADEMEIA_URL` (default `http://localhost:8080`). Run `curl -s "$OPENAKADEMEIA_URL/api/v1/catalog"`; an empty reply means the API is down or the URL is wrong. To change the URL, set it in the environment the agent is launched from.
4. **The tutor protocol is reachable.** The server fetches it from `OPENPEDAGOGY_PROTOCOL_URL` (default `https://raw.githubusercontent.com/openakademeia/openpedagogy/main/PROTOCOL.md`). Run `curl -sI` on that URL; anything but `200` means the server starts without the protocol, and `pedagogy_protocol` fails with the same error.
5. **The client loaded the plugin.** Claude Code: `/mcp` lists `plato`. Codex: `/mcp` in a session. Cursor: Settings → MCP.

Learner identity is the token in `~/.openakademeia/<host>.token`, created on first use. `OPENAKADEMEIA_TOKEN` overrides it, for example to use the same learner on two machines. Deleting the file starts a new learner with no progress.
