import Navbar from "../components/Navbar";
import image from'../assets/images/old-nicosia.jpg';
import '../assets/styles/admin.css';
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import API from "../services/Api";

export default function AdminPage() {

    const navigate = useNavigate();
    useEffect(() => {
        const isAdmin = localStorage.getItem("isAdmin");

        if (isAdmin !== "true") {
        navigate("/login");
        }
    }, [navigate]);

    // add loading state
    const [loading, setLoading] = useState(true);

    const [stories, setStories] = useState([]);

    const [activeTab, setActiveTab] = useState("pending");

    useEffect(() => {
        const fetchStories = async () => {
            setLoading(true); // start loading
            try {
                const res = await API.get(`/stories?status=${activeTab}`);
                setStories(res.data);
            } catch (err) {
                console.error("Error fetching stories", err);
            } finally {
                setLoading(false); // start loading
            }
        };

        fetchStories();
    }, [activeTab]);

    // add approve / reject logic
    const handleApprove = async (id) => {
        try {
            await API.patch(`/stories/${id}/status`, {
                status: "approved"
            });

            setStories(prev => prev.filter(s => s.id !== id))
        } catch (err) {
            console.error(err);
        }
    }

    const handleReject = async (id) => {
        try {
            await API.patch(`/stories/${id}/status`, { status: "rejected" },
            {
                headers: {
                    "Content-Type": "application/json"
                }
            });

            setStories(prev => prev.filter(s => s.id !== id))
        } catch (err) {
            console.error(err);
        }
    }

    return(
        <div>
            {/* Navbar */}
            <Navbar />

            {/* sidebar + content */}
            <div className="d-flex">
                <div className="flex-grow-1 p-4">
                    {/* Header */}
                    <div className="mb-4">
                        <h2 className="fw-bold">Content Moderation</h2>
                        <p className="text-muted">
                            Review submitted cultural stories and oral histories.
                            Ensure each entry meets the archival standards.
                        </p>
                    </div>

                    {/* Tabs */}
                    <div className="tabs-container d-flex flex-wrap gap-2 mb-5">
                        <button className={`tab-btn  fw-semibold ${activeTab === "pending" ? "active" : ""}`}
                            onClick={() => setActiveTab("pending")}
                        >
                            Pending Review
                        </button>

                        <button className={`tab-btn fw-semibold ${activeTab === "approved" ? "active" : ""}`}
                            onClick={() => setActiveTab("approved")}
                        >
                            Recently Approved
                        </button>

                        <button className={`tab-btn fw-semibold ${activeTab === "rejected" ? "active" : ""}`}
                            onClick={() => setActiveTab("rejected")}
                        >
                            Flagged
                        </button>

                    </div>

                    {/* show loading */}
                    {loading && <p>Loading stories...</p>}

                    {/* If no stories */}
                    {!loading && stories.length === 0 && (
                        <p className="text-muted">No stories found.</p>
                    )}

                    {/* Cards */}
                    <div className="admin-grid mt-3">
                        {/* Admin card */}
                        {stories.map((story) => (
                            <div className="admin-card" key={story.id}>
                                {/* Image */}
                                <img 
                                    src={story.media_url || image}
                                    alt="story"
                                    className="admin-card-img"
                                />

                                {/* Content */}
                                <div className="p-3">

                                    {/* Category + time */}
                                    <div className="d-flex justify-content-between mb-2">
                                        <span className="badge">{story.category?.toUpperCase()}</span>
                                        <small className="text-muted">
                                            {formatDistanceToNow(new Date(story.created_at), { addSuffix: true })}
                                        </small>
                                    </div>

                                    {/* Title */}
                                    <h5 className="fw-bold">{story.title}</h5>

                                    {/* Description */}
                                    <p className="text-muted small">
                                        {story.content?.slice(0, 120)}...
                                    </p>

                                    {/* Buttons */}
                                    {activeTab === "pending" && (
                                            <div className="d-flex justify-content-around mt-3">
                                                <button className="approve-btn"  onClick={() => handleApprove(story.id)}>
                                                    <i className="bi bi-check-lg"></i> Approve
                                                </button>

                                                <button className="reject-btn" onClick={() => handleReject(story.id)}>
                                                    <i className="bi bi-x-lg"></i> Reject
                                                </button>
                                            </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        </div>
                    </div>
                </div>
        </div>
    );
}