import { Link } from "react-router-dom";
import '../assets/styles/sidebar.css';

// renders the story category sidebar and upload link
// passes the category change handler to the sidebar
// allows sidebar clicks to update the selected category
export default function Sidebar({type,  onCategoryChange, onClose, activeCategory }) {
    return (
        <div className="sidebar d-flex flex-column bg-light p-4" style={{ width: "275px", height:"100vh" }}>
            {onClose && (
                <button className="close-btn" onClick={onClose}>
                ✖
                </button>
            )}

            {/* shows the sidebar heading */}
            <h5>Categories</h5>
            <p className="text-muted small">Filter stories</p>

            {/*  category list used to filter stories on the map
             replaces route-based navigation with dynamic filtering */}
            <ul className="sidebar-menu d-flex flex-column">
                <li className={activeCategory === "all" ? "active" : ""} onClick={() => onCategoryChange("all")}>
                    {/* triggers category change when clicked, updates activeCategory in HomePage*/}
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-grid-fill"></i>
                        <span>All</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("heritage")}
                    className={activeCategory === "heritage" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-journal-bookmark"></i>
                        <span>Heritage</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("landmarks")}
                    className={activeCategory === "landmarks" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-bank2"></i>
                        <span>Landmarks</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("oral_history")}
                    className={activeCategory === "oral_history" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-mic-fill"></i>
                        <span>Oral Histories</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("customs")}
                    className={activeCategory === "customs" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-stars"></i>
                        <span>Customs</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("migration")}
                    className={activeCategory === "migration" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-globe"></i>
                        <span>Migration</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("religion")}
                    className={activeCategory === "religion" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-book"></i>
                        <span>Religion</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("music")}
                    className={activeCategory === "music" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-music-note-beamed"></i>
                        <span>Music</span>
                    </div>
                </li>

                <li onClick={() => onCategoryChange("food")}
                    className={activeCategory === "food" ? "active" : ""}
                >
                    <div className="menu-link d-flex align-items-center">
                        <i className="bi bi-cup-hot-fill"></i> 
                        <span>Food</span>
                    </div>
                </li>
            </ul>

            {/* links to the story upload page */}
            {type !== "admin" && (
                <Link to="/upload" className="upload-btn mt-auto">
                    <i className="bi bi-plus-lg"></i>
                    Upload Story
                </Link>
            )}
        </div>
    );
}
