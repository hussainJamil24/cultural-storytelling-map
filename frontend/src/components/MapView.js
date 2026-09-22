import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import "../assets/styles/mapview.css";
import { useEffect, useMemo, useState } from "react";
import API, { mediaUrl } from "../services/Api";
import { getCategory, getMarkerIcon } from "../constants/categories";
import Logo from "../assets/images/logo.png";

// centers the map on cyprus and keeps panning inside island bounds
const CYPRUS_CENTER = [35.1264, 33.4299];
const CYPRUS_BOUNDS = [
    [34.5, 32.0], // southwest map limit
    [35.7, 34.8], // northeast map limit
];

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

// builds a short preview for each story popup
const getStoryPreview = (story) => {
    if (!story.content) {
        return "No story content available yet.";
    }

    return story.content.length > 110
        ? `${story.content.slice(0, 110).trimEnd()}…`
        : story.content;
};

// renders the reusable story map with approved story markers
export default function MapView({ activeCategory, focusStoryId, focusLocationLabel }) {
    const [stories, setStories] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [searchTerm, setSearchTerm] = useState("");

    // fetches stories whenever the selected category changes
    useEffect(() => {
        let isCurrent = true;

        const fetchStories = async () => {
            setIsLoading(true);
            setLoadError("");

            try {
                const url =
                    activeCategory === "all"
                        ? "/stories"
                        : `/stories?category=${activeCategory}`;

                const res = await API.get(url);
                if (isCurrent) setStories(res.data);
            } catch (err) {
                if (isCurrent) {
                    setLoadError(
                        "We couldn't load the stories. Check the connection and try again."
                    );
                }
            } finally {
                if (isCurrent) setIsLoading(false);
            }
        };

        fetchStories();
        return () => {
            isCurrent = false;
        };
    }, [activeCategory]);

    // matches on title and story body so search finds themes, not just names
    const filteredStories = useMemo(() => {
        const term = searchTerm.trim().toLowerCase();

        return stories.filter((story) => {
            const hasValidCoords =
                Number.isFinite(Number(story.latitude)) &&
                Number.isFinite(Number(story.longitude));

            if (!hasValidCoords) return false;
            if (!term) return true;

            return (
                story.title?.toLowerCase().includes(term) ||
                story.content?.toLowerCase().includes(term)
            );
        });
    }, [stories, searchTerm]);

    return (
        <div className="map-container">
            {/* floating search panel over the map */}
            <div className="map-search">
                <div className="map-search-field">
                    <i className="bi bi-search" aria-hidden="true"></i>
                    <input
                        type="search"
                        placeholder="Search stories, places, themes…"
                        aria-label="Search stories"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    {searchTerm && (
                        <button
                            type="button"
                            className="map-search-clear"
                            aria-label="Clear search"
                            onClick={() => setSearchTerm("")}
                        >
                            <i className="bi bi-x-lg"></i>
                        </button>
                    )}
                </div>

                {/* live status under the search field */}
                {isLoading && (
                    <div className="map-status">
                        <span className="map-status-dot" />
                        Loading stories…
                    </div>
                )}

                {!isLoading && loadError && (
                    <div className="map-status map-status-error">
                        <i className="bi bi-exclamation-triangle-fill"></i>
                        {loadError}
                    </div>
                )}

                {!isLoading && !loadError && (
                    <div className="map-status">
                        <i className="bi bi-geo-alt-fill"></i>
                        {filteredStories.length}{" "}
                        {filteredStories.length === 1 ? "story" : "stories"}
                        {activeCategory !== "all" &&
                            ` in ${getCategory(activeCategory).label}`}
                    </div>
                )}
                {!isLoading && !loadError && focusLocationLabel && !searchTerm.trim() &&
                    filteredStories.some((story) => story.id === focusStoryId) && (
                        <div className="map-status" role="status" aria-live="polite">
                            <i className="bi bi-stars" aria-hidden="true"></i>
                            <span>Approximate place (AI): {focusLocationLabel}</span>
                        </div>
                    )}
            </div>

            <MapContainer
                center={CYPRUS_CENTER}
                zoom={9}
                maxBounds={CYPRUS_BOUNDS}
                maxBoundsViscosity={1.0}
                zoomControl={false}
                style={{ height: "100%", width: "100%" }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />

                {/* flies to a search match first, otherwise a story handed off
                    from the Browse tab's "locate" button */}
                <FlyToStory
                    story={
                        searchTerm.trim() && filteredStories.length > 0
                            ? filteredStories[0]
                            : stories.find((s) => s.id === focusStoryId) || null
                    }
                />

                {filteredStories.map((story) => {
                    const category = getCategory(story.category);
                    const image = mediaUrl(story.image_url);
                    const audio = mediaUrl(story.audio_url);

                    return (
                        <Marker
                            key={story.id}
                            position={[Number(story.latitude), Number(story.longitude)]}
                            icon={getMarkerIcon(story.category)}
                        >
                            <Popup>
                                <article className="popup-card">
                                    {image ? (
                                        <div className="popup-image">
                                            <img src={image} alt={story.title} />
                                            <span
                                                className="cat-chip popup-chip"
                                                style={{ background: category.color }}
                                            >
                                                <i className={`bi ${category.icon}`}></i>
                                                {category.label}
                                            </span>
                                        </div>
                                    ) : (
                                        <div
                                            className="popup-image popup-image-empty"
                                            style={{ background: category.color }}
                                        >
                                            <i className={`bi ${category.icon}`}></i>
                                            <span className="cat-chip popup-chip popup-chip-solid">
                                                {category.label}
                                            </span>
                                        </div>
                                    )}

                                    <div className="popup-content">
                                        <h5>{story.title}</h5>
                                        <p>{getStoryPreview(story)}</p>

                                        {audio && (
                                            <audio controls preload="none" src={audio}>
                                                Your browser does not support audio playback.
                                            </audio>
                                        )}

                                        <Link to={`/story/${story.id}`} className="popup-btn">
                                            Read full story
                                            <i className="bi bi-arrow-right"></i>
                                        </Link>
                                    </div>
                                </article>
                            </Popup>
                        </Marker>
                    );
                })}

                <ZoomControl position="topright" />
            </MapContainer>

            {/* empty state when a filter or search returns nothing */}
            {!isLoading && !loadError && filteredStories.length === 0 && (
                <div className="map-empty">
                    <img src={Logo} alt="" className="map-empty-mark" />
                    <h5>No stories here yet</h5>
                    <p>
                        {searchTerm
                            ? "Try a different search term or clear the filter."
                            : "Be the first to add a story to this category."}
                    </p>
                    <Link to="/upload" className="map-empty-btn">
                        Share a story
                    </Link>
                </div>
            )}
        </div>
    );
}
