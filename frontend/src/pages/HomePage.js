import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import '../assets/styles/mappage.css'

// combines the navbar, sidebar, and map into the home page
export default function HomePage() {
    return(
        <div className="app-container">
            <Navbar />
            {/* lays out the sidebar beside the map */}
            <div className="main-layout d-flex" style={{ height: "100vh" }}>
                {/* shows the sidebar column */}
                <div className="sidebar-wrapper">
                    <Sidebar />
                </div>

                {/* shows the main map area */}
                <div className="map-wrapper flex-grow-1">
                    <MapView />
                </div>
            </div>
        </div>
    );
}
