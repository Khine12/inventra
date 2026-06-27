# Inventra MCP Tool Contracts

Source: `app/mcp_server.py`. Input schemas are the literal JSON Schema served by `tools/list` (via FastMCP, derived from the Python signatures). Output shapes are the literal dicts returned by each tool function, confirmed by direct invocation and by `tools/call` over the real stdio transport.

---

## `lookup_stock`

> Look up a single product's stock by id, or list all products if product_id is omitted.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "product_id": {
      "anyOf": [{ "type": "integer" }, { "type": "null" }],
      "default": null,
      "title": "Product Id"
    }
  },
  "title": "lookup_stockArguments"
}
```
`product_id` — optional `int`, defaults to `null` (omit/null → list all products for the owner).

**Output — `product_id` omitted (list):**
```json
{
  "success": true,
  "products": [
    {
      "id": 4,
      "name": "ice cream",
      "sku": "D-111",
      "quantity": 25,
      "price": 5.99,
      "cost_price": 2.0,
      "low_stock_threshold": 10,
      "expiry_date": null,
      "created_at": "2026-04-11T00:43:25.965483+00:00"
    }
  ]
}
```

**Output — `product_id` given (single):**
```json
{
  "success": true,
  "product": {
    "id": 4,
    "name": "ice cream",
    "sku": "D-111",
    "quantity": 25,
    "price": 5.99,
    "cost_price": 2.0,
    "low_stock_threshold": 10,
    "expiry_date": null,
    "created_at": "2026-04-11T00:43:25.965483+00:00"
  }
}
```

**Output — product not found:**
```json
{
  "success": false,
  "error": "product_not_found",
  "product_id": 999999999
}
```

---

## `record_transaction`

> Record a sale or restock for a product. Sales are refused if they would drive stock below zero.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "product_id": { "title": "Product Id", "type": "integer" },
    "type": { "title": "Type", "type": "string" },
    "quantity": { "title": "Quantity", "type": "integer" },
    "note": {
      "anyOf": [{ "type": "string" }, { "type": "null" }],
      "default": null,
      "title": "Note"
    }
  },
  "required": ["product_id", "type", "quantity"],
  "title": "record_transactionArguments"
}
```
`product_id` — required `int`. `type` — required `str`, must be `"sale"` or `"restock"` (validated against `TransactionType`). `quantity` — required `int`. `note` — optional `str`, defaults to `null`.

**Output — success:**
```json
{
  "success": true,
  "transaction": {
    "id": 9,
    "product_id": 4,
    "product_name": "ice cream",
    "type": "restock",
    "quantity": 1,
    "note": "mcp smoke test restock",
    "created_at": "2026-06-27T16:07:42.272951+00:00"
  }
}
```

**Output — insufficient stock (structured, not a plain string):**
```json
{
  "success": false,
  "error": "insufficient_stock",
  "product_id": 4,
  "available": 25,
  "requested": 999999,
  "message": "Not enough stock. Available: 25, requested: 999999"
}
```

**Output — invalid type:**
```json
{
  "success": false,
  "error": "invalid_type",
  "message": "type must be 'sale' or 'restock', got 'scrap'"
}
```

**Output — product not found:**
```json
{
  "success": false,
  "error": "product_not_found",
  "product_id": 999999999
}
```

---

## `list_low_stock`

> List products at or under their low-stock threshold.

**Input schema:**
```json
{
  "type": "object",
  "properties": {},
  "title": "list_low_stockArguments"
}
```
No parameters.

**Output:**
```json
{
  "success": true,
  "products": []
}
```
(`products` is a list of the same per-product shape as in `lookup_stock` — `id`, `name`, `sku`, `quantity`, `price`, `cost_price`, `low_stock_threshold`, `expiry_date`, `created_at`.)

---

## `list_expiring`

> List products expiring within the given number of days (default 7).

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "days": { "default": 7, "title": "Days", "type": "integer" }
  },
  "title": "list_expiringArguments"
}
```
`days` — optional `int`, defaults to `7`.

**Output:**
```json
{
  "success": true,
  "products": [
    {
      "id": 14,
      "name": "milk",
      "sku": "M-001",
      "quantity": 16,
      "price": 3.99,
      "cost_price": 0.0,
      "low_stock_threshold": 5,
      "expiry_date": "2026-04-23T00:00:00+00:00",
      "created_at": "2026-04-11T07:26:23.435900+00:00"
    }
  ]
}
```

---

## `get_dashboard_summary`

> Get total product count, low-stock count, and expiring-soon count.

**Input schema:**
```json
{
  "type": "object",
  "properties": {},
  "title": "get_dashboard_summaryArguments"
}
```
No parameters.

**Output:**
```json
{
  "success": true,
  "total_products": 5,
  "low_stock_count": 0,
  "expiring_soon_count": 3
}
```

---

## `get_revenue_analytics`

> Get daily revenue/cost/profit breakdown and totals from recorded sales.

**Input schema:**
```json
{
  "type": "object",
  "properties": {},
  "title": "get_revenue_analyticsArguments"
}
```
No parameters.

**Output:**
```json
{
  "success": true,
  "daily": [
    {
      "date": "2026-04-11",
      "revenue": 255.56000000000003,
      "cost": 80.0,
      "profit": 175.56000000000003,
      "sales": 44
    },
    {
      "date": "2026-04-16",
      "revenue": 105.92,
      "cost": 83.92,
      "profit": 22.0,
      "sales": 8
    },
    {
      "date": "2026-06-27",
      "revenue": 5.99,
      "cost": 2.0,
      "profit": 3.99,
      "sales": 1
    }
  ],
  "summary": {
    "total_revenue": 367.47,
    "total_cost": 165.92,
    "total_profit": 201.55,
    "profit_margin": 54.8
  }
}
```
