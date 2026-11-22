async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || "Something went wrong while contacting the server.");
  }
  return body;
}

export const api = {
  health: () => request("/api/health"),
  me: () => request("/api/auth/me"),
  login: (payload) =>
    request("/api/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  register: (payload) =>
    request("/api/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  logout: () => request("/api/auth/logout", { method: "POST" }),
  users: () => request("/api/users"),
  products: (search = "") =>
    request(`/api/products?search=${encodeURIComponent(search)}`),
  updateProduct: (id, price) =>
    request(`/api/products/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ price }),
    }),
  ingredients: () => request("/api/ingredients"),
  recipes: () => request("/api/recipes"),
  orders: (status = "", search = "") =>
    request(`/api/orders?status=${encodeURIComponent(status)}&search=${encodeURIComponent(search)}`),
  order: (id) => request(`/api/orders/${id}`),
  createOrder: (payload) =>
    request("/api/orders", { method: "POST", body: JSON.stringify(payload) }),
  updateOrder: (id, status) =>
    request(`/api/orders/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
  restock: (id, amount) =>
    request(`/api/ingredients/${id}/stock`, {
      method: "PATCH",
      body: JSON.stringify({ amount }),
    }),
  incompleteOrders: () => request("/api/reports/incomplete-orders"),
  unassignedOrders: () => request("/api/reports/unassigned-orders"),
  unorderedProducts: () => request("/api/reports/unordered-products"),
  lowStock: () => request("/api/reports/low-stock"),
  salesSummary: () => request("/api/reports/sales-summary"),
  customerSummary: () => request("/api/reports/customer-summary"),
};
