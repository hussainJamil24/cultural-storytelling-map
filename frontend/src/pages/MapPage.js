import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapPage() {
    const CyprusCenter = [35.1264, 33.4299];
    const bounds = [
        [34.5, 32.0], // Southwest
        [35.7, 34.8], // Northeast
    ];
    return (
        <MapContainer center={[35.18, 33.38]} zoom={10} style={{ height: "90vh" }}>
            <TileLayer
            center = {CyprusCenter}
            zoom= {9}
            maxBounds={bounds}
            maxBoundsViscosity={1.0}
            style={{ height: "90vh", width: "100%" }}
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={[35.1856, 33.3823]}>
                <Popup>Nicosia Story</Popup>
            </Marker>
        </MapContainer>
    );
}