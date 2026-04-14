import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { ZoomControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import '../assets/styles/mapview.css';

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

            {/* Map */}
            <MapContainer center={CyprusCenter} zoom={9}  maxBounds={bounds} maxBoundsViscosity={1.0}
            zoomControl={false} // disable default
            style={{ height: "100vh" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
                <Marker position={[35.1856, 33.3823]}>
                    <Popup>Nicosia Story</Popup>
                </Marker>

                {/* Zoom on right */}
                <ZoomControl position="topright" />
            </MapContainer>
        </div>
    );
}