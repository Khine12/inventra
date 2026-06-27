import type { Product } from "../types";

export function ProductList({ products }: { products: Product[] }) {
  return (
    <section className="card">
      <h2>Products</h2>
      {products.length === 0 ? (
        <p className="muted">No products yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>Quantity</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.sku}</td>
                <td>{p.quantity}</td>
                <td>${p.price.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
