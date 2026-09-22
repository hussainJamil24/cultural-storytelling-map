import { Link } from "react-router-dom";
import "../assets/styles/sidebar.css";
import { CATEGORIES } from "../constants/categories";

// renders the story category sidebar and upload link
// category list is driven by the shared category config
export default function Sidebar({ type, onCategoryChange, onClose, activeCategory }) {
    return (
        <div className="sidebar d-flex flex-column">
            {onClose && (
                <button className="close-btn" onClick={onClose} aria-label="Close menu">
                    <i className="bi bi-x-lg"></i>
                </button>
            )}

            <div className="sidebar-head">
                <h5>Categories</h5>
                <p>Filter stories on the map</p>
            </div>

            <ul className="sidebar-menu d-flex flex-column">
                <li
                    className={activeCategory === "all" ? "active" : ""}
                    onClick={() => onCategoryChange("all")}
                >
                    <div className="menu-link">
                        <span className="menu-icon" style={{ background: "var(--ink-soft)" }}>
                            <i className="bi bi-grid-fill"></i>
                        </span>
                        <span className="menu-label">All stories</span>
                    </div>
                </li>

                {CATEGORIES.map((category) => (
                    <li
                        key={category.key}
                        className={activeCategory === category.key ? "active" : ""}
                        onClick={() => onCategoryChange(category.key)}
                    >
                        <div className="menu-link">
                            <span className="menu-icon" style={{ background: category.color }}>
                                <i className={`bi ${category.icon}`}></i>
                            </span>
                            <span className="menu-label">{category.label}</span>
                        </div>
                    </li>
                ))}
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
