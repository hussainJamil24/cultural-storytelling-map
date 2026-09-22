import axios from "axios";

// single place to point the app at a backend, overridable per environment
export const API_BASE_URL =
    process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

// builds an absolute url for media the backend serves from /uploads
export const mediaUrl = (path) => {
    if (!path) return null;
    if (/^https?:\/\//i.test(path)) return path;
    return `${API_BASE_URL}/${String(path).replace(/^\/+/, "")}`;
};

// creates a shared axios client for backend requests
const API = axios.create({
    baseURL: API_BASE_URL,
});

API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// exports the shared api client
export default API;
