import { useState } from "react";
import { api } from "./api";

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    role: "customer",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const isRegistering = mode === "register";

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const result = isRegistering
        ? await api.register(form)
        : await api.login({ email: form.email, password: form.password });
      onAuthenticated(result.user);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-decoration decoration-one" />
      <div className="auth-decoration decoration-two" />
      <section className="auth-card">
        <div className="auth-brand">
          <div className="brand-mark">S</div>
          <div>
            <strong>SweetStock</strong>
            <span>Bakery operations</span>
          </div>
        </div>
        <div className="auth-heading">
          <div className="eyebrow">{isRegistering ? "Join the bakery" : "Welcome back"}</div>
          <h1>{isRegistering ? "Create your account." : "Sign in to your workspace."}</h1>
          <p>
            {isRegistering
              ? "Create a customer or employee account to test the bakery workflow."
              : "Manage orders, products, and inventory in one place."}
          </p>
        </div>
        <div className="auth-tabs">
          <button className={mode === "login" ? "selected" : ""} onClick={() => { setMode("login"); setError(""); }}>Sign in</button>
          <button className={mode === "register" ? "selected" : ""} onClick={() => { setMode("register"); setError(""); }}>Create account</button>
        </div>
        {error && <div className="alert error">{error}</div>}
        <form className="auth-form" onSubmit={submit}>
          {isRegistering && (
            <>
              <label>Full name<input name="name" value={form.name} onChange={updateField} placeholder="Jordan Lee" autoComplete="name" /></label>
              <div className="form-row">
                <label>Email<input name="email" type="email" value={form.email} onChange={updateField} placeholder="you@example.com" autoComplete="email" /></label>
                <label>Phone<input name="phone" value={form.phone} onChange={updateField} placeholder="555-123-4567" autoComplete="tel" /></label>
              </div>
            </>
          )}
          {!isRegistering && <label>Email<input name="email" type="email" value={form.email} onChange={updateField} placeholder="you@example.com" autoComplete="email" /></label>}
          <label>Password<input name="password" type="password" value={form.password} onChange={updateField} placeholder="At least 6 characters" autoComplete={isRegistering ? "new-password" : "current-password"} /></label>
          {isRegistering && (
            <label>Account type
              <select name="role" value={form.role} onChange={updateField}>
                <option value="customer">Customer</option>
                <option value="employee">Employee</option>
              </select>
            </label>
          )}
          <button className="primary-button auth-submit" disabled={saving}>{saving ? "Please wait…" : isRegistering ? "Create account" : "Sign in"}</button>
        </form>
        <p className="auth-note">For local testing only. Use separate emails to create multiple accounts.</p>
      </section>
    </main>
  );
}

export default AuthScreen;
