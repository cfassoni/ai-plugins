# ai-plugins

A collection of custom AI agent plugins packaged around the Antigravity plugin layout, with cross-client installation guidance for Claude Code, Codex, and Cursor.

## Repository Structure

Each top-level directory (outside dot-directories) is a self-contained plugin:

```text
ai-plugins/
├── .ai-memory.toml          # ai-memory workspace/project scope config
├── AGENTS.md                # Agent authoring rules and ai-memory routing
├── README.md                # Repository overview and installation guide
├── btg-trader-desk/         # BTG Pactual Trader Desk local MCP plugin
│   ├── plugin.json          # Plugin manifest (name, version, description, prompts)
│   ├── mcp_config.json      # MCP server definitions
│   ├── README.md            # Plugin-specific documentation
│   ├── assets/              # Plugin icon / visual assets (e.g., logo.svg)
│   ├── rules/               # Always-on plugin rules (AGENTS.md)
│   └── skills/              # Agent Skills (<skill-name>/SKILL.md)
└── mythos/                  # 11-agent Greek-mythology-inspired ecosystem plugin
    ├── plugin.json          # Plugin manifest
    ├── mcp_config.json      # Bundled mythos-hevy MCP server definition
    ├── README.md            # Architecture, roster, and MCP setup
    ├── assets/              # Plugin icon (logo.svg)
    ├── agents/              # 11 specialist subagent definitions (mythos-*.md)
    ├── rules/               # Contextual Hermes router & guardrails (AGENTS.md)
    └── skills/              # 11 specialist skills + zero-dep Python CLI tools
```

## Available Plugins

| Plugin | Version | Description | Path |
| :--- | :--- | :--- | :--- |
| **BTG Trader Desk** | `1.0.0` | Connects to the local BTG Pactual Trader Desk MCP server (`http://localhost:7777/mcp`) for quotes, candlestick history, news, corporate events, portfolio positions, orders, financial balances, and research analyses. | [`btg-trader-desk/`](./btg-trader-desk/README.md) |
| **Mythos** | `1.2.0` | An 11-agent Greek-mythology-inspired multi-specialist plugin covering Hermes routing, nutrition (`Higia`), fitness & bundled `hevy-mcp` (`Quiron`), memory/RAG (`Clio`), health record organization (`Epione`), architecture (`Daedalus`), engineering (`Hefesto`), wellbeing (`Psique`), philosophy (`Pitia`), deep research (`Argos`), and quantitative finance (`Plutus`). | [`mythos/`](./mythos/README.md) |

## Installation

### Antigravity (Native Plugin Layout)

Copy or symlink a plugin directory into your Antigravity plugins folder, then enable it on the **Customizations** page:

- **Global (all workspaces):** `~/.gemini/config/plugins/<plugin-name>/`
- **Workspace-scoped:** `<workspace>/.agents/plugins/<plugin-name>/`

On Windows PowerShell (example for `btg-trader-desk`):

```powershell
Copy-Item -Recurse -Force .\btg-trader-desk "$HOME\.gemini\config\plugins\btg-trader-desk"
```

### Other Clients (Claude Code, Codex, Cursor)

Because each plugin uses standard Markdown rules, `SKILL.md` Agent Skills, and JSON MCP server definitions, components map cleanly to other harnesses:

| Plugin Component | Antigravity | Claude Code | Codex | Cursor |
| :--- | :--- | :--- | :--- | :--- |
| **MCP Servers** | `mcp_config.json` (auto-loaded) | Merge `mcpServers` into `~/.claude.json` or `.mcp.json` | Merge into `~/.codex/config.toml` | Merge `mcpServers` into `~/.cursor/mcp.json` or `.cursor/mcp.json` |
| **Agents** | `agents/<name>.md` (auto-loaded) | Copy to `~/.claude/agents/` or `.claude/agents/` | Reference roles in `AGENTS.md` | Reference roles in `AGENTS.md` or custom modes |
| **Skills** | `skills/<name>/SKILL.md` | Copy to `~/.claude/skills/<name>/` or `.claude/skills/<name>/` | Copy to `~/.agents/skills/<name>/` or `.agents/skills/<name>/` | Copy to `~/.cursor/skills/<name>/` or `.agents/skills/<name>/` |
| **Rules** | `rules/AGENTS.md` | Append/include in `CLAUDE.md` | Append/include in `AGENTS.md` | Append/include in `AGENTS.md` or `.cursor/rules/` |

> [!NOTE]
> Check each plugin's own `README.md` for local prerequisites (such as local desktop apps, ports, or environment variables) before enabling it.

## Contributing a New Plugin

1. Create a new top-level `<plugin-name>/` directory in kebab-case.
2. Include `plugin.json` and `README.md`, plus only the subdirectories the plugin actually uses (`mcp_config.json`, `skills/<skill-name>/SKILL.md`, `rules/AGENTS.md`, `agents/`, `hooks.json`, `assets/logo.svg`).
3. Version each plugin independently with [Semantic Versioning](https://semver.org/) in its `plugin.json`, and update the **Available Plugins** table in this `README.md` whenever a plugin is added or bumps its version.
4. Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat(<plugin-name>): ...`, `fix(<plugin-name>): ...`, `docs: ...`).
5. Keep all secrets, tokens, and personal account identifiers out of committed files (use environment variables or local runtime prompts instead).
6. Validate all JSON files before committing. See [`AGENTS.md`](./AGENTS.md) for the full authoring checklist (including `github-app` CLI authentication rules for AI agents).
