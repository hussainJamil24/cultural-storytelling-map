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
        anonymous: false,
        images:null,
        audio:null,
        location: null,
    });

    // disables submit until the required text and location are filled
    const btnDisable =
    formData.title === "" || formData.narrative === ""  ||formData.location == null ;
    
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
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    // stores selected files even though uploads are currently disabled
    const handleFileChange = (e, fieldName) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: e.target.files
        }));
    };

    // submits the story payload to the backend api
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (formData.images || formData.audio) {
                alert("Media file upload is coming soon. For now, submit text and location only.");
                return;
            }

            const payload = {
                title: formData.title.trim(),
                content: formData.narrative.trim(),
                media_url: null,
                latitude: formData.location?.lat,
                longitude: formData.location?.lng,
            };

            const res = await API.post("/stories", payload, {
                headers: {
                    "Content-Type": "application/json",
                },
            });

            console.log("SUCCESS:", res.data);
            alert("Story submitted successfully and is now pending review.");
            setFormData({
                title: '',
                narrative: '',
                anonymous: false,
                images: null,
                audio: null,
                location: null,
            });
            setPosition(null);

        } catch(err) {
            console.error(err);
            alert("Upload failed");
        }


        // console.log('Form submitted:', formData);
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

                    {/* shows the placeholder media upload boxes */}
                    <div className="upload-boxes">
                        {/* shows the disabled image upload field */}
                        <div className="upload-box text-center">
                            <input type="file" id="images-input" multiple accept="image/*"
                            disabled
                            onChange={(e)=> handleFileChange(e, 'images')}
                            />
                            <label htmlFor="images-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-image"></i>
                                </div>
                                <h6>Upload Images</h6>
                                <p className='fw-lighter'>Media upload coming soon</p>
                            </label>
                        </div>

                        {/* shows the disabled audio upload field */}
                        <div className="upload-box text-center">
                            <input type="file" id="audio-input" accept="audio/*"
                            disabled
                            onChange={(e)=> handleFileChange(e, 'audio')}
                            />
                            <label htmlFor="audio-input" className="upload-label d-flex flex-column align-items-center gap-1 text-uppercase m-0 fw-medium">
                                <div className="upload-icon d-flex align-items-center justify-content-center">
                                    <i className="bi bi-mic"></i>
                                </div>
                                <h6>Add Oral History</h6>
                                <p className='fw-lighter'>Media upload coming soon</p>
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

                    {/* lets the user submit anonymously */}
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

                    {/* submits the story once required fields are complete */}
                    <div className="form-section submit-section d-flex justify-content-center mt-5">
                        <button type="submit" id="submit-btn" className= "main-btn rounded-pill" 
                            disabled={btnDisable}
                        >
                            SUBMIT STORY
                        </button>
                    </div>
                </form>
            </div>

            {/* shows the closing page quote */}
            <div className="story-footer text-center fst-italic fw-lighter">
                <p>"We are the stories we tell." — The Curator</p>
            </div>
        </div>
    );
}
