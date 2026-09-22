import { useEffect, useState } from "react";
import "../assets/styles/ailoader.css";

// shared "AI is working" indicator used everywhere a Gemini call is in flight:
// companion card generation, story translation, and moderation assist during
// submit. cycles through short status messages so a multi-second wait feels
// purposeful instead of a static spinner.
export default function AiLoader({ messages, size = "md", inline = false }) {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        if (!messages || messages.length < 2) return undefined;

        const interval = setInterval(() => {
            setIndex((i) => (i + 1) % messages.length);
        }, 1900);

        return () => clearInterval(interval);
    }, [messages]);

    const activeMessage = messages?.[index];

    if (inline) {
        return (
            <span className="ai-loader ai-loader-inline">
                <span className="ai-loader-ring ai-loader-ring-sm">
                    <i className="bi bi-stars"></i>
                </span>
                {activeMessage && (
                    <span className="ai-loader-text" key={index}>
                        {activeMessage}
                    </span>
                )}
            </span>
        );
    }

    return (
        <div className={`ai-loader ai-loader-${size}`}>
            <span className="ai-loader-ring">
                <i className="bi bi-stars"></i>
            </span>
            {activeMessage && (
                <p className="ai-loader-text" key={index}>
                    {activeMessage}
                </p>
            )}
        </div>
    );
}
