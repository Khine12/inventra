export interface Product {
  id: number;
  name: string;
  sku: string;
  quantity: number;
  cost_price: number;
  price: number;
  low_stock_threshold: number;
  expiry_date: string | null;
  created_at: string;
}

export type TransactionType = "sale" | "restock";

export interface TransactionPayload {
  product_id: number;
  type: TransactionType;
  quantity: number;
  note?: string;
}

export interface TransactionResponse {
  id: number;
  product_id: number;
  type: TransactionType;
  quantity: number;
  note: string | null;
  created_at: string;
}

export interface RevenueDaily {
  date: string;
  revenue: number;
  cost: number;
  profit: number;
  sales: number;
}

export interface RevenueSummary {
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  profit_margin: number;
}

export interface RevenueAnalytics {
  daily: RevenueDaily[];
  summary: RevenueSummary;
}
