import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { Menu, Plane } from "lucide-react";

import { getSessions } from "./api/client";
import Sidebar from "./components/Sidebar";
import HomePage from "./pages/HomePage";
import PastTripsPage from "./pages/PastTripsPage";
import PlannerPage from "./pages/PlannerPage";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import LandingPage from "./pages/LandingPage";
import ComparePage from "./pages/ComparePage";

function AppShell() {
  const location = useLocation();
  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    refreshSessions();
  }, []);

  async function refreshSessions() {
    try {
      setSessions(await getSessions());
    } catch {
      setSessions([]);
    }
  }

  const isLandingPage = location.pathname === "/";
  const isAuthPage = location.pathname === "/login" || location.pathname === "/signup";
  const hideSidebar = isAuthPage || isLandingPage;

  return (
    <div className={`app-shell ${hideSidebar ? 'no-sidebar' : ''}`}>
      {!hideSidebar && (
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
      )}

      <main className="main-panel">
        {!hideSidebar && (
          <header className="topbar">
            <button
              className="icon-button mobile-only"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={21} />
            </button>
            <div className="brand-mark">
              <Plane size={22} />
            </div>
            <div>
              <h1>Fleet Trip Planner</h1>
              <p>Chat with the bot or generate an itinerary directly</p>
            </div>
          </header>
        )}

        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route
            path="/home"
            element={
              <ProtectedRoute>
                <div className="home-page-wrap">
                  <HomePage />
                </div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/plan"
            element={
              <ProtectedRoute>
                <PlannerPage onSessionsChanged={refreshSessions} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/plan/:sessionId"
            element={
              <ProtectedRoute>
                <PlannerPage onSessionsChanged={refreshSessions} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trips"
            element={
              <ProtectedRoute>
                <PastTripsPage sessions={sessions} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/compare"
            element={
              <ProtectedRoute>
                <ComparePage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
