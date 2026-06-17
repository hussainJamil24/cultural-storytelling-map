import { MapContainer, TileLayer, Marker, useMapEvents  } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useState } from "react";
import API from "../services/Api";
import Navbar from '../components/Navbar';
import '../assets/styles/uploadstory.css';

// restores leaflet marker image paths inside the react build
delete L.Icon.Default.prototype._getIconUrl;

// configures the default leaflet marker assets
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
    iconUrl: require("leaflet/dist/images/marker-icon.png"),
    shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

// captures map clicks and sends the selected coordinates to the form
function LocationMarker({ setPosition, onSelectLocation  }) {
    useMapEvents({
        click(e) {
            const coords = {
                lat: e.latlng.lat,
                lng: e.latlng.lng
            };

            setPosition([coords.lat, coords.lng]);   // shows the marker on the map
            onSelectLocation(coords); // saves the coordinates into the form state
        },
    });
    return null;
}

// renders the story upload form and location picker
export default function Upload() {
    // tracks the marker position selected on the map
    const [position, setPosition] = useState(null);

    // centers the picker map on cyprus and keeps panning inside island bounds
    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // southwest map limit
        [35.7, 34.8], // northeast map limit
    ];

    // stores the story form values before submission
    const [formData, setFormData] = useState({
        title:'',
        narrative:'',
        location: null,
        category: "",
    });

    const [companionCard, setCompanionCard] = useState(null);
    const [selectedImages, setSelectedImages] = useState([]);
    const [selectedAudio, setSelectedAudio] = useState(null);
    const [mediaInputKey, setMediaInputKey] = useState(0);
    const [submitting, setSubmitting] = useState(false);
    const [loadingAI, setLoadingAI] = useState(false);

    // disables submit until the required text and location are filled
    const btnDisable =
        submitting ||
        formData.title.trim() === "" ||
        formData.narrative.trim() === "" ||
        formData.location == null ||
        formData.category === "";

    const aiDisabled =
        loadingAI ||
        formData.title.trim() === "" ||
        formData.narrative.trim() === "" ||
        formData.category === "";

    // saves the selected map coordinates into the form data
    const handleLocationSelect = (coords) => {
        setFormData(prev => ({
            ...prev,
            location: coords
        }));
    };

    // updates text fields and checkbox values
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setCompanionCard(null);
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleMediaChange = (e) => {
        const { name, files } = e.target;
        const selectedFiles = Array.from(files || []);

        if (name === "images") {
            setSelectedImages(selectedFiles);
        }

        if (name === "audio") {
            setSelectedAudio(selectedFiles[0] || null);
        }
    };

    const uploadSelectedMedia = async () => {
        const file = selectedImages[0] || selectedAudio;
        if (!file) {
            return null;
        }

        const data = new FormData();
        data.append("file", file);

        const res = await API.post("/upload-image", data, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        console.log("UPLOAD RESPONSE:", res.data);

        return res.data.url;
    };

    // submits the story payload to the backend api
    const handleSubmit = async (e) => {
        e.preventDefault();
        // setSubmitting(true);
        
        try {
            const media_url = await uploadSelectedMedia();

            const payload = {
                title: formData.title.trim(),
                content: formData.narrative.trim(),
                media_url: media_url,
                latitude: formData.location?.lat,
                longitude: formData.location?.lng,
                category: formData.category,
            };

            console.log("mediaUrl:", media_url);

            const res = await API.post("/stories", payload);

            console.log("SUCCESS:", res.data);
            alert("Story submitted successfully and is now pending review.");

            setFormData({
                title: '',
                narrative: '',
                location: null,
                category: "",
            });

            setPosition(null);
            setCompanionCard(null);
            setSelectedImages([]);
            setSelectedAudio(null);
            setMediaInputKey((key) => key + 1);

        } catch(err) {
            console.error(err);
            const message = err.response?.data?.detail || "Upload failed";
            alert(message);
        } finally {
            setSubmitting(false);
        }

        
    };

    const handleGenerateAI = async () => {
        if (aiDisabled) {
            alert("Add a title, narrative, and category before generating the companion card.");
            return;
        }

        setLoadingAI(true);

        try {
            const res = await API.post("/ai/generate-companion-card", {
                title: formData.title.trim(),
                content: formData.narrative.trim(),
                category: formData.category,
            });

            console.log(res.data);
            setCompanionCard(res.data);

        } catch (err) {
            console.error(err);
            const message =
                err.response?.data?.detail || err.message || "Failed to generate companion card";
            alert(message);
        } finally {
            setLoadingAI(false);
        }
    };

    return (
        <div className="upload-story-container bg-light">
            {/* shows the shared site navigation */}
            <Navbar/>

            {/* introduces the upload page */}
            <div className="story-header text-center mt-5">
                <h1 className='fw-bolder mb-3'>Share a Fragment of History</h1>
                <p className='fw-lighter m-0'>Pin your story to the living map of our collective heritage.</p>
            </div>

            {/* contains the story submission form */}
            <div className="story-card">
                <form onSubmit={handleSubmit}>
                    {/* collects the story title */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium '>Story Title</label>
                        <input type='text' name='title' className='form-control p-3'
                        placeholder='Enter a memorable name for your story'
                        value={formData.title} onChange={handleInputChange}
                        />
                    </div>

                    {/* collects the main story narrative */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium'>The narrative</label>
                        <textarea type='text' name='narrative' className='form-control textarea-large p-3' rows="6"
                        placeholder='Describe the memory, the event, or the significance of this place....'
                        value={formData.narrative} onChange={handleInputChange}
                        >
                        </textarea>
                    </div>

                    {/* lets the user select a story category */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium'>
                            Category
                        </label>
                        <select name="category" className="form-control p-3"
                        value={formData.category}
                        onChange={handleInputChange}
                        >
                            <option value="">Select category</option>
                            <option value="heritage">Heritage</option>
                            <option value="landmarks">Landmarks</option>
                            <option value="oral_history">Oral Histories</option>
                            <option value="customs">Customs</option>
                            <option value="migration">Migration</option>
                            <option value="religion">Religion</option>
                            <option value="music">Music</option>
                            <option value="food">Food</option>
                        </select>
                    </div>

                    {/* shows the media upload fields */}
                    <div className="upload-boxes">
                        {/* shows the image upload field */}
                        <div className="upload-box text-center">
                            <input
                                key={`images-${mediaInputKey}`}
                                type="file"
                                id="images-input"
                                name="images"
                                multiple
                                accept="image/*"
                                onChange={handleMediaChange}
                            />
                            <label htmlFor="images-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-image"></i>
                                </div>
                                <h6>Upload Images</h6>
                                <p className='fw-lighter'>
                                    {selectedImages.length > 0
                                        ? `${selectedImages.length} image${selectedImages.length === 1 ? "" : "s"} ready to upload`
                                        : "Select images to upload with this story"}
                                </p>
                            </label>
                        </div>

                        {/* shows the audio upload field */}
                        <div className="upload-box text-center">
                            <input
                                key={`audio-${mediaInputKey}`}
                                type="file"
                                id="audio-input"
                                name="audio"
                                accept="audio/*"
                                onChange={handleMediaChange}
                            />
                            <label htmlFor="audio-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-mic"></i>
                                </div>
                                <h6>Add Oral History</h6>
                                <p className='fw-lighter'>
                                    {selectedAudio
                                        ? `${selectedAudio.name} ready to upload`
                                        : "Select audio to upload with this story"}
                                </p>
                            </label>
                        </div>
                    </div>

                    {/* lets the user choose a map location */}
                    <div className="form-section">
                        <label className="form-label d-block text-uppercase mb-2 fw-medium">Geographic Anchor</label>
                        <div className="map-wrapper">
                            {/* renders the picker map with a custom zoom control placement */}
                            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
                            zoomControl={false}
                            style={{height: "180px", borderRadius:"15px" }}
                            >
                                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

                                {/* listens for clicks and updates the selected coordinates */}
                                <LocationMarker setPosition={setPosition}
                                    onSelectLocation={handleLocationSelect}
                                />

                                {/* shows a marker only after a location is selected */}
                                {position && <Marker position={position} />}

                                {/* shows zoom controls on the right side of the map */}
                                <ZoomControl position="topright"/>
                            </MapContainer>

                            {/* explains how to choose a location */}
                            <div className="map-overlay d-flex gap-1">
                                <i className="bi bi-geo-alt-fill"></i>
                                <p className="fw-medium">Click to pinpoint location</p>
                            </div>
                        </div>
                    </div>

                    {/* submits the story once required fields are complete */}
                    <div className="form-section submit-section d-flex justify-content-center mt-5 gap-2">
                        <button type="submit" id="submit-btn" className= "main-btn rounded-pill"
                            disabled={btnDisable}
                        >
                            {submitting ? "SAVING..." : "SUBMIT STORY"}
                        </button>

                        <button type="button" className= "main-btn rounded-pill" id="ai-btn"
                            onClick={handleGenerateAI}
                            disabled={aiDisabled}
                        >
                            {loadingAI ? (
                                "Generating..."
                            ) : (
                                <><i className="bi bi-stars"></i> Generate Companion Card</>
                            )}
                        </button>

                    </div>

                    {loadingAI && (
                        <p className="text-primary mt-2">
                            Preparing companion card...
                        </p>
                    )}

                    {companionCard && (
                        <div className="ai-companion-panel">
                            <h5>Companion Card</h5>

                            <p className="ai-companion-summary">{companionCard.short_summary}</p>

                            <div className="ai-companion-tags">
                                {companionCard.themes.map((theme) => (
                                    <span key={theme}>{theme}</span>
                                ))}
                            </div>

                            <div className="ai-companion-section">
                                <h6>Timeline</h6>
                                <ol>
                                    {companionCard.timeline.map((item) => (
                                        <li key={item}>{item}</li>
                                    ))}
                                </ol>
                            </div>

                            <div className="ai-companion-section">
                                <h6>Cultural Value</h6>
                                <p>{companionCard.cultural_value}</p>
                            </div>

                            <p className="ai-companion-note">{companionCard.respect_note}</p>
                            <p className="ai-companion-note">{companionCard.safety_notice}</p>
                        </div>
                    )}
                </form>
            </div>

            {/* shows the closing page quote */}
            <div className="story-footer text-center fst-italic fw-lighter">
                <p>"We are the stories we tell." — The Curator</p>
            </div>
        </div>
    );
}
