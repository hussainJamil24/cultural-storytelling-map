import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import '../assets/styles/mapview.css';
import popup from'../assets/images/old-nicosia.jpg';
import { useEffect, useState } from "react";
import API from "../services/Api";

// create colored marker icon
const createIcon = (color) =>
    new L.Icon({
        iconUrl: `https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-${color}.png`,
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
    });

    // map category → color
    const getMarkerIcon = (category) => {
        switch (category) {
            case "heritage":
                return createIcon("blue");
            case "landmarks":
                return createIcon("red");
            case "oral_history":
                return createIcon("green");
            case "customs":
                return createIcon("yellow");
            default:
                return createIcon("blue");
        }
    };

// renders the reusable story map with approved story markers
// renders category filters instead of navigation links
// clicking a category updates the selected category in the parent component
// receives the selected category and updates map content accordingly
export default function MapView({ activeCategory }) {
    
    console.log(activeCategory);

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
    // stores stories fetched from the backend based on selected category
    const [stories, setStories] = useState([]);

    // loads approved stories when the map first renders
    // fetches stories whenever the selected category changes
    // if "all" is selected, fetches all approved stories
    // otherwise, fetches stories filtered by category
    useEffect(() => {
        const fetchStories = async () => {
            try {
                let url = "/stories";
                if (activeCategory !== "all") {
                    url += `?category=${activeCategory}`;
                }

                const res = await API.get(url);
                setStories(res.data);

                console.log(res.data);

            } catch (err) {
                console.error("Error fetching stories", err);
            }
        };

        fetchStories();
    }, [activeCategory]);

    // saerch by title
    const [searchTerm, setSearchTerm] = useState("");

    const filteredStories = stories.filter((story) => {
        const hasValidCoords = Number.isFinite(Number(story.latitude)) &&
        Number.isFinite(Number(story.longitude));

        const matchesSearch = story.title?.toLowerCase().includes(searchTerm.trim().toLowerCase());
        return hasValidCoords && matchesSearch;
    });

    return (
        <div className="map-container">
            {/* shows a placeholder search input */}
            <div className="map-search">
                <input
                    type="text"
                    placeholder="Search stories..."
                    className="form-control shadow"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            {/* links to the story upload form */}
            <div className="map-upload-btn">
                <Link to="/upload" className="upload-btn mt-auto">
                    <i className="bi bi-plus-lg"></i>
                    Upload Story
                </Link>
            </div>

            {/* show message when no result */}
            {searchTerm && filteredStories.length === 0 && (
                <p className="no-results">No stories found</p>
            )}

            {/* renders the map with a custom zoom control placement */}
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false}
            style={{ height: "100vh" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

                {/* renders markers only for stories with valid coordinates */}
                    {filteredStories.map((story) => (
                    <Marker key={story.id}
                        position={[Number(story.latitude), Number(story.longitude)]}
                        icon={getMarkerIcon(story.category)}
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
                                        <Link to={`/story/${story.id}`} className="popup-btn">
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
