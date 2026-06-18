import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import '../assets/styles/mapview.css';
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

// pans and zooms the map to a matching story when searching
function FlyToStory({ story }) {
    const map = useMap();
    const id = story?.id;

    useEffect(() => {
        if (story) {
            map.flyTo([Number(story.latitude), Number(story.longitude)], 14, {
                duration: 1.2,
            });
        }
        // only re-fly when the matched story changes
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    return null;
}

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

            {/* show message when no result */}
            {searchTerm && filteredStories.length === 0 && (
                <p className="no-results">No stories found</p>
            )}

            {/* renders the map with a custom zoom control placement */}
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false}
            style={{ height: "100vh", width: "100%" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

                {/* flies to the first matching story when a search is active */}
                <FlyToStory
                    story={
                        searchTerm.trim() && filteredStories.length > 0
                            ? filteredStories[0]
                            : null
                    }
                />

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
                                    {story.image_url && (
                                        <img src={`http://127.0.0.1:8000/${story.image_url}`}  alt={story.title}/>
                                    )}

                                    {story.audio_url && (
                                        <audio controls>
                                            <source src={`http://127.0.0.1:8000/${story.audio_url}`} />
                                        </audio>
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
