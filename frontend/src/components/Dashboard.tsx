import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getLowStock, getProducts, getRevenueAnalytics } from "../api";
import type { Product, RevenueAnalytics } from "../types";
import { ProductList } from "./ProductList";
import { LowStockPanel } from "./LowStockPanel";
import { TransactionForm } from "./TransactionForm";
import { RevenueChart } from "./RevenueChart";

export function Dashboard() {
  const { token, logout } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [lowStock, setLowStock] = useState<Product[]>([]);
  const [analytics, setAnalytics] = useState<RevenueAnalytics | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!token) return;
    try {
      const [productsResult, lowStockResult, analyticsResult] = await Promise.all([
        getProducts(token),
        getLowStock(token),
        getRevenueAnalytics(token),
      ]);
      setProducts(productsResult);
      setLowStock(lowStockResult);
      setAnalytics(analyticsResult);
      setLoadError(null);
    } catch {
      setLoadError("Failed to load dashboard data.");
    }
  }, [token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Inventra</h1>
        <button onClick={logout}>Log out</button>
      </header>
      {loadError && <p className="error">{loadError}</p>}
      <div className="dashboard-grid">
        <ProductList products={products} />
        <LowStockPanel products={lowStock} />
        <TransactionForm products={products} onRecorded={refresh} />
        {analytics && <RevenueChart analytics={analytics} />}
      </div>
    </div>
  );
}
