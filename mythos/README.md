# Mythos Plugin

A portable, 11-agent multi-specialist ecosystem inspired by Greek mythology. Coordinated by **Hermes** (`mythos-hermes`), Mythos routes domain queries across nutrition, strength & biomechanics, memory/RAG archiving, non-clinical health organization, systems architecture, software engineering, behavioral wellbeing, spiritual/philosophical inquiry, deep research, and quantitative finance.

## Architecture Overview

```text
                              User Prompt
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │   Hermes (mythos-hermes)      │
                   │   Router & Generalist         │
                   └───────────────┬───────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │ (User-Facing Specialists) │                           │
       ▼                           ▼                           ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│    Higia     │           │    Quiron    │           │   Daedalus   │
│  Nutrition   │           │   Fitness    │           │ Architecture │
└──────┬───────┘           └──────┬───────┘           └──────┬───────┘
       │                          │                          │
       ├──────────────────────────┼──────────────────────────┤
       ▼                          ▼                          ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│    Psique    │           │    Pitia     │           │    Plutus    │
│  Wellbeing   │           │  Philosophy  │           │   Finance    │
└──────┬───────┘           └──────┬───────┘           └──────┬───────┘
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
                   ┌───────────────────────────────┐
                   │     Clio (mythos-clio)        │
                   │  Memory, RAG & Provenance     │
                   └───────────────┬───────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │ (Internal & Cross-Domain Support)                     │
       ▼                           ▼                           ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│    Epione    │           │   Hefesto    │           │    Argos     │
│  Health Rec  │           │ Engineering  │           │ Deep Mining  │
└──────────────┘           └──────────────┘           └──────────────┘
```

## Agent Roster

| Agent | Archetype | Role | Skill | Model Tier | Native Tools | Local CLI Tool |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `mythos-hermes` | Messenger god | Central router & generalist fallback | `mythos-hermes` | `flash` | `read_file`, `search_web` | — |
| `mythos-higia` | Goddess of health | Integrative nutrition & meal balance | `mythos-higia` | `flash` | `read_file`, `edit_file`, `write_file`, `run_command`, `search_web` | `nutrition_calc.py` |
| `mythos-quiron` | Mentor of heroes | Strength, hypertrophy & biomechanics | `mythos-quiron` | `flash` | `read_file`, `edit_file`, `write_file`, `run_command`, `search_web` | `quiron_engine.py` |
| `mythos-clio` | Muse of history | Memory, RAG & provenance custodian | `mythos-clio` | `flash` | `read_file`, `edit_file`, `write_file`, `run_command` | `provenance_validator.py` |
| `mythos-epione` | Caretaker of healing | Non-clinical health record organizer | `mythos-epione` | `pro` | `read_file`, `edit_file`, `write_file`, `search_web` | — |
| `mythos-daedalus` | Master architect | Systems & software architecture | `mythos-daedalus` | `pro` | `read_file`, `edit_file`, `write_file`, `search_web` | — |
| `mythos-hefesto` | God of the forge | Software, tests, containers & CI/CD | `mythos-hefesto` | `inherit` | `read_file`, `edit_file`, `write_file`, `run_command`, `manage_task`, `search_web` | — |
| `mythos-psique` | Personification of mind | Behavioral equilibrium, CBT/ACT & sleep | `mythos-psique` | `pro` | `read_file`, `edit_file`, `write_file`, `search_web` | — |
| `mythos-pitia` | Oracle of Delphi | Comparative religion, philosophy & alchemy | `mythos-pitia` | `inherit` | `read_file`, `edit_file`, `write_file`, `search_web` | — |
| `mythos-argos` | The all-seeing seeker | Deep research, mining & source grading | `mythos-argos` | `pro` | `read_file`, `run_command`, `search_web` | — |
| `mythos-plutus` | Guardian of wealth | Quantitative finance, options & LLM costs | `mythos-plutus` | `pro` | `read_file`, `edit_file`, `write_file`, `run_command`, `search_web` | `finance_calc.py` |

## Model Tiers & Reasoning Effort

- **Per-Agent `model` Tiers:** Every agent definition in `agents/mythos-*.md` declares `inheritMcp: true` plus an abstract `model` tier (`flash` for low-latency routing, daily coaching, and memory retrieval; `pro` for high-stakes architecture, clinical organization, behavioral nuance, deep research, and quantitative finance; `inherit` to match the parent session model for implementation and contemplative guidance).
- **Reasoning Effort & Sampling:** Reasoning effort (`Low`, `Medium`, `High`) is controlled at the active client session level (for example via `/effort` or `--effort` in Antigravity), rather than in per-agent Markdown frontmatter. Determinism for math and validation tasks is enforced via the bundled Python CLI tools.
- **Cross-Client Portability:** Harnesses that do not use abstract `flash` / `pro` / `inherit` tiers (such as Claude Code, Codex, or Cursor) can ignore or map those fields to local model aliases when importing `agents/mythos-*.md`.

