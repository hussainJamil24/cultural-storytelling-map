import { Link } from "react-router-dom";
import '../assets/styles/navbar.css'
import Logo from '../assets/images/logo.png'

export default function Navbar() {
    return (
        <nav className="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-4">
            {/* Logo */}
            <div className="logo-section">
                {/* <img className="logo" style={{width:"75px"}} src={Logo} alt="StoryTelling"/> */}
                <span className="navbar-brand fw-bold">
                    <img className="logo" style={{width:"75px"}} src={Logo} alt="StoryTelling"/>
                    StoryTelling
                </span>
            </div>
            

            {/* Navigation Links */}
            <div className="collapse navbar-collapse justify-content-center">
                <div className="navbar-nav">
                    <Link className="nav-link fw-bold" to="/map">Map</Link>
                    <Link className="nav-link fw-bold" to="/upload">Upload Story</Link>
                </div>
            </div>

            {/* Right Side */}
            <div className="user-section">
                <Link className="login-btn" to="/">
                    Logout
                </Link>
            </div>
        </nav>
    );
}