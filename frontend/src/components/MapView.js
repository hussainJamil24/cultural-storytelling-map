import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import '../assets/styles/mapview.css';
import popup from'../assets/images/old-nicosia.jpg'

export default function MapView() {
    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // Southwest
        [35.7, 34.8], // Northeast
    ];
    return (
        <div className="map-container">
            {/* Search Bar */}
            <div className="map-search">
                <input
                    type="text"
                    placeholder="Search location..."
                    className="form-control shadow"
                />
            </div>

            {/* Upload Button */}
            <div className="map-upload-btn">
                <Link to="/upload" className="upload-btn mt-auto">
                    <i className="bi bi-plus-lg"></i>
                    Upload Story
                </Link>
            </div>

            {/* Map */}
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false} // disable default
            style={{ height: "100vh" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
                <Marker position={[35.1856, 33.3823]}>
                    <Popup className="custom-popup">
                        <div className="popup-card">
                            {/* Image */}
                            <div className="popup-image">
                                <img 
                                    src={popup} 
                                    alt="story" 
                                />
                            </div>

                            {/* Content */}
                            <div className="popup-content">
                                <h5>The golden heart of the city</h5>

                                <p>
                                An elevated, sun-drenched view of Nicosia's historic quarter, where the weathered 
                                stone of an ancient church spire stands in quiet contrast to 
                                the sprawling urban horizon of the divided capital.
                                </p>

                                {/* Audio */}
                                <audio controls className="w-100">
                                    <source src="" />
                                </audio>

                                {/* Button */}
                                <Link to={`/story/1`} className="popup-btn">
                                    View Full Story
                                </Link>
                            </div>
                        </div>
                    </Popup>
                </Marker>

                {/* Zoom on right */}
                <ZoomControl position="topright" />
            </MapContainer>
        </div>
    );
}