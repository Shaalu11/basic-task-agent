const BASE_URL = "http://localhost:8000";

export const login = async () => {
  const res = await fetch(`${BASE_URL}/login`);
  const data = await res.json();
  window.location.href = data.auth_url;
};

export const logout = async (email) => {
  try {
    const res = await fetch(`${BASE_URL}/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return await res.json();
  } catch (err) {
    return { error: "Logout failed" };
  }
};

export const validateSession = async (email) => {
  try {
    const res = await fetch(`${BASE_URL}/validate-session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    return await res.json();
  } catch (err) {
    return { valid: false };
  }
};

export const addTask = async (email, text) => {
  try {
    const res = await fetch(`${BASE_URL}/ai-task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, text }),
    });

    return await res.json();
  } catch (err) {
    return { error: "Server error" };
  }
};

export const getEvents = async (email) => {
  try {
    const res = await fetch(`${BASE_URL}/events/${email}`);
    return await res.json();
  } catch {
    return { error: "Failed to fetch events" };
  }
};

export const deleteEventById = async (email, eventId) => {
  try {
    const res = await fetch(`${BASE_URL}/events/${email}/${eventId}`, {
      method: "DELETE",
    });
    return await res.json();
  } catch {
    return { error: "Delete failed" };
  }
};

export const deleteTask = async (email, title) => {
  try {
    const res = await fetch(`${BASE_URL}/ai-task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        text: `delete ${title}`,
      }),
    });

    return await res.json();
  } catch {
    return { error: "Delete failed" };
  }
};