import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import API, { mediaUrl } from "../services/Api";
import Navbar from "../components/Navbar";
import AiLoader from "../components/AiLoader";
import { getCategory } from "../constants/categories";
import "../assets/styles/storypage.css";

// order requested: Greek, Turkish, English. "en" is the original submitted
// text -- no API call needed, it's just the story as written.
const LANGUAGES = [
    { code: "el", label: "Ελληνικά", flag: "🇬🇷" },
    { code: "tr", label: "Türkçe", flag: "🇹🇷" },
    { code: "en", label: "English", flag: "🇬🇧" },
];

const TRANSLATING_MESSAGES = {
    el: [
        "Reading the original story…",
        "Translating into Ελληνικά…",
        "Preserving the tone and meaning…",
    ],
    tr: [
        "Reading the original story…",
        "Translating into Türkçe…",
        "Preserving the tone and meaning…",
    ],
};

export default function StoryPage() {
    const { id } = useParams();
    const [story, setStory] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState("");

    // likes state for this story
    const [likes, setLikes] = useState({ count: 0, liked: false });

    // comments state
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState("");
    const [replyTo, setReplyTo] = useState(null);
    const [replyText, setReplyText] = useState("");
    const [actionError, setActionError] = useState("");
    const [isPosting, setIsPosting] = useState(false);

    // current signed-in user (null when logged out)
    const currentUser = JSON.parse(localStorage.getItem("user") || "null");
    const isLoggedIn = Boolean(localStorage.getItem("access_token") && currentUser);

    // AI translation: "en" is the original text, plus a cache of any languages
    // fetched so far so switching back and forth never re-calls the API
    const [activeLang, setActiveLang] = useState("en");
    const [translations, setTranslations] = useState({});
    const [translating, setTranslating] = useState(false);
    const [translationError, setTranslationError] = useState("");
    // null while unknown, so buttons stay enabled-looking until we actually know
    const [aiConfigured, setAiConfigured] = useState(true);

    useEffect(() => {
        API.get("/ai/status")
            .then((res) => setAiConfigured(Boolean(res.data.configured)))
            .catch(() => setAiConfigured(true)); // don't block the toggle on a status-check hiccup
    }, []);

    const selectLanguage = async (code) => {
        setTranslationError("");
        if (code === "en" || translations[code]) {
            setActiveLang(code);
            return;
        }

        if (!aiConfigured) {
            // known-unavailable -- skip the round trip and show a calm note instead of an error
            setTranslationError("AI translation is coming soon for this story.");
            return;
        }

        setTranslating(true);
        setActiveLang(code);
        try {
            const res = await API.get(`/stories/${id}/translate/${code}`);
            setTranslations((prev) => ({ ...prev, [code]: res.data }));
        } catch (err) {
            setActiveLang("en");
            setTranslationError(
                err?.response?.status === 503
                    ? "AI translation is coming soon for this story."
                    : "Couldn't translate this story right now. Please try again."
            );
        } finally {
            setTranslating(false);
        }
    };

    useEffect(() => {
        const fetchStory = async () => {
            setIsLoading(true);
            setLoadError("");
            try {
                const res = await API.get(`/stories/${id}`);
                setStory(res.data);
            } catch (err) {
                setLoadError(
                    err?.response?.status === 404
                        ? "This story doesn't exist, or it hasn't been approved yet."
                        : "We couldn't load this story. Please try again."
                );
            } finally {
                setIsLoading(false);
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
        setIsPosting(true);
        try {
            const res = await API.post(`/stories/${id}/comments`, {
                content: content.trim(),
                parent_id: parentId,
            });
            setComments((prev) => [...prev, res.data]);
            clear();
        } catch (err) {
            setActionError("Could not post comment. Please try again.");
        } finally {
            setIsPosting(false);
        }
    };

    // deletes a comment the user owns or moderates
    const deleteComment = async (commentId) => {
        try {
            await API.delete(`/comments/${commentId}`);
            setComments((prev) => prev.filter((c) => c.id !== commentId));
        } catch (err) {
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
        if (Number.isNaN(d.getTime())) return "";
        return d.toLocaleDateString(undefined, {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    };

    const initialOf = (name) => name?.trim()?.charAt(0)?.toUpperCase() || "?";

    // loading skeleton keeps the page shape while data arrives
    if (isLoading) {
        return (
            <div>
                <Navbar />
                <div className="story-shell">
                    <div className="skeleton" style={{ height: 18, width: 120 }} />
                    <div className="skeleton" style={{ height: 38, marginTop: 20 }} />
                    <div
                        className="skeleton"
                        style={{ height: 18, width: "40%", marginTop: 12 }}
                    />
                    <div
                        className="skeleton"
                        style={{ height: 320, marginTop: 24, borderRadius: 22 }}
                    />
                    <div className="skeleton" style={{ height: 14, marginTop: 24 }} />
                    <div className="skeleton" style={{ height: 14, marginTop: 10 }} />
                    <div
                        className="skeleton"
                        style={{ height: 14, width: "70%", marginTop: 10 }}
                    />
                </div>
            </div>
        );
    }

    if (loadError || !story) {
        return (
            <div>
                <Navbar />
                <div className="story-shell">
                    <div className="story-error">
                        <i className="bi bi-compass"></i>
                        <h3>Story not found</h3>
                        <p>{loadError}</p>
                        <Link to="/map" className="story-error-btn">
                            Back to the map
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    const category = getCategory(story.category);
    const image = mediaUrl(story.image_url);
    const audio = mediaUrl(story.audio_url);

    // splits comments into top-level threads and their replies
    const topLevel = comments.filter((c) => !c.parent_id);
    const repliesOf = (parentId) => comments.filter((c) => c.parent_id === parentId);

    const renderComment = (comment, isReply = false) => (
        <div key={comment.id} className={`comment ${isReply ? "comment-reply" : ""}`}>
            <div className="comment-head">
                <span className="comment-avatar">{initialOf(comment.author_name)}</span>
                <div>
                    <span className="comment-author">{comment.author_name}</span>
                    <span className="comment-date">{formatDate(comment.created_at)}</span>
                </div>
            </div>

            <p className="comment-body">{comment.content}</p>

            <div className="comment-actions">
                {isLoggedIn && !isReply && (
                    <button
                        type="button"
                        className="link-btn"
                        onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}
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
                        placeholder="Write a reply…"
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

            <article className="story-shell story-detail">
                <Link to="/map" className="story-back">
                    <i className="bi bi-arrow-left"></i>
                    Back to map
                </Link>

                <header className="story-header">
                    <div className="story-header-top">
                        <span className="cat-chip" style={{ background: category.color }}>
                            <i className={`bi ${category.icon}`}></i>
                            {category.label}
                        </span>

                        <div className="lang-toggle">
                            {LANGUAGES.map((lang) => (
                                <button
                                    key={lang.code}
                                    type="button"
                                    className={
                                        activeLang === lang.code
                                            ? lang.code === "en"
                                                ? "active"
                                                : "active active-ai"
                                            : ""
                                    }
                                    onClick={() => selectLanguage(lang.code)}
                                    disabled={translating}
                                >
                                    <span className="lang-flag">{lang.flag}</span>
                                    {lang.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <h1>{translations[activeLang]?.title ?? story.title}</h1>

                    {activeLang !== "en" && translations[activeLang] && !translating && (
                        <p className="lang-note">
                            <i className="bi bi-stars"></i>
                            Translated by AI — the original text is the source of truth.
                        </p>
                    )}

                    {translationError && (
                        <div
                            className={`notice ${aiConfigured ? "notice-error" : "notice-empty"}`}
                            style={{ marginTop: 10 }}
                        >
                            <i
                                className={`bi ${
                                    aiConfigured
                                        ? "bi-exclamation-circle-fill"
                                        : "bi-stars"
                                }`}
                            ></i>
                            {translationError}
                        </div>
                    )}

                    <div className="story-meta">
                        <span>
                            <i className="bi bi-person-circle"></i>
                            {story.is_anonymous ? "Shared anonymously" : "Community story"}
                        </span>
                        <span>
                            <i className="bi bi-calendar3"></i>
                            {formatDate(story.created_at)}
                        </span>
                        <span>
                            <i className="bi bi-geo-alt"></i>
                            {Number(story.latitude).toFixed(3)},{" "}
                            {Number(story.longitude).toFixed(3)}
                        </span>
                    </div>
                </header>

                {image && (
                    <figure className="story-hero">
                        <img src={image} alt={story.title} />
                    </figure>
                )}

                {audio && (
                    <div className="story-audio">
                        <div className="story-audio-label">
                            <i className="bi bi-mic-fill"></i>
                            Listen to this story
                        </div>
                        <audio controls src={audio}>
                            Your browser does not support audio.
                        </audio>
                    </div>
                )}

                <div className={`story-body ${translating ? "story-body-loading" : ""}`}>
                    {translating ? (
                        <div className="story-translate-panel">
                            <AiLoader messages={TRANSLATING_MESSAGES[activeLang]} />
                        </div>
                    ) : (
                        (translations[activeLang]?.content ?? story.content)
                            .split(/\n\s*\n/)
                            .filter(Boolean)
                            .map((paragraph, index) => <p key={index}>{paragraph}</p>)
                    )}
                </div>

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
                        {likes.count} {likes.count === 1 ? "person appreciates" : "people appreciate"} this story
                    </span>
                </div>

                {actionError && (
                    <div className="notice notice-error" style={{ marginTop: 14 }}>
                        <i className="bi bi-exclamation-circle-fill"></i>
                        {actionError}
                    </div>
                )}

                {/* COMMENTS */}
                <section className="comments-section">
                    <h4>
                        Comments <span className="comment-count">{comments.length}</span>
                    </h4>

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
                                placeholder="Share your thoughts…"
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                            />
                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={!newComment.trim() || isPosting}
                            >
                                {isPosting ? "Posting…" : "Post Comment"}
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
            </article>
        </div>
    );
}
