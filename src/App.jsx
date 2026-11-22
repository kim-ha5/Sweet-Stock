import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import AuthScreen from "./AuthScreen";

const STATUSES = ["Pending", "In Progress", "Ready", "Completed", "Cancelled"];

function money(value) {
  return Number(value || 0).toLocaleString("en-US", { style: "currency", currency: "USD" });
}

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    api.me()
      .then((result) => setUser(result.user))
      .catch(() => setUser(null))
      .finally(() => setAuthLoading(false));
  }, []);

  if (authLoading) return <main className="auth-page"><p>Loading your SweetStock session…</p></main>;
  if (!user) {
    return <AuthScreen onAuthenticated={(authenticatedUser) => {
      setUser(authenticatedUser);
    }} />;
  }

  function signOut() {
    api.logout().catch(() => {}).finally(() => {
      setUser(null);
    });
  }

  return user.role === "customer"
    ? <CustomerApp user={user} onSignOut={signOut} />
    : <StaffApp user={user} onSignOut={signOut} />;
}

function CustomerApp({ user, onSignOut }) {
  const [page, setPage] = useState("shop");
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState({ order_count: 0, sales_total: 0 });

  async function loadCustomerData() {
    try {
      setError("");
      const [productResult, orderResult, summaryResult] = await Promise.all([api.products(search), api.orders(), api.customerSummary()]);
      setProducts(productResult.products);
      setOrders(orderResult.orders);
      setSummary(summaryResult.summary);
    } catch (requestError) { setError(requestError.message); }
  }

  useEffect(() => { loadCustomerData(); }, [search]);

  const cartTotal = cart.reduce((total, item) => total + item.price * item.quantity, 0);
  const cartCount = cart.reduce((total, item) => total + item.quantity, 0);

  function addToCart(product) {
    setCart((items) => {
      const existing = items.find((item) => item.product_id === product.product_id);
      if (existing) return items.map((item) => item.product_id === product.product_id ? { ...item, quantity: item.quantity + 1 } : item);
      return [...items, { ...product, quantity: 1 }];
    });
    setMessage(`${product.name} added to your order.`);
  }

  async function checkout() {
    try {
      await api.createOrder({
        customer: { name: user.name, email: user.email },
        items: cart.map((item) => ({ product_id: item.product_id, quantity: item.quantity })),
      });
      setCart([]);
      setPage("orders");
      setMessage("Your order was placed successfully.");
      await loadCustomerData();
    } catch (requestError) { setError(requestError.message); }
  }

  return (
    <CustomerShell user={user} page={page} setPage={setPage} cartCount={cartCount} onSignOut={onSignOut}>
      {error && <Alert message={error} onRetry={loadCustomerData} />}
      {message && <div className="alert success">{message}</div>}
      {page === "shop" && <CustomerShop products={products} search={search} setSearch={setSearch} onAdd={addToCart} />}
      {page === "orders" && <CustomerOrders orders={orders} onOpenOrder={async (id) => setSelectedOrder((await api.order(id)).order)} />}
      {page === "account" && <CustomerAccount user={user} summary={summary} />}
      {page === "cart" && <CartPage cart={cart} setCart={setCart} total={cartTotal} onCheckout={checkout} />}
      {selectedOrder && <OrderDetails order={selectedOrder} onClose={() => setSelectedOrder(null)} />}
    </CustomerShell>
  );
}

function CustomerShell({ user, page, setPage, cartCount, onSignOut, children }) {
  const nav = [["shop", "Shop"], ["orders", "My orders"], ["account", "My account"]];
  return (
    <div className="app-shell customer-shell">
      <aside className="sidebar">
        <Brand subtitle="Customer bakery" />
        <nav className="nav-list" aria-label="Customer navigation">
          {nav.map(([id, label]) => <NavButton key={id} active={page === id} onClick={() => setPage(id)} label={label} />)}
        </nav>
        <div className="sidebar-footer"><div className="avatar">{initials(user.name)}</div><div><strong>{user.name}</strong><span>Customer</span></div><button className="logout-button" onClick={onSignOut}>Log out</button></div>
      </aside>
      <main className="main-content">
        <header className="topbar"><span className="breadcrumb">SweetStock / {page === "shop" ? "Shop" : page}</span><button className="cart-button" onClick={() => setPage("cart")}>Cart <b>{cartCount}</b></button></header>
        <section className="page-content">{children}</section>
      </main>
    </div>
  );
}

