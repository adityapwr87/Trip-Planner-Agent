import axios from "axios";

export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function loginApi(email, password) {
  const { data } = await api.post("/auth/login", {
    email,
    password
  });
  return data;
}

export async function signupApi(email, password, fullName) {
  const { data } = await api.post("/auth/signup", {
    email,
    password,
    full_name: fullName
  });
  return data;
}
export async function getSessions() {
  const { data } = await api.get("/sessions");
  return data.sessions || [];
}

export async function getChatHistory(sessionId) {
  const { data } = await api.get(`/chat/${sessionId}`);
  return data;
}

export async function sendChatMessage({ message, sessionId }) {
  const { data } = await api.post("/chat", {
    message,
    session_id: sessionId,
  });
  return data;
}

export async function resumeChat({ sessionId, approved }) {
  const { data } = await api.post("/chat/resume", {
    session_id: sessionId,
    approved: approved,
  });
  return data;
}

export async function generateDirectItinerary(form) {
  const { data } = await api.post("/itinerary/generate", {
    ...form,
    travelers: Number(form.travelers),
  });
  return data;
}

export async function compareDestinations(form) {
  const { data } = await api.post("/api/explore/compare", {
    source: form.source || undefined,
    destination_1: form.destination_1,
    destination_2: form.destination_2,
    start_date: form.start_date,
    end_date: form.end_date,
    travelers: Number(form.travelers),
    budget: form.budget,
    preferences: form.preferences,
  });
  return data;
}
