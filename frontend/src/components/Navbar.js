import { Link } from "react-router-dom";
import '../assets/styles/navbar.css'
import Logo from '../assets/images/logo.png';

// renders the top navigation bar
export default function Navbar() {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-2 px-md-4">
            {/* links the brand back to the map page */}
            <Link to="/map" className="navbar-brand d-flex align-items-center fw-bold">
                <img src={Logo} alt="StoryTelling"
                    style={{ width: "50px", marginRight: "10px" }}/>
                    StoryTelling
            </Link>
            
             {/* toggles the collapsed menu on smaller screens */}
            <button
                className="navbar-toggler custom-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            {/* groups the navigation links and login action */}
            <div className="collapse navbar-collapse" id="navbarNav">
                {/* shows the main navigation links */}
                <ul className="navbar-nav mx-auto mobile-nav">
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/map">Map</Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/upload">Upload Story</Link>
                    </li>
                </ul>

                {/* shows the login button */}
                <div className="d-flex">
                    <Link className="btn btn-outline-primary rounded-pill px-3" to="/login">
                        Log in
                    </Link>
                </div>
            </div>
        </nav>
    );
}
