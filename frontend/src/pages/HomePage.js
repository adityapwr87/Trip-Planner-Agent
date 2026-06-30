import React, { useState, useEffect } from "react";
import api from "../utils/api";
import "./HomePage.css";

// Lucide icons
import { MapPin, ChevronRight, Play } from "lucide-react";

const TRENDING_CITIES = [
  "Paris",
  "New York",
  "Tokyo",
  "London",
  "Sydney",
  "Rome",
  "Dubai",
  "Bangkok",
  "Barcelona",
  "Singapore",
  "Los Angeles",
  "Istanbul",
  "Moscow",
  "Delhi",
  "Hong Kong",
];

function HomePage() {
  const [searchQuery, setSearchQuery] = useState("");

  const [location, setLocation] = useState({
    city: "Loading...",
    temp: "--",
    weather: "--",
  });
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);

  const openGoogleMaps = (place) => {
    if (place?.googleMapsUrl) {
      window.open(place.googleMapsUrl, "_blank", "noopener,noreferrer");
      return;
    }

    const query = [place?.title, location.city].filter(Boolean).join(", ");
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
      query || place?.title || location.city || "",
    )}`;
    window.open(mapsUrl, "_blank", "noopener,noreferrer");
  };

  const handlePlaceKeyDown = (event, place) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openGoogleMaps(place);
    }
  };

  // Fetch from our backend with caching
  const fetchPlaces = async (cityName, coords = null) => {
    const cacheKey = coords
      ? `places_cache_${cityName.toLowerCase()}_${coords.lat}_${coords.lon}`
      : `places_cache_${cityName.toLowerCase()}`;
    const cachedData = sessionStorage.getItem(cacheKey);

    if (cachedData) {
      // Use cached data instantly
      setPlaces(JSON.parse(cachedData));
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const params = { location: cityName };
      if (coords) {
        params.lat = coords.lat;
        params.lon = coords.lon;
      }
      const res = await api.get("/api/explore/places", { params });
      if (res.data && res.data.places) {
        setPlaces(res.data.places);
        // Store in session storage so it doesn't fetch again this session
        sessionStorage.setItem(cacheKey, JSON.stringify(res.data.places));
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  // Get current weather via Open-Meteo
  const fetchWeather = async (lat, lon, cityName) => {
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`,
      );
      const data = await res.json();

      const weatherCode = data.current_weather.weathercode;
      let weatherDesc = "clear sky";
      if (weatherCode > 1 && weatherCode <= 3) weatherDesc = "partly cloudy";
      else if (weatherCode > 3 && weatherCode < 50) weatherDesc = "cloudy";
      else if (weatherCode >= 50 && weatherCode < 70) weatherDesc = "rain";
      else if (weatherCode >= 70) weatherDesc = "snow";

      setLocation({
        city: cityName,
        temp: `${data.current_weather.temperature}°C`,
        weather: weatherDesc,
      });
    } catch (err) {
      console.error(err);
      setLocation({ city: cityName, temp: "--", weather: "--" });
    }
  };

  const applyFallback = () => {
    fetchPlaces("Delhi");
    setLocation({ city: "Delhi", temp: "--", weather: "--" });
  };

  // On mount, get geolocation -> wrap it -> fetch places
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            // Reverse geocoding via simple nominatim OpenStreetMap
            const revRes = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`,
            );
            const revData = await revRes.json();
            const city =
              revData.address.city ||
              revData.address.town ||
              revData.address.village ||
              revData.address.state ||
              "Local Area";

            fetchWeather(latitude, longitude, city);
            fetchPlaces(city, { lat: latitude, lon: longitude });
          } catch (error) {
            console.error("Reverse geocoding failed", error);
            applyFallback();
          }
        },
        (error) => {
          console.warn("Geolocation blocked", error);
          applyFallback();
        },
      );
    } else {
      applyFallback();
    }
  }, []);

  const searchCity = (targetCity) => {
    // Quick geocode to get weather for new city
    fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(targetCity)}&count=1`,
    )
      .then((res) => res.json())
      .then((data) => {
        if (data.results && data.results.length > 0) {
          const { latitude, longitude, name } = data.results[0];
          fetchWeather(latitude, longitude, name);
          fetchPlaces(name, { lat: latitude, lon: longitude });
        } else {
          fetchPlaces(targetCity);
          setLocation({ city: targetCity, temp: "--", weather: "--" });
        }
      })
      .catch(() => {
        fetchPlaces(targetCity);
        setLocation({ city: targetCity, temp: "--", weather: "--" });
      });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    searchCity(searchQuery);
  };

  const handlePillClick = (city) => {
    setSearchQuery(city);
    searchCity(city);
  };

  return (
    <>
      <header className="main-header">
        <div className="header-top">
          <h1>Ready for your next adventure, Explorer?</h1>
          {location.city !== "Loading..." && (
            <div className="weather-badge">
              <MapPin size={16} className="weather-icon" /> 
              <span className="weather-city">{location.city}</span>
              <span className="weather-divider">|</span>
              <span className="weather-desc">{location.temp} • {location.weather}</span>
            </div>
          )}
        </div>
      </header>

      <section className="trending-section">
        <div className="section-header">
          <h2>Trending Destinations</h2>
          <button className="view-all-btn">
            View all <ChevronRight size={16} />
          </button>
        </div>

        <form className="search-bar" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Type a city (e.g. Jaipur) and press Enter"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="search-btn">
            Search
          </button>
        </form>

        <div className="city-pills">
          {TRENDING_CITIES.map((city) => (
            <span
              key={city}
              className="city-pill"
              onClick={() => handlePillClick(city)}
            >
              {city}
            </span>
          ))}
        </div>
      </section>

      <section className="places-section">
        <h2>Nearby Places to Explore</h2>

        {loading ? (
          <div className="loading-spinner">Discovering places...</div>
        ) : (
          <div className="places-grid">
            {places.map((place, idx) => (
              <div
                key={idx}
                className="place-card"
                role="button"
                tabIndex={0}
                onClick={() => openGoogleMaps(place)}
                onKeyDown={(event) => handlePlaceKeyDown(event, place)}
                title={`Open ${place.title} in Google Maps`}
              >
                <div className="image-wrapper">
                  <img src={place.image} alt={place.title} />
                  {idx === 0 && (
                    <div className="play-button">
                      <Play size={24} fill="white" color="white" />
                    </div>
                  )}
                </div>
                <div className="place-info">
                  <h3>{place.title}</h3>
                  <p>
                    <MapPin size={14} /> {place.distance || "Nearby"}
                  </p>
                  {place.rating && <span className="place-rating">★ {place.rating}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

export default HomePage;
