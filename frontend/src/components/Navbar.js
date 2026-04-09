import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav className="navbar navbar-light bg-light px-3">
            <h4>StoryMap</h4>
            <div>
                <Link to="/">Map</Link> |{" "}
                <Link to="/upload">Upload</Link> |{" "}
                <Link to="/login">Login</Link>
            </div>
        </nav>
    );
}