import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import '../assets/styles/mappage.css'

export default function MapPage() {
    return(
        <div className="app-container">
            <Navbar />
            {/* Main Layout */}
            <div className="main-layout d-flex" style={{ height: "100vh" }}>
                {/* Sidebar */}
                <div className="sidebar-wrapper">
                    <Sidebar />
                </div>

                {/* Map */}
                <div className="map-wrapper flex-grow-1">
                    <MapView />
                </div>
            </div>
        </div>
    );
}