import type {
  Product,
  RevenueAnalytics,
  TransactionPayload,
  TransactionResponse,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // no JSON body to read the error detail from
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!res.ok) {
    throw new ApiError(res.status, "Invalid email or password");
  }

  const data = await res.json();
  return data.access_token as string;
}

export async function register(
  email: string,
  password: string,
  fullName: string
): Promise<void> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // no JSON body
    }
    throw new ApiError(res.status, detail);
  }
}

export function getProducts(token: string): Promise<Product[]> {
  return request<Product[]>("/products/", token);
}

export function getLowStock(token: string): Promise<Product[]> {
  return request<Product[]>("/alerts/low-stock", token);
}

export function getRevenueAnalytics(token: string): Promise<RevenueAnalytics> {
  return request<RevenueAnalytics>("/alerts/analytics/revenue", token);
}

export function recordTransaction(
  token: string,
  payload: TransactionPayload
): Promise<TransactionResponse> {
  return request<TransactionResponse>("/transactions/", token, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
