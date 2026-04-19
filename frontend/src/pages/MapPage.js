import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import popup from'../assets/images/old-nicosia.jpg';
import API from "../services/Api";
import Navbar from "../components/Navbar";

export default function MapPage() {
    const getStoryPreview = (story) => {
        if (!story.content) {
            return "No story content available yet.";
        }

        return story.content.length > 80
            ? `${story.content.slice(0, 80)}...`
            : story.content;
    };

    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // Southwest
        [35.7, 34.8], // Northeast
    ];

    const [stories, setStories] = useState([]);
        useEffect(() => {
        const fetchStories = async () => {
            try {
                const res = await API.get("/stories");
                setStories(res.data);
            } catch (err) {
                console.error("Error fetching stories", err);
            }
        };

        fetchStories();
    }, []);

    return(
        <div className="map-container">
            <Navbar/>
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false} // disable default
            style={{ height: "100vh" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
                {stories
                    .filter((story) => Number.isFinite(Number(story.latitude)) && Number.isFinite(Number(story.longitude)))
                    .map((story) => (
                    <Marker key={story.id}
                        position={[Number(story.latitude), Number(story.longitude)]}
                    >
                        <Popup>
                            <div className="popup-card">
                                {/* Image */}
                                <div className="popup-image">
                                    <img
                                        src={popup} // temporary static image
                                        alt="story"
                                    />
                                </div>

                                {/* Content */}
                                <div className="popup-content">
                                    <h5>{story.title}</h5>
                                    <p>{getStoryPreview(story)}</p>

                                    {/* Media link */}
                                    {story.media_url && (
                                        <a
                                            href={story.media_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="popup-btn"
                                        >
                                            Open Media
                                        </a>
                                    )}
                                    {!story.media_url && (
                                        <Link to="/upload" className="popup-btn">
                                        View Full Story
                                        </Link>
                                    )}
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
                

                {/* Zoom on right */}
                <ZoomControl position="topright" />
            </MapContainer>
        </div>
    );
}
