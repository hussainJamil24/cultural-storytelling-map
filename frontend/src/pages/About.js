import Navbar from "../components/Navbar";
import { Link } from "react-router-dom";
import '../assets/styles/about.css';

export default function About() {
    return (
        <div>
            <Navbar />

            {/* HERO */}
            <div className="about-hero">
                <h1>Every Place Holds a Story</h1>
                <p>
                    Discover, preserve, and share cultural stories connected to real locations around the world.
                </p>

                <div className="hero-cta">
                    <Link to="/upload" className="upload-btn mt-auto">
                        <i className="bi bi-send"></i>
                        Start Sharing
                    </Link>
                </div>
            </div>

            {/* CONTENT */}
            <div className="about-container about-background">

                <section className="about-card">
                    <h3>The Problem</h3>
                    <p>
                        Many minority communities lack visibility, and their
                        stories risk being lost over time.
                    </p>
                </section>

                <section className="about-card alt">
                    <h3>Our Solution</h3>
                    <p>
                        We connect storytelling with maps to create an immersive,
                        location-based cultural archive.
                    </p>
                </section>

                <section className="about-steps">
                    <h3>How It Works</h3>

                    <div className="steps-grid">
                        <div className="step">
                            <h4> <i className="bi bi-geo-alt-fill me-2"></i> Explore</h4>
                            <p>Browse stories pinned across the map.</p>
                        </div>

                        <div className="step">
                            <h4> <i className="bi bi-pencil-fill me-2"></i> Share</h4>
                            <p>Upload your story with images or audio.</p>
                        </div>

                        <div className="step">
                            <h4> <i className="bi bi-check-circle-fill me-2"></i> Review</h4>
                            <p>Stories are reviewed before becoming public.</p>
                        </div>

                        <div className="step">
                            <h4> <i className="bi bi-globe2 me-2"></i> Connect</h4>
                            <p>Discover cultures and histories worldwide.</p>
                        </div>
                    </div>
                </section>

                <section className="about-impact">
                    <h3>Why It Matters</h3>
                    <p>
                        Stories shape identity and culture. By preserving them, we ensure
                        that voices, memories, and traditions are never lost.
                    </p>

                    <div className="about-cta">
                        <h3>Be part of the story</h3>
                        <p>Start sharing your cultural experience today.</p>
                        <Link to="/upload" className="upload-btn mt-auto">
                            <i className="bi bi-plus-lg"></i>
                            Upload Story
                        </Link>
                    </div>
                </section>

            </div>
        </div>
    );
}