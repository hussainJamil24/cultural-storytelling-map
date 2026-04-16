import { Link } from "react-router-dom";
import '../assets/styles/navbar.css'
import Logo from '../assets/images/logo.png';

export default function Navbar() {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-4">
            {/* Logo */}
            <Link to="/map" className="navbar-brand d-flex align-items-center fw-bold">
                <img src={Logo} alt="StoryTelling"
                    style={{ width: "50px", marginRight: "10px" }}/>
                    StoryTelling
            </Link>
            
             {/* Mobile Toggle */}
            <button
                className="navbar-toggler custom-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            {/* Links + Right side */}
            <div className="collapse navbar-collapse" id="navbarNav">
                {/* Center Links */}
                <ul className="navbar-nav mx-auto mobile-nav">
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/map">Map</Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link fw-bold" to="/upload">Upload Story</Link>
                    </li>
                </ul>

                {/* Right Side */}
                <div className="d-flex">
                    <Link className="btn btn-outline-primary rounded-pill px-3" to="/Login">
                        Logo in
                    </Link>
                </div>
            </div>
        </nav>
    );
}