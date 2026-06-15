import Navbar from "../components/Navbar";

export default function About() {
    return (
        <div>
            <Navbar />

            <div className="container mt-5">
                <h1>Preserving Stories. Connecting Cultures.</h1>

                <p>
                    Our platform is an interactive storytelling map that allows
                    communities to share cultural narratives linked to real-world locations.
                </p>

                <h3 className="mt-4">The Problem</h3>
                <p>
                    Many minority communities lack visibility, and their stories
                    risk being lost over time.
                </p>

                <h3 className="mt-4">Our Solution</h3>
                <p>
                    We connect storytelling with maps to create an immersive,
                    location-based cultural archive.
                </p>

                <h3 className="mt-4">How It Works</h3>
                <ul>
                    <li>Explore stories on the map</li>
                    <li>Upload your own story</li>
                    <li>Admin reviews content</li>
                    <li>Stories become public</li>
                </ul>
            </div>
        </div>
    );
}