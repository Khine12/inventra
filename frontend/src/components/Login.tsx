import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { register as apiRegister, ApiError } from "../api";

type Mode = "login" | "register";

export function Login() {
  const { login } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "register") {
        await apiRegister(email, password, fullName);
      }
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : `${mode === "register" ? "Registration" : "Login"} failed.`);
    } finally {
      setSubmitting(false);
    }
  }

  function switchMode() {
    setMode((m) => (m === "login" ? "register" : "login"));
    setError(null);
    setFullName("");
  }

  return (
    <div className="login-screen">
      <form className="card login-form" onSubmit={handleSubmit}>
        <h1>Inventra</h1>
        {mode === "register" && (
          <label>
            Full Name
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </label>
        )}
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting
            ? mode === "register" ? "Creating account..." : "Signing in..."
            : mode === "register" ? "Create account" : "Sign in"}
        </button>
        <button type="button" onClick={switchMode} style={{ marginTop: "0.5rem", background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>
          {mode === "login" ? "Don't have an account? Register" : "Already have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}
