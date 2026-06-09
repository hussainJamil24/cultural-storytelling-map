import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import API from "../services/Api";
import Navbar from "../components/Navbar";
// import popup from '../assets/images/old-nicosia.jpg';

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

                {story.media_url && (
                    <img
                        src={story.media_url}
                        // src={story.media_url || popup}
                        alt="story"
                        style={{width:"100%", maxHeight:"400px", objectFit:"cover"}}
                    />
                )}

                <p className="mt-3">{story.content}</p>
            </div>
        </div>
    );
}