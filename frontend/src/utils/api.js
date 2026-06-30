import axios from "axios";

// Create a configured axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://127.0.0.1:8000",
});

// Add a request interceptor to attach the token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

export default api;
