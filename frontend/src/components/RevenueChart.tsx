import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RevenueAnalytics } from "../types";

export function RevenueChart({ analytics }: { analytics: RevenueAnalytics }) {
  const { daily, summary } = analytics;

  return (
    <section className="card">
      <h2>Revenue</h2>
      <div className="summary-grid">
        <div className="summary-item">
          <span className="label">Revenue</span>
          <span className="value">${summary.total_revenue.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Cost</span>
          <span className="value">${summary.total_cost.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Profit</span>
          <span className="value">${summary.total_profit.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Margin</span>
          <span className="value">{summary.profit_margin}%</span>
        </div>
      </div>
      {daily.length === 0 ? (
        <p className="muted">No sales recorded yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={daily}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="revenue" stroke="#2563eb" />
            <Line type="monotone" dataKey="profit" stroke="#16a34a" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
