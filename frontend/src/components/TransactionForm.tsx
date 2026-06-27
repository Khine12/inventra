import { useState, type FormEvent } from "react";
import type { Product, TransactionType } from "../types";
import { ApiError, recordTransaction } from "../api";
import { useAuth } from "../context/AuthContext";

interface Props {
  products: Product[];
  onRecorded: () => void;
}

export function TransactionForm({ products, onRecorded }: Props) {
  const { token } = useAuth();
  const [productId, setProductId] = useState<number | "">("");
  const [type, setType] = useState<TransactionType>("sale");
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || productId === "") return;
    setError(null);
    setSubmitting(true);
    try {
      await recordTransaction(token, {
        product_id: productId,
        type,
        quantity,
        note: note || undefined,
      });
      setQuantity(1);
      setNote("");
      onRecorded();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not record transaction.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="card">
      <h2>Record Transaction</h2>
      <form className="transaction-form" onSubmit={handleSubmit}>
        <label>
          Product
          <select
            value={productId}
            onChange={(e) =>
              setProductId(e.target.value ? Number(e.target.value) : "")
            }
            required
          >
            <option value="" disabled>
              Select a product
            </option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.sku}) — {p.quantity} in stock
              </option>
            ))}
          </select>
        </label>
        <label>
          Type
          <select
            value={type}
            onChange={(e) => setType(e.target.value as TransactionType)}
          >
            <option value="sale">Sale</option>
            <option value="restock">Restock</option>
          </select>
        </label>
        <label>
          Quantity
          <input
            type="number"
            min={1}
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Note
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="optional"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Recording..." : "Record"}
        </button>
      </form>
    </section>
  );
}
