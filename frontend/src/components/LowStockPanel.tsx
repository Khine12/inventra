import type { Product } from "../types";

export function LowStockPanel({ products }: { products: Product[] }) {
  return (
    <section className="card">
      <h2>Low Stock</h2>
      {products.length === 0 ? (
        <p className="muted">No products at risk.</p>
      ) : (
        <ul className="low-stock-list">
          {products.map((p) => (
            <li key={p.id} className="low-stock-item">
              <span>{p.name}</span>
              <span className="badge badge-warning">
                {p.quantity} / {p.low_stock_threshold}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
