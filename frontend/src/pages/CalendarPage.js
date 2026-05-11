import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import { getEvents, deleteEventById } from "../api";

function CalendarPage() {
  const [date, setDate] = useState(new Date());
  const [email, setEmail] = useState("");
  const [events, setEvents] = useState([]);
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedEmail = localStorage.getItem("email");
    if (savedEmail) {
      setEmail(savedEmail);
      loadEvents(savedEmail);
    }
  }, []);

  const loadEvents = async (mail) => {
    setLoading(true);
    const res = await getEvents(mail);
    if (res.error) {
      alert(res.error);
      localStorage.clear();
      window.location.href = "/";
      return;
    }
    setEvents(Array.isArray(res) ? res : []);
    setLoading(false);
  };

  const handleDateClick = (value) => {
    setDate(value);

    const filtered = events.filter((event) => {
      if (!event.start?.dateTime) return false;

      const eventDate = new Date(event.start.dateTime);
      const selectedDate = new Date(value);

      return eventDate.toDateString() === selectedDate.toDateString();
    });

    setSelectedEvents(filtered);
  };

  const handleDelete = async (eventId, title) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    setLoading(true);
    const result = await deleteEventById(email, eventId);

    if (result.error) {
      alert("Failed to delete event: " + result.error);
    } else {
      alert(result.message || "Event deleted successfully");
      await loadEvents(email);
    }

    setLoading(false);
  };

  return (
    <div className="calendar-page">
      <h2>Calendar View</h2>

      {loading && <p>Loading...</p>}

      <div className="calendar-container">
        <Calendar
          onChange={handleDateClick}
          value={date}
          tileContent={({ date, view }) => {
            if (view === "month") {
              const hasEvent = events.some((event) => {
                if (!event.start?.dateTime) return false;
                const eventDate = new Date(event.start.dateTime);
                return eventDate.toDateString() === date.toDateString();
              });

              return hasEvent ? <div className="event-dot"></div> : null;
            }
          }}
        />

        <div className="calendar-events">
          <h3>Events on {date.toDateString()}</h3>

          {selectedEvents.length === 0 ? (
            <p>No events</p>
          ) : (
            selectedEvents.map((event, i) => (
              <div key={i} className="event-card">
                <h4>{event.summary}</h4>
                <p>
                  {event.start?.dateTime
                    ? new Date(event.start.dateTime).toLocaleTimeString()
                    : "No time"}
                </p>
                <button onClick={() => handleDelete(event.id, event.summary)}>
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default CalendarPage;