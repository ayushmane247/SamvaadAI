import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";
import DashboardLayout from "./layouts/DashboardLayout";
import Chat from "./pages/dashboard/Chat";
import Results from "./pages/dashboard/Results";
import SchemeDetail from "./pages/dashboard/SchemeDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import { useEffect } from "react";
import useUIStore from "./store/useUIStore";
import Home from "./pages/dashboard/Home";
import Profile from "./pages/dashboard/Profile";

function App() {
  const theme = useUIStore((state) => state.theme);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
  }, [theme]);
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<Auth />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            {/* Default route */}
            <Route index element={<Home />} />
            <Route path="home" element={<Home />} />
            <Route path="conversation" element={<Chat />} />
            <Route path="chat" element={<Chat />} />
            <Route path="results" element={<Results />} />
            <Route path="scheme/:id" element={<SchemeDetail />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Route>

        {/* Fallback Route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
