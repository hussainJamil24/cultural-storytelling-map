import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import AiLoader from "../components/AiLoader";
import API, { mediaUrl } from "../services/Api";
import { CATEGORIES, getCategory } from "../constants/categories";
import Logo from "../assets/images/logo.png";
import "../assets/styles/browse.css";

const LOCATE_MESSAGES = ["Reading the coordinates…", "Writing a place name…"];

// short preview so long stories don't overrun the card
const getPreview = (content) => {
    if (!content) return "No story content available yet.";
    return content.length > 140 ? `${content.slice(0, 140).trimEnd()}…` : content;
};

// lets a user read stories one category at a time as a plain list --
// no map, no clicking around pins, just pick a category and scroll
export default function BrowsePage() {
    const navigate = useNavigate();
    const [activeCategory, setActiveCategory] = useState("all");
    const [stories, setStories] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    // tracks which story card's "locate" button is currently working, and
    // caches labels already fetched this session so repeat clicks are instant
    const [locatingId, setLocatingId] = useState(null);
    const [locationLabels, setLocationLabels] = useState({});

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
                    setLoadError("We couldn't load the stories. Please try again.");
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

    // asks Gemini to describe where the story is, then jumps to the map
    // centered on it -- this is the whole point of the button: read first,
    // see it on the map only once you actually want to
    const handleLocate = async (story) => {
        if (locationLabels[story.id]) {
            navigate("/map", {
                state: { focusStoryId: story.id, focusLocationLabel: locationLabels[story.id] },
            });
            return;
        }

        setLocatingId(story.id);
        try {
            const res = await API.get(`/stories/${story.id}/locate`);
            setLocationLabels((prev) => ({ ...prev, [story.id]: res.data.label }));
            navigate("/map", {
                state: { focusStoryId: story.id, focusLocationLabel: res.data.label },
            });
        } catch (err) {
            // still useful without the AI label -- just go to the map directly
            navigate("/map", { state: { focusStoryId: story.id } });
        } finally {
            setLocatingId(null);
        }
    };

    return (
        <div className="browse-page">
            <Navbar />

            <header className="browse-header">
                <h1>
                    Browse <span className="gradient-text">Stories</span>
                </h1>
                <p>Read stories by category, no map clicking required.</p>
            </header>

            {/* category filter chips -- the whole "keep it simple" interface */}
            <div className="browse-filters">
                <button
                    className={activeCategory === "all" ? "active" : ""}
                    onClick={() => setActiveCategory("all")}
                >
                    <i className="bi bi-grid-fill"></i>
                    All
                </button>
                {CATEGORIES.map((category) => (
                    <button
                        key={category.key}
                        className={activeCategory === category.key ? "active" : ""}
                        style={
                            activeCategory === category.key
                                ? { background: category.color, borderColor: category.color }
                                : undefined
                        }
                        onClick={() => setActiveCategory(category.key)}
                    >
                        <i className={`bi ${category.icon}`}></i>
                        {category.label}
                    </button>
                ))}
            </div>

            <div className="browse-body">
                {isLoading && (
                    <div className="browse-grid">
                        {[0, 1, 2, 3].map((n) => (
                            <div className="browse-card" key={n}>
                                <div className="skeleton" style={{ height: 140, borderRadius: 0 }} />
                                <div className="browse-card-body">
                                    <div className="skeleton" style={{ height: 12, width: "35%" }} />
                                    <div className="skeleton" style={{ height: 18, marginTop: 10 }} />
                                    <div className="skeleton" style={{ height: 12, marginTop: 10 }} />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {!isLoading && loadError && (
                    <div className="notice notice-error">
                        <i className="bi bi-exclamation-circle-fill"></i>
                        {loadError}
                    </div>
                )}

                {!isLoading && !loadError && stories.length === 0 && (
                    <div className="browse-empty">
                        <img src={Logo} alt="" className="browse-empty-mark" />
                        <h5>No stories here yet</h5>
                        <p>Be the first to add one to this category.</p>
                        <Link to="/upload" className="browse-empty-btn">
                            Share a story
                        </Link>
                    </div>
                )}

                {!isLoading && !loadError && stories.length > 0 && (
                    <div className="browse-grid">
                        {stories.map((story) => {
                            const category = getCategory(story.category);
                            const image = mediaUrl(story.image_url);
                            const isLocating = locatingId === story.id;

                            return (
                                <article className="browse-card" key={story.id}>
                                    {image ? (
                                        <img
                                            src={image}
                                            alt={story.title}
                                            className="browse-card-img"
                                        />
                                    ) : (
                                        <div
                                            className="browse-card-img browse-card-img-empty"
                                            style={{ background: category.color }}
                                        >
                                            <i className={`bi ${category.icon}`}></i>
                                        </div>
                                    )}

                                    <div className="browse-card-body">
                                        <span
                                            className="cat-chip"
                                            style={{ background: category.color }}
                                        >
                                            {category.label}
                                        </span>

                                        <h3>
                                            <Link to={`/story/${story.id}`}>{story.title}</Link>
                                        </h3>

                                        <p>{getPreview(story.content)}</p>

                                        {isLocating ? (
                                            <div className="browse-locate-loading">
                                                <AiLoader inline messages={LOCATE_MESSAGES} />
                                            </div>
                                        ) : (
                                            <button
                                                type="button"
                                                className="browse-locate-btn"
                                                onClick={() => handleLocate(story)}
                                            >
                                                <i className="bi bi-stars"></i>
                                                <span className="browse-locate-label">
                                                    {locationLabels[story.id]
                                                        ? locationLabels[story.id]
                                                        : "Where is this?"}
                                                </span>
                                                <i className="bi bi-arrow-right browse-locate-arrow"></i>
                                            </button>
                                        )}
                                    </div>
                                </article>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
