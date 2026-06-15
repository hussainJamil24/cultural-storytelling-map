import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import MapView from "../components/MapView";
import '../assets/styles/mappage.css';
import { useState } from 'react';

// combines the navbar, sidebar, and map into the home page
export default function HomePage() {
    // tracks the currently selected category from the sidebar
    // used to filter stories displayed on the map
    const [activeCategory, setActiveCategory] = useState("all");
    console.log(activeCategory);

    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    return(
        <div className="app-container">
            <Navbar />

            {/* MOBILE MENU BUTTON */}
            {!isSidebarOpen && (
                    <button
                        className="menu-btn"
                        onClick={() => setIsSidebarOpen(true)}
                    >
                        ☰
                    </button>
            )}

            {/* lays out the sidebar beside the map */}
            <div className="main-layout d-flex" style={{ height: "100vh" }}>
                {/* shows the sidebar column */}
                <div className={`sidebar-wrapper ${isSidebarOpen ? "open" : "closed"}`}>
                    <Sidebar type="user" onCategoryChange={setActiveCategory}
                    activeCategory={activeCategory}
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                    />
                </div>

                {/* shows the main map area */}
                <div className="map-wrapper flex-grow-1">
                    <MapView activeCategory={activeCategory}/>
                </div>

                {isSidebarOpen && (
                    <div
                        className="overlay"
                        onClick={() => setIsSidebarOpen(false)}
                    ></div>
                )}
            </div>
        </div>
    );
}