## Orchestration Mechanics

- **Contextual Activation:** Rules in `rules/AGENTS.md` engage specialist routing only for Mythos domains or explicit invocations, keeping unrelated IDE/coding tasks unhindered.
- **Sticky Specialist State:** Follow-up turns stay with the active specialist for conversational continuity.
- **Graceful Interruption:** Side-questions to another specialist receive a concise `[Context: ...]` header so cross-domain guidance remains coherent.
- **Generalist Fallback:** Out-of-domain requests (travel, everyday formatting, general reasoning) are answered directly without specialist overhead.

## Bundled & Optional MCP Integrations

Mythos bundles **`mythos-hevy`** (`npx -y hevy-mcp`) in `mcp_config.json` for **Quiron** (`mythos-quiron`), while keeping memory, brokerage, and search MCPs optional (*Bring-Your-Own-MCP*) so they never collide with existing host servers.

### Bundled: Hevy (`mythos-hevy`)

- **Transport:** Stdio (`npx -y hevy-mcp`, requires Node.js/npx)
- **Setup (Antigravity):** Because `mythos-hevy` declares the `HEVY_API_KEY` variable, Antigravity stages the plugin **disabled** on first discovery. Open the **Mythos** plugin page under **Customizations**, enter your `HEVY_API_KEY`, and enable the plugin.
- **Setup (Other Clients):** Copy the `mythos-hevy` entry from `mcp_config.json` into your client's MCP config and supply your `HEVY_API_KEY` environment variable.

### Optional: Memory & Knowledge RAG (`mythos-clio` / `ai-memory`)

Used by **Clio** and all specialists for semantic RAG search and episodic user context:

```json
{
  "mcpServers": {
    "mythos-clio": {
      "url": "http://localhost:8100/mcp",
      "transport": "http"
    }
  }
}
```

### Optional: Brokerage & Market Quotes (`btg-trader-desk`)

Used by **Plutus** for verified quotes, dividends/events, portfolio positions, and financial balances (see [`../btg-trader-desk/`](../btg-trader-desk/README.md)):

```json
{
  "mcpServers": {
    "btg-trader-desk": {
      "url": "http://localhost:7777/mcp",
      "transport": "http"
    }
  }
}
```

### Optional: Deep Search Engine (for Argos)

**Argos** uses native `search_web` by default and can optionally pair with a local SearXNG or web-mining MCP server configured in your host client.

## Bundled Python 3 CLI Tools (Zero External Dependencies)

All bundled CLI tools require only Python 3.10+ standard library and support `--json`:

- `skills/mythos-quiron/scripts/quiron_engine.py` — `calories` (MET + RPE/RIR + EPOC), `e1rm` (Epley & Brzycki), `volume`
- `skills/mythos-higia/scripts/nutrition_calc.py` — `bmr` (Mifflin-St Jeor), `tdee`, `macros`
- `skills/mythos-plutus/scripts/finance_calc.py` — `cagr`, `allocation`, `options-payoff`, `llm-cost`
- `skills/mythos-clio/scripts/provenance_validator.py` — Knowledge Wiki frontmatter, `## Sources & References`, and privacy/secret lint

## Cross-Client Installation

- **Antigravity:** Copy `mythos/` to `~/.gemini/config/plugins/mythos/` (global) or `<workspace>/.agents/plugins/mythos/` (workspace-scoped) and enable it on the **Customizations** page.
- **Claude Code:** Copy `agents/mythos-*.md` to `~/.claude/agents/` (or `.claude/agents/`), copy `skills/mythos-*` to `~/.claude/skills/`, and append `rules/AGENTS.md` to `CLAUDE.md`.
- **Codex / Cursor:** Copy `skills/mythos-*` to `~/.agents/skills/` (or `~/.cursor/skills/`), append `rules/AGENTS.md` to `AGENTS.md` (or `.cursor/rules/`), and reference `agents/mythos-*.md` as role definitions.

## File Inventory

- `plugin.json` — Plugin manifest
- `mcp_config.json` — Bundled `mythos-hevy` MCP server configuration (`HEVY_API_KEY` variable)
- `assets/logo.svg` — Plugin icon
- `rules/AGENTS.md` — Contextual Hermes routing, handoff invariants, and universal guardrails
- `agents/mythos-*.md` — 11 standalone subagent definitions and harmonized SOULs
- `skills/mythos-*/SKILL.md` — 11 specialist skill workflows
- `skills/mythos-{quiron,higia,plutus,clio}/scripts/*.py` — 4 stdlib-only Python CLI utilities
