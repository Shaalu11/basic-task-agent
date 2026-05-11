import React, { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { login, validateSession } from "../api";
import { LoginContext } from "../App";

function Home({ setIsLoggedIn }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const { setEmail: setContextEmail } = useContext(LoginContext);

  useEffect(() => {
    const checkSession = async () => {
      const params = new URLSearchParams(window.location.search);
      const userEmail = params.get("email");

      if (userEmail) {
        localStorage.setItem("email", userEmail);
        localStorage.setItem("logged_in", "true");
        setEmail(userEmail);
        setIsLoggedIn(true);
        setContextEmail(userEmail);
        // Remove email from URL
        window.history.replaceState({}, document.title, "/");
        setLoading(false);
      } else {
        const savedEmail = localStorage.getItem("email");
        const loggedIn = localStorage.getItem("logged_in");

        if (savedEmail && loggedIn) {
          const result = await validateSession(savedEmail);
          if (result.valid) {
            setEmail(savedEmail);
            setIsLoggedIn(true);
            setContextEmail(savedEmail);
          } else {
            localStorage.clear();
            setIsLoggedIn(false);
            setEmail("");
          }
        } else {
          setEmail("");
          setIsLoggedIn(false);
        }
        setLoading(false);
      }
    };

    checkSession();
  }, [setIsLoggedIn, setContextEmail]);

  if (loading) {
    return (
      <div className="home-page">
        <h1 className="main-title">AI Task Scheduler</h1>
        <p className="subtitle">Loading...</p>
      </div>
    );
  }

  return (
    <div className="home-page">
      <h1 className="main-title">AI Task Scheduler</h1>
      <p className="subtitle">
        Smart task scheduling using AI + Google Calendar
      </p>

      {!email ? (
        <button className="login-btn" onClick={login}>
          Login with Google
        </button>
      ) : (
        <div className="home-buttons">
          <div className="card" onClick={() => navigate("/chat")}>
            <h2>Chat with AI</h2>
            <p>Tell AI to schedule tasks</p>
          </div>

          <div className="card" onClick={() => navigate("/events")}>
            <h2>View Events</h2>
            <p>See and delete your events</p>
          </div>

          <div className="card" onClick={() => navigate("/calendar")}>
            <h2>Calendar</h2>
            <p>View events in calendar</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;