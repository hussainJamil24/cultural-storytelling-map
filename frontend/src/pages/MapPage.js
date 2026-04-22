import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import popup from'../assets/images/old-nicosia.jpg';
import API from "../services/Api";
import Navbar from "../components/Navbar";

// renders the full map page with navbar and approved story markers
export default function MapPage() {
    // builds a short preview for each story popup
    const getStoryPreview = (story) => {
        if (!story.content) {
            return "No story content available yet.";
        }

        return story.content.length > 80
            ? `${story.content.slice(0, 80)}...`
            : story.content;
    };

    // centers the map on cyprus and keeps panning inside island bounds
    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // southwest map limit
        [35.7, 34.8], // northeast map limit
    ];

    // stores approved stories loaded from the api
    const [stories, setStories] = useState([]);

    // loads approved stories when the page first renders
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
            {/* shows the shared site navigation */}
            <Navbar/>

            {/* renders the map with a custom zoom control placement */}
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false}
            style={{ height: "100vh" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

                {/* renders markers only for stories with valid coordinates */}
                {stories
                    .filter((story) => Number.isFinite(Number(story.latitude)) && Number.isFinite(Number(story.longitude)))
                    .map((story) => (
                    <Marker key={story.id}
                        position={[Number(story.latitude), Number(story.longitude)]}
                    >
                        <Popup>
                            <div className="popup-card">
                                {/* shows a placeholder popup image */}
                                <div className="popup-image">
                                    {/* uses a temporary image until story media is available */}
                                    <img
                                        src={popup}
                                        alt="story"
                                    />
                                </div>

                                {/* shows the story title, preview, and action */}
                                <div className="popup-content">
                                    <h5>{story.title}</h5>
                                    <p>{getStoryPreview(story)}</p>

                                    {/* opens the linked media when one exists */}
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

                                    {/* shows the current fallback action when no media link exists */}
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
                

                {/* shows zoom controls on the right side of the map */}
                <ZoomControl position="topright" />
            </MapContainer>
        </div>
    );
}
