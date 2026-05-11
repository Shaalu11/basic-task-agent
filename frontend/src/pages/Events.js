import React, { useState, useEffect } from "react";
import { getEvents, deleteEventById } from "../api";

function Events() {
  const [email, setEmail] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedEmail = localStorage.getItem("email");

    if (savedEmail) {
      setEmail(savedEmail);
      loadEvents(savedEmail);
    } else {
      setLoading(false);
    }
  }, []);

  const loadEvents = async (mail) => {
    setLoading(true);

    const res = await getEvents(mail);

    console.log("EVENTS RESPONSE:", res);

    if (res.error) {
      alert(res.error);
      localStorage.clear();
      window.location.href = "/";
      return;
    }

    if (Array.isArray(res)) {
      console.log("Events array:", res);
      console.log("First event:", res[0]);
      setEvents(res);
    } else {
      console.error("Events is not array:", res);
      setEvents([]);
    }

    setLoading(false);
  };

  const handleDelete = async (eventId, title) => {
    console.log("Deleting event:", eventId, title);
    
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    setLoading(true);

    const result = await deleteEventById(email, eventId);
    console.log("Delete result:", result);

    if (result.error) {
      alert("Failed to delete event: " + result.error);
      setLoading(false);
      return;
    }

    alert(result.message || "Event deleted successfully");

    // Reload events after deletion
    await loadEvents(email);
  };

  return (
    <div className="events-page">
      <h2>Your Events</h2>

      {loading && <p>Loading events...</p>}

      {!loading && Array.isArray(events) && events.length > 0 ? (
        events.map((event, i) => (
          <div key={event.id || i} className="event-card">
            <h3>{event.summary}</h3>
            <p>
              {event.start?.dateTime
                ? new Date(event.start.dateTime).toLocaleString()
                : "No date"}
            </p>
            <button onClick={() => {
              console.log("Button clicked for event:", event);
              handleDelete(event.id, event.summary);
            }}>
              Delete
            </button>
          </div>
        ))
      ) : !loading ? (
        <p>No events found</p>
      ) : null}
    </div>
  );
}

export default Events;