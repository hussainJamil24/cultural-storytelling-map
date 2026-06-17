import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import API from "../services/Api";
import Navbar from "../components/Navbar";
import L from "leaflet";


// renders the full map page with navbar and approved story markers
export default function MapPage() {

    const createIcon = (color) =>
    new L.Icon({
        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${color}.png`,
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });

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
            case "migration":
                return createIcon("violet");
            case "food":
                return createIcon("orange");
            case "music":
                return createIcon("grey");
            case "religion":
                return createIcon("black");
            default:
                return createIcon("blue");
    }
};

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
                        icon={getMarkerIcon(story.category)}
                    >
                        <Popup>
                            <div className="popup-card">
                                {/* shows a placeholder popup image */}
                                <div className="popup-image">
                                    {/* uses a temporary image until story media is available */}
                                    {story.image_url && (
                                        <img
                                            src={`http://127.0.0.1:8000/${story.image_url}`}
                                            alt={story.title}
                                        />
                                    )}

                                    {story.audio_url && (
                                        <audio controls style={{ width: "100%", marginTop: "8px" }}>
                                            <source
                                                src={`http://127.0.0.1:8000/${story.audio_url}`}
                                                type="audio/mpeg"
                                            />
                                            Your browser does not support audio.
                                        </audio>
                                    )}

                                    {!story.image_url && !story.audio_url && (
                                        <img
                                            src="https://via.placeholder.com/300"
                                            alt="placeholder"
                                        />
                                    )}
                                </div>

                                {/* shows the story title, preview, and action */}
                                <div className="popup-content">
                                    <h5>{story.title}</h5>
                                    <p>{getStoryPreview(story)}</p>

                                    {/* shows the current fallback action when no media link exists */}
                                    <Link to={`/story/${story.id}`} className="popup-btn">
                                        View Full Story
                                    </Link>
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
