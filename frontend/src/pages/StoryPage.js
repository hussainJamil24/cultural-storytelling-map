import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import API from "../services/Api";
import Navbar from "../components/Navbar";

export default function StoryPage() {
    const {id} = useParams();
    const [story, setStory] = useState(null);

    useEffect(()=> {
        const fetchStory = async ()=> {
            try{
                const res = await API.get(`/stories/${id}`);
                setStory(res.data);
                console.log(res.data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchStory();
    },[id]);

    if(!story) return <p>Loading...</p>;
    
    return(
        <div>
            <Navbar />

            <div className="container mt-4">
                <h2>{story.title}</h2>

                <p className="text-muted">
                    Category: {story.category}
                </p>

                    {/* IMAGE */}
                    {story.image_url && (
                        <img
                            src={`http://127.0.0.1:8000/${story.image_url}`}
                            alt={story.title}
                            style={{
                                width: "100%",
                                maxHeight: "400px",
                                objectFit: "cover",
                                marginTop: "15px"
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
            </div>
        </div>
    );
}