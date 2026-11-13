# philosophers

openakademeia teaching agents, packaged as plugins for Claude Code, Codex, and Cursor.

| Plugin | What it does |
|---|---|
| [plato](plugins/plato) | Teaches an openakademeia course by prediction and repair (MCP server + skill) |

## Install

- **Claude Code**: `/plugin marketplace add openakademeia/philosophers`, then `/plugin install plato@philosophers`
- **Codex**: `codex plugin marketplace add openakademeia/philosophers && codex plugin add plato@philosophers`
- **Cursor**: add `https://github.com/openakademeia/philosophers` as a plugin marketplace

## Marketplace files

`.claude-plugin/marketplace.json` is the source of truth; Claude Code and Codex read it. `.cursor-plugin/marketplace.json` mirrors it for Cursor. Each plugin carries `.claude-plugin/plugin.json` and an Agent Plugins `plugin.json` with the same name, version, and description. When you add or change a plugin, update all four.
