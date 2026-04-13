import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";

export default function MapPage() {
    return(
        <div className="app-container">
            <Navbar />
            {/* mapcontainer */}
            <div className="d-flex" style={{ height: "100vh" }}>
                <Sidebar />
                <div className="flex-grow-1">
                    <MapView />
                </div>
            </div>
        </div>
    );
}