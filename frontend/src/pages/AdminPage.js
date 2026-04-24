import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import image from'../assets/images/old-nicosia.jpg';
import '../assets/styles/admin.css'
import { useEffect, useState } from "react";
import API from "../services/Api";

export default function AdminPage() {
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
        };

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

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
        <div>
            {/* Navbar */}
            <Navbar />

            {/* sidebar + content */}
            <div className="d-flex">
                {!isMobile && <Sidebar type="admin" />}

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
                        <button className="tab-btn active fw-semibold">Pending Review (12)</button>
                        <button className="tab-btn fw-semibold">Recently Approved</button>
                        <button className="tab-btn fw-semibold">Flagged</button>
                    </div>

                    {/* Cards */}
                    <div className="admin-grid mt-3">
                        {/* Admin card */}
                        {stories.map((story) => (
                            <div className="admin-card" key={story.id}>
                                {/* Image */}
                                <img 
                                    src={image}
                                    alt="story"
                                    className="admin-card-img"
                                />

                                {/* Content */}
                                <div className="p-3">

                                    {/* Category + time */}
                                    <div className="d-flex justify-content-between mb-2">
                                        <span className="badge">ORAL HISTORY</span>
                                        <small className="text-muted">2 hours ago</small>
                                    </div>

                                    {/* Title */}
                                    <h5 className="fw-bold">{story.title}</h5>

                                    {/* Description */}
                                    <p className="text-muted small">
                                        {story.narrative?.slice(0, 120)}...
                                    </p>

                                    {/* Buttons */}
                                    <div className="d-flex justify-content-around mt-3">
                                        <button className="approve-btn">
                                            <i className="bi bi-check-lg"></i> Approve
                                        </button>

                                        <button className="reject-btn">
                                            <i className="bi bi-x-lg"></i> Reject
                                        </button>
                                    </div>

                                </div>
                            </div>
                        ))}
                        </div>
                    </div>
                </div>
        </div>
    );
}