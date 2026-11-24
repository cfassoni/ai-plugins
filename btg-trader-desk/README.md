# BTG Trader Desk Plugin

Antigravity plugin that connects to the local **BTG Pactual Trader Desk** MCP server (`http://localhost:7777/mcp`, Streamable HTTP, MCP protocol `2025-11-25`).

## Prerequisites

1. **BTG Trader Desk** installed and running locally on your machine.
2. **Active logged-in session** in BTG Trader Desk (the local MCP server delegates authentication to your active desktop session and cannot fetch data if logged out).

## Capabilities

Once enabled, the `btg-trader-desk` MCP server and its companion skill/rules support:

- **Quotes (`get_quotes`)**: Real-time asset quotes, volumes, variations, auction data, options metrics, technical indicators, and fundamentals.
- **Historical Prices (`get_historical_price`)**: OHLCV candlesticks across `M1`, `M5`, `M10`, `M15`, `M30`, `H`, `D`, `W`, and `MO` timeframes.
- **News (`get_news`)**: Market and ticker-filtered financial headlines.
- **Corporate Events (`get_events`)**: Dividends, shareholder meetings, splits, and corporate actions.
- **Positions (`get_positions`)**: Custody, blocked, available, collateral, and BTC lending quantities, average prices, PnL, and period returns.
- **Orders (`get_orders`)**: Order history filtered by account, ticker, date range (`yyyy/MM/dd`), strategy (`DT`/`P`), and side (`B`/`S`).
- **Financial (`get_financial`)**: Current/projected/daily balances, margin limits (BMF, BTC, options, forward), PnL, custody, and net worth.
- **Analyses (`get_analysis`)**: BTG Trader Desk research across `ALL`, `CMDT`, `FII`, `TRD`, `ACS`, `BDR`, `FIN`, `MPOL`, `RF`, and `CPTO`.

## Files

- `plugin.json` — Plugin manifest
- `mcp_config.json` — Streamable HTTP MCP server entry (`http://localhost:7777/mcp`)
- `skills/btg-trader-desk/SKILL.md` — Tool parameters, codes, and workflow guidance
- `rules/AGENTS.md` — Data verification and local-session guardrails
- `assets/logo.svg` — Plugin icon
