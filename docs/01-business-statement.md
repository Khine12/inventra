# Business Statement — Inventra (Agent-Operable Edition)

## The problem

Small and independent retailers run their stock and sales on a mix of spreadsheets,
memory, and reactive guesswork. Three failures recur:

1. **Overselling.** Stock is sold past what's physically on hand because nothing
   enforces a hard limit at the moment of sale.
2. **Blind reordering.** Low-stock situations are noticed too late — usually when a
   product runs out — because no one is watching thresholds continuously.
3. **No profit visibility.** Owners see revenue but rarely cost or margin, so they
   can't tell which products actually make money.

These are operational, not strategic, problems: they happen in the daily flow of
recording sales and checking stock, where the owner has the least time and attention.

## The solution

**Inventra** is a full-stack inventory and sales platform that makes the daily flow
safe and visible: every sale is validated against real on-hand quantity (a server-side
guard refuses oversells), stock deducts automatically, low-stock items surface against
per-product thresholds, and an analytics layer aggregates revenue, cost, profit, and
margin over time.

The distinguishing piece — and the focus of this submission — is that Inventra is
**operable two ways from the same core logic**:

- **By a human**, through a conventional web UI and REST API.
- **By an AI agent**, through a Model Context Protocol (MCP) server that exposes the
  same business operations as agent-callable tools.

A shop owner can either click through a dashboard, or simply tell an assistant *"we
sold five units of SKU-203 today — log it and flag anything running low,"* and the
agent records the sale, respects the same oversell guard, and reports back. The
identical service layer backs both front doors, so the safety rules and business logic
can never drift between the human path and the agent path.

## Business value

- **Prevents revenue/inventory errors at the source.** The negative-stock guard makes
  overselling structurally impossible, not just discouraged — and it holds identically
  whether a human or an agent initiates the sale.
- **Turns inventory management from a screen task into a conversation.** The agentic
  layer collapses multi-click operations (look up stock → record sale → re-check
  thresholds) into a single natural-language request, lowering the operational tax on
  the owner.
- **Surfaces margin, not just revenue.** The analytics layer makes per-day profit and
  margin visible, supporting pricing and reorder decisions that revenue figures alone
  hide.
- **Demonstrates a reusable pattern.** The architecture — a clean service layer fronted
  by *both* a REST API and an MCP server — is a general recipe for making any existing
  business application agent-operable without rewriting its core.

## Scope of this submission

This packet documents Inventra's core domain (authentication, products, transactions,
and alerts/analytics) and its MCP integration in full, precise enough to be regenerated
from the documentation alone. The accompanying Logical Structure Document and Technical
Implementation Guide specify the data model, the shared service layer, the REST API,
and the six MCP tools and their input/output contracts.