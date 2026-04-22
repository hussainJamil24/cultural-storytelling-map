import axios from "axios";

// creates a shared axios client for backend requests
const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

// exports the shared api client
export default API;
