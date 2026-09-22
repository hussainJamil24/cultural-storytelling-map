import Navbar from "../components/Navbar";
import "../assets/styles/admin.css";
import { useNavigate } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import API, { mediaUrl } from "../services/Api";
import { getCategory } from "../constants/categories";

const TABS = [
    { key: "pending", label: "Pending Review", icon: "bi-hourglass-split" },
    { key: "approved", label: "Approved", icon: "bi-check2-circle" },
    { key: "rejected", label: "Flagged", icon: "bi-flag" },
];

export default function AdminPage() {
    const navigate = useNavigate();

    useEffect(() => {
        const isAdmin = localStorage.getItem("isAdmin");
        if (isAdmin !== "true") {
            navigate("/login");
        }
    }, [navigate]);

    const [loading, setLoading] = useState(true);
    const [stories, setStories] = useState([]);
    const [activeTab, setActiveTab] = useState("pending");
    const [counts, setCounts] = useState({ pending: 0, approved: 0, rejected: 0 });
    const [error, setError] = useState("");
    const [busyId, setBusyId] = useState(null);

    // keeps the header totals in sync with the moderation queue
    const refreshCounts = useCallback(async () => {
        try {
            const results = await Promise.all(
                TABS.map((tab) => API.get(`/stories?status=${tab.key}`))
            );
            setCounts({
                pending: results[0].data.length,
                approved: results[1].data.length,
                rejected: results[2].data.length,
            });
        } catch (err) {
            // counts are supplementary, the queue below still works without them
        }
    }, []);

    useEffect(() => {
        const fetchStories = async () => {
            setLoading(true);
            setError("");
            try {
                const res = await API.get(`/stories?status=${activeTab}`);
                setStories(res.data);
            } catch (err) {
                setError("Could not load the moderation queue. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        fetchStories();
    }, [activeTab]);

    useEffect(() => {
        refreshCounts();
    }, [refreshCounts]);

    // moves a story to a new status and drops it from the current tab
    const setStatus = async (id, status) => {
        setBusyId(id);
        setError("");
        try {
            await API.patch(`/stories/${id}/status`, { status });
            setStories((prev) => prev.filter((s) => s.id !== id));
            refreshCounts();
        } catch (err) {
            setError("Could not update that story. Please try again.");
        } finally {
            setBusyId(null);
        }
    };

    const activeLabel = TABS.find((t) => t.key === activeTab)?.label.toLowerCase();

    return (
        <div>
            <Navbar />

            <div className="admin-shell">
                <header className="admin-header">
                    <h2>Content Moderation</h2>
                    <p>
                        Review submitted cultural stories and oral histories. Ensure each
                        entry meets the archival standards.
                    </p>
                </header>

                {/* queue totals at a glance */}
                <div className="admin-stats">
                    {TABS.map((tab) => (
                        <button
                            key={tab.key}
                            className={`admin-stat ${activeTab === tab.key ? "active" : ""}`}
                            onClick={() => setActiveTab(tab.key)}
                        >
                            <span className={`admin-stat-icon ${tab.key}`}>
                                <i className={`bi ${tab.icon}`}></i>
                            </span>
                            <span className="admin-stat-body">
                                <span className="admin-stat-value">{counts[tab.key]}</span>
                                <span className="admin-stat-label">{tab.label}</span>
                            </span>
                        </button>
                    ))}
                </div>

                {error && (
                    <div className="notice notice-error" style={{ marginBottom: 20 }}>
                        <i className="bi bi-exclamation-circle-fill"></i>
                        {error}
                    </div>
                )}

                {/* loading skeletons keep the grid from collapsing */}
                {loading && (
                    <div className="admin-grid">
                        {[0, 1, 2].map((n) => (
                            <div className="admin-card" key={n}>
                                <div className="skeleton" style={{ height: 150, borderRadius: 0 }} />
                                <div className="p-3">
                                    <div className="skeleton" style={{ height: 14, width: "40%" }} />
                                    <div className="skeleton" style={{ height: 19, marginTop: 12 }} />
                                    <div className="skeleton" style={{ height: 12, marginTop: 12 }} />
                                    <div className="skeleton" style={{ height: 12, width: "75%", marginTop: 8 }} />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {!loading && stories.length === 0 && (
                    <div className="admin-empty">
                        <i className="bi bi-inbox"></i>
                        <h5>Nothing {activeLabel === "pending review" ? "waiting" : "here"}</h5>
                        <p>
                            {activeTab === "pending"
                                ? "The moderation queue is clear. New submissions will appear here."
                                : `No ${activeLabel} stories yet.`}
                        </p>
                    </div>
                )}

                <div className="admin-grid">
                    {!loading &&
                        // AI-flagged stories surface first so a moderator sees them before
                        // scrolling past -- the AI never decides, it just saves attention
                        [...stories]
                            .sort((a, b) => (b.ai_flag === true) - (a.ai_flag === true))
                            .map((story) => {
                            const category = getCategory(story.category);
                            const image = mediaUrl(story.image_url);
                            const audio = mediaUrl(story.audio_url);
                            const isBusy = busyId === story.id;

                            return (
                                <article
                                    className={`admin-card ${story.ai_flag ? "admin-card-flagged" : ""}`}
                                    key={story.id}
                                >
                                    {story.ai_flag && (
                                        <div className="admin-flag-banner">
                                            <i className="bi bi-shield-exclamation"></i>
                                            <span>
                                                <span className="ai-tag">
                                                    <i className="bi bi-stars"></i>
                                                    AI
                                                </span>
                                                <strong>Flagged for review.</strong>{" "}
                                                {story.ai_flag_reason}
                                            </span>
                                        </div>
                                    )}

                                    {image ? (
                                        <img
                                            src={image}
                                            alt={story.title}
                                            className="admin-card-img"
                                        />
                                    ) : (
                                        <div
                                            className="admin-card-img admin-card-img-empty"
                                            style={{ background: category.color }}
                                        >
                                            <i className={`bi ${category.icon}`}></i>
                                        </div>
                                    )}

                                    <div className="p-3">
                                        <div className="admin-card-meta">
                                            <span
                                                className="cat-chip"
                                                style={{ background: category.color }}
                                            >
                                                {category.label}
                                            </span>
                                            <small>
                                                {formatDistanceToNow(new Date(story.created_at), {
                                                    addSuffix: true,
                                                })}
                                            </small>
                                        </div>

                                        <h5>{story.title}</h5>

                                        <p className="admin-card-text">
                                            {story.content?.slice(0, 130)}
                                            {story.content?.length > 130 ? "…" : ""}
                                        </p>

                                        {audio && (
                                            <audio controls preload="none" src={audio} />
                                        )}

                                        <div className="admin-actions">
                                            {activeTab !== "approved" && (
                                                <button
                                                    className="approve-btn"
                                                    disabled={isBusy}
                                                    onClick={() => setStatus(story.id, "approved")}
                                                >
                                                    <i className="bi bi-check-lg"></i>
                                                    {activeTab === "rejected" ? "Restore" : "Approve"}
                                                </button>
                                            )}

                                            {activeTab !== "rejected" && (
                                                <button
                                                    className="reject-btn"
                                                    disabled={isBusy}
                                                    onClick={() => setStatus(story.id, "rejected")}
                                                >
                                                    <i className="bi bi-x-lg"></i>
                                                    Reject
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </article>
                            );
                        })}
                </div>
            </div>
        </div>
    );
}
