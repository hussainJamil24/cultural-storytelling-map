import axios from "axios";

// creates a shared axios client for backend requests
const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

// before every request, attach the JWT token from localStorage if it exists.
// this is what lets protected endpoints (submit story, moderation) know who you are.
API.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// exports the shared api client
export default API;
