import { MapContainer, TileLayer, Marker, useMapEvents  } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useState } from "react";
import API from "../services/api";
import Navbar from '../components/Navbar';
import '../assets/styles/uploadstory.css';

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
    iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
    iconUrl: require("leaflet/dist/images/marker-icon.png"),
    shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

// Component to handle map clicks
function LocationMarker({ setPosition, onSelectLocation  }) {
    useMapEvents({
        click(e) {
            const coords = {
                lat: e.latlng.lat,
                lng: e.latlng.lng
            };

            setPosition([coords.lat, coords.lng]);   // show marker
            onSelectLocation(coords); // save to formData
        },
    });
    return null;
}

export default function Upload() {
    const [position, setPosition] = useState(null);
    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // Southwest
        [35.7, 34.8], // Northeast
    ];

    const [formData, setFormData] = useState({
        title:'',
        narrative:'',
        anonymous: false,
        images:null,
        audio:null,
        location: null,
    });

    const btnDisable =
    formData.title === "" || formData.narrative === ""  ||formData.location == null ;
    
    const handleLocationSelect = (coords) => {
    setFormData(prev => ({
        ...prev,
        location: coords
    }));
};

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleFileChange = (e, fieldName) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: e.target.files
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const form = new FormData();

            form.append("title", formData.title);
            form.append("narrative", formData.narrative);

             // location
            form.append("lat", formData.location?.lat);
            form.append("lng", formData.location?.lng);

            // files
            if (formData.images) {
            form.append("image", formData.images[0]); // first image
            }

            if (formData.audio) {
            form.append("audio", formData.audio[0]);
            }

            const res = await API.post("/stories", form, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            console.log("SUCCESS:", res.data);
            alert("Story uploaded successfully");

        } catch(err) {
            console.error(err);
            alert("Upload failed");
        }


        // console.log('Form submitted:', formData);
    };

    return (
        <div className="upload-story-container bg-light">
            {/* Navbar */}
            <Navbar/>

            {/* Header */}
            <div className="story-header text-center mt-5">
                <h1 className='fw-bolder mb-3'>Share a Fragment of History</h1>
                <p className='fw-lighter m-0'>Pin your story to the living map of our collective heritage.</p>
            </div>

            {/* Main Form */}
            <div className="story-card">
                <form onSubmit={handleSubmit}>
                    {/* Story Title */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium '>Story Title</label>
                        <input type='text' name='title' className='form-control p-3'
                        placeholder='Enter a memorable name for your story'
                        value={formData.title} onChange={handleInputChange}
                        />
                    </div>

                    {/* The Narrative */}
                    <div className="form-section">
                        <label className='form-label d-block text-uppercase mb-2 fw-medium'>The narrative</label>
                        <textarea type='text' name='narrative' className='form-control textarea-large p-3' rows="6"
                        placeholder='Describe the memory, the event, or the significance of this place....'
                        value={formData.narrative} onChange={handleInputChange}
                        >
                        </textarea>
                    </div>

                    {/* Upload Boxes */}
                    <div className="upload-boxes">
                        {/* Upload Images */}
                        <div className="upload-box text-center">
                            <input type="file" id="images-input" multiple accept="image/*"
                            onChange={(e)=> handleFileChange(e, 'images')}
                            />
                            <label htmlFor="images-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-image"></i>
                                </div>
                                <h6>Upload Images</h6>
                                <p className='fw-lighter'>PNG, JPG up to 10MB</p>
                            </label>
                        </div>

                        {/* Add Oral History */}
                        <div className="upload-box text-center">
                            <input type="file" id="audio-input" accept="audio/*"
                            onChange={(e)=> handleFileChange(e, 'audio')}
                            />
                            <label htmlFor="audio-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-mic"></i>
                                </div>
                                <h6>Add Oral History</h6>
                                <p className='fw-lighter'>MP3, WAV up to 20MB</p>
                            </label>
                        </div>
                    </div>

                    {/* Geographic Anchor */}
                    <div className="form-section">
                        <label className="form-label d-block text-uppercase mb-2 fw-medium">Geographic Anchor</label>
                        <div className="map-wrapper">
                            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
                            zoomControl={false} // disable default
                            style={{height: "180px", borderRadius:"15px" }}
                            >
                                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>

                                {/* Detect click */}
                                <LocationMarker setPosition={setPosition} 
                                    onSelectLocation={handleLocationSelect} 
                                />

                                {/* Show marker ONLY if user clicked */}
                                {position && <Marker position={position} />}

                                {/* Zoom on right */}
                                <ZoomControl position="topright"/>
                            </MapContainer>

                            <div className="map-overlay d-flex gap-1">
                                <i className="bi bi-geo-alt-fill"></i>
                                <p className="fw-medium">Click to pinpoint location</p>
                            </div>
                        </div>
                    </div>

                    {/* Anonymous Checkbox */}
                    <div className="form-section checkbox-section">
                        <div className="form-check d-flex align-items-center gap-2">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="anonymous"
                                name="anonymous"
                                checked={formData.anonymous} onChange={handleInputChange}
                            />
                            <label className="form-check-label fw-medium" htmlFor="anonymous">
                                Post story anonymously
                            </label>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="form-section submit-section d-flex justify-content-center mt-5">
                        <button type="submit" id="submit-btn" className= "main-btn rounded-pill" 
                            disabled={btnDisable}
                        >
                            SUBMIT STORY
                        </button>
                    </div>
                </form>
            </div>

            {/* Footer Quote */}
            <div className="story-footer text-center fst-italic fw-lighter">
                <p>"We are the stories we tell." — The Curator</p>
            </div>
        </div>
    );
}
