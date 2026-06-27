import { useAuth } from "./context/AuthContext";
import { Login } from "./components/Login";
import { Dashboard } from "./components/Dashboard";

export function App() {
  const { token } = useAuth();
  return token ? <Dashboard /> : <Login />;
}
