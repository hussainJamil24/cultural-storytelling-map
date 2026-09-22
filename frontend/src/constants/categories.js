import L from "leaflet";

// single source of truth for category labels, colors and icons.
// the map, sidebar, story page and upload form all read from here.
export const CATEGORIES = [
    { key: "heritage", label: "Heritage", icon: "bi-journal-bookmark", color: "#007bff" },
    { key: "landmarks", label: "Landmarks", icon: "bi-bank2", color: "#d64545" },
    { key: "oral_history", label: "Oral Histories", icon: "bi-mic-fill", color: "#2e9e5b" },
    { key: "customs", label: "Customs", icon: "bi-stars", color: "#e0a325" },
    { key: "migration", label: "Migration", icon: "bi-globe", color: "#7c5cbf" },
    { key: "religion", label: "Religion", icon: "bi-book", color: "#4a5578" },
    { key: "music", label: "Music", icon: "bi-music-note-beamed", color: "#c2559a" },
    { key: "food", label: "Food", icon: "bi-cup-hot-fill", color: "#e2703a" },
];

const FALLBACK = { key: "heritage", label: "Story", icon: "bi-geo-alt-fill", color: "#007bff" };

export const getCategory = (key) =>
    CATEGORIES.find((category) => category.key === key) || FALLBACK;

export const getCategoryLabel = (key) => getCategory(key).label;
export const getCategoryColor = (key) => getCategory(key).color;

// teardrop pin drawn inline so markers never depend on an external image host
const pinSvg = (color) => `
<svg class="map-pin-shape" viewBox="0 0 32 42" width="32" height="42" aria-hidden="true">
  <path d="M16 0C7.163 0 0 7.163 0 16c0 11 16 26 16 26s16-15 16-26C32 7.163 24.837 0 16 0z"
        fill="${color}" stroke="#ffffff" stroke-width="2"/>
</svg>`;

// builds the leaflet marker icon for a story category
export const getMarkerIcon = (categoryKey) => {
    const { color, icon } = getCategory(categoryKey);

    return L.divIcon({
        className: "map-pin-wrapper",
        html: `<div class="map-pin">${pinSvg(color)}<i class="bi ${icon}"></i></div>`,
        iconSize: [32, 42],
        iconAnchor: [16, 42],
        popupAnchor: [0, -38],
    });
};
