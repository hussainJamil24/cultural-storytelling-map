import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import MapPage from "./pages/MapPage";
import AdminPage from "./pages/AdminPage";
import './App.css';

// renders the main application routes
function App() {
  return (
    <BrowserRouter>
      {/* defines the main page routes */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
