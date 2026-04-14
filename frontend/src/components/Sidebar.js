import { Link } from "react-router-dom";
import '../assets/styles/sidebar.css';

export default function Sidebar() {
    return (
        <div className="sidebar d-flex flex-column bg-light p-4" style={{ width: "275px", height:"100vh" }}>
            <h5>Categories</h5>
            <p className="text-muted small">Filter stories</p>

            <ul className="sidebar-menu d-flex flex-column">
                <li className='active'>
                    <Link to="/map" className="menu-link d-flex align-items-center">
                        <i className="bi bi-grid-fill"></i>
                        <span>All</span>
                    </Link>
                </li>

                <li>
                    <Link to="/heritage" className="menu-link d-flex align-items-center">
                        <i className="bi bi-journal-bookmark"></i>
                        <span>Heritage</span>
                    </Link>
                </li>

                <li>
                    <Link to="/landmarks" className="menu-link d-flex align-items-center">
                        <i className="bi bi-bank2"></i>
                        <span>Landmarks</span>
                    </Link>
                </li>

                <li>
                    <Link to="/oral" className="menu-link d-flex align-items-center">
                        <i className="bi bi-mic-fill"></i>
                        <span>Oral Histories</span>
                    </Link>
                </li>

                <li>
                    <Link to="/customs" className="menu-link d-flex align-items-center">
                        <i className="bi bi-stars"></i>
                        <span>Customs</span>
                    </Link>
                </li>
            </ul>

            <button className="upload-btn mt-auto">
                <i className="bi bi-plus-lg"></i>
                Upload Story
            </button>
        </div>
    );
}