function CustomerShop({ products, search, setSearch, onAdd }) {
  return <>
    <PageHeader eyebrow="Fresh from our kitchen" title="What are you craving?" description="Browse today's bakes and build your order." />
    <div className="toolbar"><div className="search-box">Search <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Find a treat..." /></div></div>
    <div className="product-grid customer-products">{products.map((product, index) => <article className="product-card" key={product.product_id}><div className={`product-art art-${index % 5}`}>{["✦", "◌", "●", "◆", "✧"][index % 5]}</div><div className="product-card-body"><div className="product-title"><h3>{product.name}</h3><strong>{money(product.price)}</strong></div><p>{product.description}</p><button className="primary-button add-button" onClick={() => onAdd(product)}>Add to order</button></div></article>)}</div>
    {!products.length && <EmptyState text="No products match your search." />}
  </>;
}

function CustomerOrders({ orders, onOpenOrder }) {
  return <><PageHeader eyebrow="Your history" title="My orders" description="Follow your orders and revisit your bakery history." /><OrdersTable orders={orders} customerView onOpenOrder={onOpenOrder} /></>;
}

function CustomerAccount({ user, summary }) {
  return <><PageHeader eyebrow="Your profile" title="My account" description="Your SweetStock customer details and order summary." /><div className="account-grid"><section className="panel account-card"><div className="large-avatar">{initials(user.name)}</div><h2>{user.name}</h2><p>{user.email}</p><p>{user.phone}</p><span className="role-pill">Customer account</span></section><section className="panel account-card"><div className="eyebrow">Order history</div><strong className="account-number">{summary.order_count}</strong><p>orders placed</p><div className="account-divider" /><div className="eyebrow">Total spent</div><strong className="account-total">{money(summary.sales_total)}</strong></section></div></>;
}

function CartPage({ cart, setCart, total, onCheckout }) {
  return <><PageHeader eyebrow="Ready when you are" title="Your cart" description="Review your order before sending it to the bakery." action={<button className="primary-button" disabled={!cart.length} onClick={onCheckout}>Place order</button>} />{cart.length ? <section className="panel cart-panel">{cart.map((item) => <div className="cart-row" key={item.product_id}><div className="mini-product-art">✦</div><div><strong>{item.name}</strong><span>{money(item.price)} each</span></div><div className="quantity-controls"><button onClick={() => setCart((items) => items.map((entry) => entry.product_id === item.product_id ? { ...entry, quantity: Math.max(1, entry.quantity - 1) } : entry))}>−</button><b>{item.quantity}</b><button onClick={() => setCart((items) => items.map((entry) => entry.product_id === item.product_id ? { ...entry, quantity: entry.quantity + 1 } : entry))}>＋</button></div><strong>{money(item.price * item.quantity)}</strong></div>)}<div className="cart-total"><span>Total</span><strong>{money(total)}</strong></div></section> : <EmptyState text="Your cart is empty. Browse the shop to get started." />}</>;
}

function StaffApp({ user, onSignOut }) {
  const [section, setSection] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [users, setUsers] = useState([]);
  const [summary, setSummary] = useState([]);
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [selectedOrder, setSelectedOrder] = useState(null);

  async function loadStaffData() {
    try {
      setError("");
      const [orderResult, productResult, ingredientResult, recipeResult, userResult, summaryResult] = await Promise.all([
        api.orders(status, search), api.products(search), api.ingredients(), api.recipes(), api.users(), api.salesSummary(),
      ]);
      setOrders(orderResult.orders); setProducts(productResult.products); setIngredients(ingredientResult.ingredients); setRecipes(recipeResult.recipes); setUsers(userResult.users); setSummary(summaryResult.summary);
    } catch (requestError) { setError(requestError.message); }
  }
  useEffect(() => { loadStaffData(); }, [status, search]);

  async function updateOrder(id, nextStatus) { try { await api.updateOrder(id, nextStatus); setMessage(`Order #${id} updated.`); loadStaffData(); } catch (requestError) { setError(requestError.message); } }
  async function restock(id, amount) { try { await api.restock(id, amount); setMessage("Inventory updated."); loadStaffData(); } catch (requestError) { setError(requestError.message); } }

  const nav = [["orders", "All orders"], ["products", "Products"], ["inventory", "Inventory"], ["recipes", "Recipes"], ["users", "Accounts"], ["reports", "Reports"]];
  return <div className="app-shell"><aside className="sidebar"><Brand subtitle={`${user.role === "admin" ? "Admin" : "Employee"} operations`} /><nav className="nav-list"><span className="nav-caption">Operations</span>{nav.map(([id, label]) => <NavButton key={id} active={section === id} onClick={() => setSection(id)} label={label} />)}</nav><div className="sidebar-footer"><div className="avatar">{initials(user.name)}</div><div><strong>{user.name}</strong><span>{user.role}</span></div><button className="logout-button" onClick={onSignOut}>Log out</button></div></aside><main className="main-content"><header className="topbar"><span className="breadcrumb">SweetStock / Operations / {section}</span><span className="status-indicator"><i /> Live database</span></header><section className="page-content">{error && <Alert message={error} onRetry={loadStaffData} />}{message && <div className="alert success">{message}</div>}{section === "orders" && <StaffOrders orders={orders} status={status} setStatus={setStatus} search={search} setSearch={setSearch} onStatus={updateOrder} onOpenOrder={async (id) => setSelectedOrder((await api.order(id)).order)} />}{section === "products" && <StaffProducts products={products} search={search} setSearch={setSearch} isAdmin={user.role === "admin"} onPrice={async (id, price) => { await api.updateProduct(id, price); setMessage("Product price updated."); loadStaffData(); }} />}{section === "inventory" && <StaffInventory ingredients={ingredients} onRestock={restock} />}{section === "recipes" && <Recipes recipes={recipes} />}{section === "users" && <Users users={users} />}{section === "reports" && <StaffReports summary={summary} />}</section></main>{selectedOrder && <OrderDetails order={selectedOrder} onClose={() => setSelectedOrder(null)} />}</div>;
}

