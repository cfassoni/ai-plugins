# BTG Trader Desk Rules

- **Verify payloads before citing numbers**: Whenever you call a `btg-trader-desk` MCP tool, inspect the full JSON response—including `priceUnit`, currency, and enumerated fields (`TradingStatus`, `OrderSide`, `OrderStrategy`, etc.)—before quoting any prices, quantities, balances, or PnL figures.
- **Never fabricate market or account data**: Only report figures directly returned by the `btg-trader-desk` MCP tools. If a field is absent for a given asset type or entitlement, state that it was not returned.
- **Active local session requirement**: If the `btg-trader-desk` MCP server cannot be reached at `http://localhost:7777/mcp` or fails to fetch account/market data, inform the user that the BTG Trader Desk desktop application must be running locally and logged in with an active session.
