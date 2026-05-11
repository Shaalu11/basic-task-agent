import React, { useState, useEffect } from "react";
import { addTask, getEvents, deleteEventById } from "../api";

function Chat() {
  const [email, setEmail] = useState("");
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);
  const [events, setEvents] = useState([]);
  const [showEvents, setShowEvents] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedEmail = localStorage.getItem("email");

    if (savedEmail) {
      setEmail(savedEmail);
    }
  }, []);

  const sendMessage = async () => {
    if (!text) return;

    if (!email) {
      alert("Please login first");
      return;
    }

    setMessages((prev) => [
      ...prev,
      { sender: "user", text }
    ]);

    const res = await addTask(email, text);

    console.log("AI RESPONSE:", res);

    if (res.error) {
      // Only logout for auth problems
      if (
        res.error.includes("not authenticated") ||
        res.error.includes("Session expired")
      ) {
        alert(res.error);
        localStorage.clear();
        window.location.href = "/";
        return;
      }

      alert(`Error: ${res.error}`);
      return;
    }

    setMessages((prev) => [
      ...prev,
      {
        sender: "bot",
        text: res.message || "Task completed"
      }
    ]);

    setText("");

    await loadEvents();
  };

  // ✅ FIXED EVENTS LOADER
  const loadEvents = async (mail) => {
    setLoading(true);

    const emailToUse = mail || email;

    if (!emailToUse) {
      console.error("Email not available");
      setLoading(false);
      return;
    }

    const res = await getEvents(emailToUse);

    console.log("EVENT RESPONSE:", res);

    // ✅ SAFE ARRAY CHECK
    if (Array.isArray(res)) {
      setEvents(res);
    } else {
      console.error("Events is not array:", res);
      setEvents([]);
    }

    setShowEvents(true);
    setLoading(false);
  };

  const handleDelete = async (eventId, title) => {
    if (!eventId) {
      alert("Cannot delete event: missing event id");
      return;
    }

    setLoading(true);

    const result = await deleteEventById(email, eventId);
    if (result.error) {
      alert("Failed to delete event: " + result.error);
      setLoading(false);
      return;
    }

    await loadEvents();

    setLoading(false);
  };

  return (
    <div className="chat-layout">
      <div className={showEvents ? "chat-section shrink" : "chat-section"}>
        <h2>Chat with AI</h2>

        <div className="chat-box">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={msg.sender === "user" ? "user-msg" : "bot-msg"}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type: Meeting tomorrow at 10am"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <button onClick={sendMessage}>
            Send
          </button>

          <button
            className="events-btn"
            onClick={() => loadEvents()}
          >
            Show Events
          </button>
        </div>

        {loading && <p>Loading...</p>}
      </div>

      {showEvents && (
        <div className="events-panel">
          <div className="events-header">
            <h3>Your Events</h3>

            <button onClick={() => setShowEvents(false)}>
              Close
            </button>
          </div>

          {/* ✅ FIXED MAP ERROR */}
          {Array.isArray(events) && events.length > 0 ? (
            events.map((event, i) => (
              <div key={i} className="event-card">
                <h4>{event.summary}</h4>

                <p>
                  {event.start?.dateTime
                    ? new Date(event.start.dateTime).toLocaleString()
                    : "No date"}
                </p>

                <button onClick={() => handleDelete(event.id, event.summary)}>
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p>No events found</p>
          )}
        </div>
      )}
    </div>
  );
}

export default Chat;