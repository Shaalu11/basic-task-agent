import React from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import Home from "./pages/Home";
import CalendarPage from "./pages/CalendarPage";
import Chat from "./pages/Chat";
import Events from "./pages/Events";
import { logout, validateSession } from "./api";
import "./App.css";

// Create context for login state
export const LoginContext = React.createContext();

function Navbar({ isLoggedIn, email }) {
  const navigate = useNavigate();
  const [dark, setDark] = React.useState(false);

  React.useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.body.classList.add("dark");
      setDark(true);
    }
  }, []);

  const toggleTheme = () => {
    if (dark) {
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
    }
    setDark(!dark);
  };

  const handleLogout = async () => {
    try {
      if (email) {
        await logout(email);
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
    localStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="navbar">
      <span className="home-icon" onClick={() => navigate("/")}>🏠</span>
      <span className="nav-title">AI Task Scheduler</span>

      <div className="nav-right">
        <span className="theme-toggle" onClick={toggleTheme}>
          {dark ? "☀️" : "🌙"}
        </span>
        {isLoggedIn && (
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        )}
      </div>
    </div>
  );
}

function Layout({ isLoggedIn, email, setIsLoggedIn }) {
  return (
    <>
      <Navbar isLoggedIn={isLoggedIn} email={email} />
      <div className="page-content">
        <Routes>
          <Route path="/" element={<Home setIsLoggedIn={setIsLoggedIn} />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/events" element={<Events />} />
          <Route path="/calendar" element={<CalendarPage />} />
        </Routes>
      </div>
    </>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false);
  const [email, setEmail] = React.useState("");

  React.useEffect(() => {
    const checkSession = async () => {
      const savedEmail = localStorage.getItem("email");
      const loggedIn = localStorage.getItem("logged_in");

      if (savedEmail && loggedIn) {
        const result = await validateSession(savedEmail);
        if (result.valid) {
          setIsLoggedIn(true);
          setEmail(savedEmail);
        } else {
          localStorage.clear();
          setIsLoggedIn(false);
          setEmail("");
        }
      }
    };

    checkSession();
  }, []);

  return (
    <Router>
      <LoginContext.Provider value={{ isLoggedIn, email, setIsLoggedIn, setEmail }}>
        <Layout isLoggedIn={isLoggedIn} email={email} setIsLoggedIn={setIsLoggedIn} />
      </LoginContext.Provider>
    </Router>
  );
}

export default App;