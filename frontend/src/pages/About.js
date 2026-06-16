import Navbar from "../components/Navbar";
import '../assets/styles/about.css';

export default function About() {
    return (
        <div>
            <Navbar />

            {/* HERO */}
            <div className="about-hero">
                <h1>Preserving Stories. Connecting Cultures.</h1>
                <p>
                    An interactive storytelling map where communities share
                    their heritage through real-world locations.
                </p>
            </div>

            {/* CONTENT */}
            <div className="about-container">

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

                <section className="about-card">
                    <h3>How It Works</h3>
                    <ul>
                        <li>Explore stories on the map</li>
                        <li>Upload your own story</li>
                        <li>Admin reviews content</li>
                        <li>Stories become public</li>
                    </ul>
                </section>

            </div>
        </div>
    );
}