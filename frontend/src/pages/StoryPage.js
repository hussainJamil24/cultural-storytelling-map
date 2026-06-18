import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import API from "../services/Api";
import Navbar from "../components/Navbar";
import "../assets/styles/storypage.css";

export default function StoryPage() {
    const { id } = useParams();
    const [story, setStory] = useState(null);

    // likes state for this story
    const [likes, setLikes] = useState({ count: 0, liked: false });

    // comments state
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState("");
    const [replyTo, setReplyTo] = useState(null);
    const [replyText, setReplyText] = useState("");
    const [actionError, setActionError] = useState("");

    // current signed-in user (null when logged out)
    const currentUser = JSON.parse(localStorage.getItem("user") || "null");
    const isLoggedIn = Boolean(localStorage.getItem("access_token") && currentUser);

    useEffect(() => {
        const fetchStory = async () => {
            try {
                const res = await API.get(`/stories/${id}`);
                setStory(res.data);
            } catch (err) {
                console.error(err);
            }
        };

        const fetchLikes = async () => {
            try {
                const res = await API.get(`/stories/${id}/likes`);
                setLikes({ count: res.data.count, liked: res.data.liked });
            } catch (err) {
                console.error(err);
            }
        };

        const fetchComments = async () => {
            try {
                const res = await API.get(`/stories/${id}/comments`);
                setComments(res.data);
            } catch (err) {
                console.error(err);
            }
        };

        fetchStory();
        fetchLikes();
        fetchComments();
    }, [id]);

    // toggles the like state for the current user
    const toggleLike = async () => {
        if (!isLoggedIn) {
            setActionError("Please log in to like stories.");
            return;
        }
        setActionError("");
        try {
            const res = likes.liked
                ? await API.delete(`/stories/${id}/likes`)
                : await API.post(`/stories/${id}/likes`);
            setLikes({ count: res.data.count, liked: res.data.liked });
        } catch (err) {
            console.error(err);
            setActionError("Could not update like. Please try again.");
        }
    };

    // posts a new comment or reply, then appends it to the list
    const submitComment = async (content, parentId, clear) => {
        if (!isLoggedIn) {
            setActionError("Please log in to comment.");
            return;
        }
        if (!content.trim()) return;
        setActionError("");
        try {
            const res = await API.post(`/stories/${id}/comments`, {
                content: content.trim(),
                parent_id: parentId,
            });
            setComments((prev) => [...prev, res.data]);
            clear();
        } catch (err) {
            console.error(err);
            setActionError("Could not post comment. Please try again.");
        }
    };

    // deletes a comment the user owns or moderates
    const deleteComment = async (commentId) => {
        try {
            await API.delete(`/comments/${commentId}`);
            setComments((prev) => prev.filter((c) => c.id !== commentId));
        } catch (err) {
            console.error(err);
            setActionError("Could not delete comment.");
        }
    };

    const canDelete = (comment) =>
        currentUser &&
        (comment.user_id === currentUser.id ||
            currentUser.role === "admin" ||
            currentUser.role === "moderator");

    const formatDate = (value) => {
        const d = new Date(value);
        return Number.isNaN(d.getTime()) ? "" : d.toLocaleString();
    };

    if (!story) return <p className="container mt-4">Loading...</p>;

    // splits comments into top-level threads and their replies
    const topLevel = comments.filter((c) => !c.parent_id);
    const repliesOf = (parentId) =>
        comments.filter((c) => c.parent_id === parentId);

    const renderComment = (comment, isReply = false) => (
        <div
            key={comment.id}
            className={`comment ${isReply ? "comment-reply" : ""}`}
        >
            <div className="comment-head">
                <span className="comment-author">{comment.author_name}</span>
                <span className="comment-date">{formatDate(comment.created_at)}</span>
            </div>
            <p className="comment-body">{comment.content}</p>

            <div className="comment-actions">
                {isLoggedIn && !isReply && (
                    <button
                        type="button"
                        className="link-btn"
                        onClick={() =>
                            setReplyTo(replyTo === comment.id ? null : comment.id)
                        }
                    >
                        <i className="bi bi-reply"></i>
                        {replyTo === comment.id ? "Cancel" : "Reply"}
                    </button>
                )}
                {canDelete(comment) && (
                    <button
                        type="button"
                        className="link-btn danger"
                        onClick={() => deleteComment(comment.id)}
                    >
                        <i className="bi bi-trash"></i>
                        Delete
                    </button>
                )}
            </div>

            {/* inline reply form */}
            {replyTo === comment.id && (
                <form
                    className="reply-form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        submitComment(replyText, comment.id, () => {
                            setReplyText("");
                            setReplyTo(null);
                        });
                    }}
                >
                    <textarea
                        rows="2"
                        placeholder="Write a reply..."
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                    />
                    <button type="submit" className="btn-primary" disabled={!replyText.trim()}>
                        Reply
                    </button>
                </form>
            )}

            {/* one level of nested replies */}
            {repliesOf(comment.id).map((reply) => renderComment(reply, true))}
        </div>
    );

    return (
        <div>
            <Navbar />

            <div className="container mt-4 story-detail">
                <h2>{story.title}</h2>

                <p className="text-muted">Category: {story.category}</p>

                {/* IMAGE */}
                {story.image_url && (
                    <img
                        src={`http://127.0.0.1:8000/${story.image_url}`}
                        alt={story.title}
                        style={{
                            width: "100%",
                            maxHeight: "400px",
                            objectFit: "cover",
                            marginTop: "15px",
                        }}
                    />
                )}

                {/* AUDIO */}
                {story.audio_url && (
                    <audio controls style={{ width: "100%", marginTop: "15px" }}>
                        <source
                            src={`http://127.0.0.1:8000/${story.audio_url}`}
                            type="audio/mpeg"
                        />
                        Your browser does not support audio.
                    </audio>
                )}

                <p className="mt-3">{story.content}</p>

                {/* LIKE BAR */}
                <div className="like-bar">
                    <button
                        type="button"
                        className={`like-btn ${likes.liked ? "liked" : ""}`}
                        onClick={toggleLike}
                    >
                        <i className={`bi ${likes.liked ? "bi-heart-fill" : "bi-heart"}`}></i>
                        <span>{likes.liked ? "Liked" : "Like"}</span>
                    </button>
                    <span className="like-count">
                        {likes.count} {likes.count === 1 ? "like" : "likes"}
                    </span>
                </div>

                {actionError && <p className="text-danger mt-2">{actionError}</p>}

                {/* COMMENTS */}
                <section className="comments-section">
                    <h4>Comments ({comments.length})</h4>

                    {isLoggedIn ? (
                        <form
                            className="comment-form"
                            onSubmit={(e) => {
                                e.preventDefault();
                                submitComment(newComment, null, () => setNewComment(""));
                            }}
                        >
                            <textarea
                                rows="3"
                                placeholder="Share your thoughts..."
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                            />
                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={!newComment.trim()}
                            >
                                Post Comment
                            </button>
                        </form>
                    ) : (
                        <p className="login-hint">
                            <Link to="/login">Log in</Link> to like and comment.
                        </p>
                    )}

                    <div className="comment-list">
                        {topLevel.length === 0 ? (
                            <p className="no-comments">No comments yet. Be the first!</p>
                        ) : (
                            topLevel.map((comment) => renderComment(comment))
                        )}
                    </div>
                </section>
            </div>
        </div>
    );
}
