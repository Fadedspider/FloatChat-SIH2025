import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix leaflet default icon issues with webpack:
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

export default function FloatMap({ floats }) {
  const defaultPosition = [0, 0]; // Equator center for map start view

  return (
    <MapContainer
      center={defaultPosition}
      zoom={2}
      style={{ height: "400px", width: "100%", borderRadius: "8px" }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {floats.map((float) =>
        float.avg_lat && float.avg_lon ? (
          <Marker
            key={float.id || float.float_id}
            position={[float.avg_lat, float.avg_lon]}
          >
            <Popup>
              Float ID: {float.id || float.float_id}
              <br />
              Location: [{float.avg_lat.toFixed(2)}, {float.avg_lon.toFixed(2)}]
            </Popup>
          </Marker>
        ) : null
      )}
    </MapContainer>
  );
}