function StaffOrders({ orders, status, setStatus, search, setSearch, onStatus, onOpenOrder }) { return <><PageHeader eyebrow="Operations" title="All orders" description="Monitor, assign, and move every order through the bakery." /><Toolbar search={search} setSearch={setSearch} placeholder="Customer or order number..." select={<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{STATUSES.map((item) => <option key={item}>{item}</option>)}</select>} /><OrdersTable orders={orders} onStatus={onStatus} onOpenOrder={onOpenOrder} /></>; }
function StaffProducts({ products, search, setSearch, isAdmin, onPrice }) { return <><PageHeader eyebrow="Catalog" title="Products" description="Everything your bakery offers, with live prices from the database." /><Toolbar search={search} setSearch={setSearch} placeholder="Search products..." /><ProductsTable products={products} isAdmin={isAdmin} onPrice={onPrice} /></>; }
function StaffInventory({ ingredients, onRestock }) { return <><PageHeader eyebrow="Stock control" title="Inventory" description="Restock ingredients and keep production moving." /><InventoryTable ingredients={ingredients} onRestock={onRestock} /></>; }
function Recipes({ recipes }) { return <><PageHeader eyebrow="Production" title="Recipes" description="Ingredient requirements for every product in the catalog." /><div className="recipe-grid">{recipes.map((recipe) => <section className="panel recipe-card" key={recipe.recipe_id}><h2>{recipe.product_name}</h2><p>Recipe #{recipe.recipe_id}</p><ul>{recipe.ingredients.map((item) => <li key={item.ingredient_id}><span>{item.name}</span><strong>{item.amount} {item.measure_unit}</strong></li>)}</ul></section>)}</div></>; }
function Users({ users }) { return <><PageHeader eyebrow="People" title="Accounts" description="Customer, employee, and admin accounts in the system." /><section className="panel"><div className="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Role</th></tr></thead><tbody>{users.map((item) => <tr key={item.user_id}><td><strong>{item.name}</strong></td><td>{item.email}</td><td>{item.phone}</td><td><span className="role-pill">{item.role}</span></td></tr>)}</tbody></table></div></section></>; }
function StaffReports({ summary }) { return <><PageHeader eyebrow="Business intelligence" title="Reports" description="The numbers behind today's bakery decisions." /><div className="report-grid"><ReportCard title="Total sales" value={money(summary.totals.sales_total)} /><ReportCard title="Open orders" value={summary.totals.open_orders} /><ReportCard title="Inventory items" value={summary.totals.inventory_count} /><ReportCard title="Completed orders" value={summary.totals.completed_orders} /></div><Report summary={summary.rows} /></>; }

function Brand({ subtitle }) { return <div className="brand"><div className="brand-mark">S</div><div><strong>SweetStock</strong><span>{subtitle}</span></div></div>; }
function NavButton({ active, onClick, label }) { return <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}>{label}</button>; }
function initials(name = "") { return name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase(); }
function Alert({ message, onRetry }) { return <div className="alert error">{message}<button onClick={onRetry}>Try again</button></div>; }
function PageHeader({ eyebrow, title, description, action }) { return <div className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>; }
function Toolbar({ search, setSearch, placeholder, select }) { return <div className="toolbar"><div className="search-box">Search <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={placeholder} /></div>{select}</div>; }
function OrdersTable({ orders, onStatus, onOpenOrder, customerView = false }) { if (!orders.length) return <EmptyState text={customerView ? "You have not placed any orders yet." : "No matching orders."} />; return <section className="panel"><div className="table-wrap"><table><thead><tr><th>Order</th><th>Customer</th><th>Date</th><th>Total</th><th>Status</th></tr></thead><tbody>{orders.map((order) => <tr className="clickable-row" key={order.order_id} onClick={() => onOpenOrder?.(order.order_id)}><td>#{order.order_id}</td><td>{order.customer_name}</td><td>{order.order_date}</td><td>{money(order.total)}</td><td>{onStatus ? <select onClick={(event) => event.stopPropagation()} value={order.status} onChange={(event) => onStatus(order.order_id, event.target.value)}>{STATUSES.map((item) => <option key={item}>{item}</option>)}</select> : <span className={`status-badge ${order.status.toLowerCase().replaceAll(" ", "-")}`}>{order.status}</span>}</td></tr>)}</tbody></table></div><p className="table-hint">Click an order to view its details and itemized total.</p></section>; }
function ProductsTable({ products, isAdmin = false, onPrice }) { return <section className="panel"><div className="table-wrap"><table><thead><tr><th>Product</th><th>Description</th><th>Price</th></tr></thead><tbody>{products.map((product) => <ProductRow key={product.product_id} product={product} isAdmin={isAdmin} onPrice={onPrice} />)}</tbody></table></div></section>; }
function ProductRow({ product, isAdmin, onPrice }) { const [price, setPrice] = useState(product.price); return <tr><td><strong>{product.name}</strong></td><td>{product.description}</td><td>{isAdmin ? <form className="price-form" onSubmit={(event) => { event.preventDefault(); const value = Number(price); if (value >= 0) onPrice(product.product_id, value); }}><span>$</span><input type="number" min="0" step="0.01" value={price} onChange={(event) => setPrice(event.target.value)} /><button className="secondary-button">Save</button></form> : money(product.price)}</td></tr>; }
function OrderDetails({ order, onClose }) { return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><section className="modal order-details"><div className="modal-header"><div><div className="eyebrow">Order #{order.order_id}</div><h2>Order details</h2></div><button className="close-button" onClick={onClose}>×</button></div><div className="order-detail-meta"><span><strong>Customer</strong>{order.customer_name}<small>{order.customer_email}</small></span><span><strong>Date</strong>{order.order_date}</span><StatusBadge status={order.status} /></div><div className="detail-items">{order.items.map((item) => <div className="detail-item" key={item.item_id}><span><strong>{item.name}</strong><small>{item.quantity} × {money(item.unit_price)}</small></span><strong>{money(item.total)}</strong></div>)}</div><div className="detail-total"><span>Total</span><strong>{money(order.total)}</strong></div></section></div>; }
function StatusBadge({ status }) { return <span className={`status-badge ${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span>; }
function InventoryTable({ ingredients, onRestock }) { return <section className="panel"><div className="table-wrap"><table><thead><tr><th>Ingredient</th><th>On hand</th><th>Unit</th><th>Last ordered</th><th>Restock</th></tr></thead><tbody>{ingredients.map((item) => <RestockRow item={item} onRestock={onRestock} key={item.ingredient_id} />)}</tbody></table></div></section>; }
function RestockRow({ item, onRestock }) { const [amount, setAmount] = useState(""); return <tr><td><strong>{item.name}</strong></td><td>{item.stock_amt}</td><td>{item.measure_unit}</td><td>{item.last_order_date || "—"}</td><td><form className="inline-form" onSubmit={(event) => { event.preventDefault(); if (Number(amount) > 0) { onRestock(item.ingredient_id, Number(amount)); setAmount(""); } }}><input type="number" min="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="Amount" required /><button className="secondary-button">Add</button></form></td></tr>; }
function Report({ summary }) { return <div className="report-grid">{summary.map((row) => <ReportCard key={row.status} title={row.status} value={`${row.order_count} orders · ${money(row.sales_total)}`} />)}</div>; }
function ReportCard({ title, value }) { return <section className="report-card"><div className="report-heading"><span>{title}</span><strong>{value}</strong></div></section>; }
function EmptyState({ text }) { return <div className="empty-state"><strong>{text}</strong></div>; }

export default App;
