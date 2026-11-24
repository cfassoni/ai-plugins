---
name: btg-trader-desk
description: >-
  Query market data, quotes, candlesticks, news, corporate events, portfolio
  positions, orders, financial balances, and research analyses through the local
  BTG Trader Desk MCP server (http://localhost:7777/mcp). Use whenever the user
  asks about B3/Brazilian or BTG Trader Desk market quotes, portfolio holdings,
  orders, PnL, balances, or BTG research analyses.
---

# BTG Trader Desk MCP Guide

The `btg-trader-desk` MCP server exposes live market data, account positions,
orders, financial balances, and research analyses from the locally running
**BTG Pactual Trader Desk** application via Streamable HTTP at
`http://localhost:7777/mcp` (MCP Protocol `2025-11-25`).

## Prerequisites & Connection Behavior

- **Local-only endpoint**: `http://localhost:7777/mcp` requires no MCP-level
  credentials or OAuth tokens.
- **Active Trader Desk session required**: The BTG Trader Desk desktop app must
  be running on the user's machine and logged in with an active session. Without
  an active login session, queries cannot retrieve data.
- **Inspect JSON before quoting**: Always inspect the full JSON response from
  each tool before reporting numbers, and check `priceUnit` when formatting
  prices or volumes.

## Available Tools & Parameters

Tool names exposed by the MCP server follow the BTG Trader Desk specification
(check exact discovered names on `btg-trader-desk` if prefixed).

### 1. Quotes (`get_quotes`)
Returns real-time quote, instrument metadata, prices, trading volumes, variations,
auction data, and (when applicable) options metrics, technical indicators, and
fundamentals.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `symbol` | Yes | `string` | Asset ticker, e.g. `VALE3`, `PETR4`. |

- Price fields use the unit specified in `priceUnit`.
- Enumerated fields include `TradingStatus`, `TradeAggressor`, and `OrderSide`.

### 2. Financial News (`get_news`)
Queries financial market news and headlines.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `symbol` | No | `string` | Filter news by ticker, e.g. `VALE3`, `PETR4`. |

### 3. Corporate & Market Events (`get_events`)
Returns corporate and market events for an asset (shareholder meetings,
dividends, stock splits, and corporate actions).

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `symbol` | Yes | `string` | Asset ticker, e.g. `VALE3`, `PETR4`. |

### 4. Historical Prices / Candlesticks (`get_historical_price`)
Returns historical OHLCV candlestick data. Response items include `symbol`,
`period` (`CandlestickPeriod`), `time`, and price fields expressed in `priceUnit`.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `symbol` | Yes | `string` | Asset ticker, e.g. `VALE3`, `PETR4`. |
| `period` | No | `string` | `M1`, `M5`, `M10`, `M15`, `M30`, `H`, `D`, `W`, `MO`. |
| `quantity` | No | `string` | Number of candles to return (default: `"252"`). |

Period codes:
- `M1` (1 min), `M5` (5 min), `M10` (10 min), `M15` (15 min), `M30` (30 min)
- `H` (hour), `D` (day), `W` (week), `MO` (month)

### 5. Portfolio Positions (`get_positions`)
Returns account and asset positions: quantities (custody, blocked, available,
collateral, BTC lending), traded volumes, average prices, results (open, closed,
realized, total PnL), and profitability indicators (month, quarter, semester,
year). Uses enums `OrderStrategy`, `PositionType`, `SecurityType`, `OptionType`,
and `OrderSide`.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `account` | No | `string` | Account number. Omit to use the active login account. |

### 6. Order History (`get_orders`)
Queries client trading orders (creation, execution, rejection, cancellation,
limits, quantity, price, and trading environment details).

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `account` | No | `string` | Account number. Omit to use the active login account. |
| `symbol` | No | `string` | Asset ticker filter, e.g. `VALE3`, `PETR4`. |
| `start_date` | No | `string` | Start date in `yyyy/MM/dd` format. |
| `end_date` | No | `string` | End date in `yyyy/MM/dd` format (defaults to `start_date` if omitted). |
| `strategy` | No | `string` | `DT` (Day Trade) or `P` (Position, default). |
| `side` | No | `string` | `B` (Buy / Compra) or `S` (Sell / Venda). |

### 7. Financial Position (`get_financial`)
Returns account financial summary: balances (current, projected, daily), limits
and warranty margins (BMF, BTC, options, forward), open/closed/total PnL,
custody, net worth, and client/office registration data.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `account` | No | `string` | Account number. Omit to use the active login account. |

### 8. Research Analyses (`get_analysis`)
Returns research and market analyses from BTG Trader Desk's Análises tool.

| Parameter | Required | Type | Notes |
| :--- | :--- | :--- | :--- |
| `symbol` | No | `string` | Asset ticker filter, e.g. `VALE3`, `PETR4`. |
| `category` | No | `string` | One of the category codes listed below. |

Accepted `category` values:
- `ALL`: Todas as fontes (All sources)
- `CMDT`: Commodities
- `FII`: FIIs
- `TRD`: Análise Técnica (Technical Analysis)
- `ACS`: Ações (Equities)
- `BDR`: BDR
- `FIN`: Fundos (Funds)
- `MPOL`: Macro
- `RF`: Renda Fixa (Fixed Income)
- `CPTO`: Cripto (Crypto)

## Troubleshooting

- **Connection refused / server unavailable**: Ask the user to confirm BTG
  Trader Desk is open and running locally, listening on `http://localhost:7777/mcp`.
- **Empty or unauthorized responses**: Remind the user that BTG Trader Desk must
  have an active logged-in session before the local MCP server can return data.
- **Missing fields on certain tickers**: Field availability depends on asset
  type (e.g., equities vs. options vs. FIIs) and user entitlements in Trader Desk.
