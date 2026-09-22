import { Link } from "react-router-dom";
import "../assets/styles/navbar.css";
import Logo from "../assets/images/logo.png";

// reads the signed-in user without throwing on stale storage
const readUser = () => {
    try {
        return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
        return null;
    }
};

// renders the top navigation bar
export default function Navbar() {
    const user = readUser();
    const isAdmin = localStorage.getItem("isAdmin") === "true";
    const initials = user?.name?.trim()?.charAt(0)?.toUpperCase() || "?";

    // logout function
    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        localStorage.removeItem("isAdmin");
        window.location.href = "/login";
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-light px-2 px-md-4">
            {/* links the brand back to the map page */}
            <Link to="/" className="navbar-brand d-flex align-items-center fw-bold">
                <img
                    src={Logo}
                    alt="Narrify"
                    style={{ width: "52px", marginRight: "10px" }}
                />
                <span className="brand-text">Narrify</span>
            </Link>

            {/* toggles the collapsed menu on smaller screens */}
            <button
                className="navbar-toggler custom-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
                aria-label="Toggle navigation"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            {/* groups the navigation links and auth actions */}
            <div className="collapse navbar-collapse" id="navbarNav">
                <ul className="navbar-nav mx-auto mobile-nav">
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/map">
                            Map
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/browse">
                            Browse
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/upload">
                            Upload Story
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/about">
                            About
                        </Link>
                    </li>
                    {/* moderation entry point, only for admins */}
                    {isAdmin && (
                        <li className="nav-item">
                            <Link className="nav-link fw-bold" to="/admin">
                                Moderation
                            </Link>
                        </li>
                    )}
                </ul>

                <div className="d-flex align-items-center">
                    {!user ? (
                        <Link
                            className="btn btn-outline-primary rounded-pill px-3"
                            to="/login"
                        >
                            Log in
                        </Link>
                    ) : (
                        <div className="nav-user">
                            <span className="nav-avatar">{initials}</span>
                            <span className="nav-username">{user.name}</span>
                            {isAdmin && <span className="nav-admin-tag">Admin</span>}
                            <button
                                className="btn btn-outline-danger rounded-pill px-3"
                                onClick={handleLogout}
                            >
                                Logout
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
}
