import ReactMarkdown from "react-markdown";
import {
  BedDouble,
  CalendarDays,
  CloudSun,
  Compass,
  MapPinned,
  Plane,
  Route,
  Sparkles,
  Wallet,
  Users,
} from "lucide-react";
import "./TripResult.css";

function TripResult({ result }) {
  if (!result) {
    return (
      <div className="result-empty">
        <Sparkles size={26} />
        <p>Your generated itinerary, route, weather, activities, and stay suggestions will appear here.</p>
      </div>
    );
  }

  const state = result.state || {};
  const weatherDays = state.weather_data?.data || [];
  const routes = state.route_options || [];
  const activities = state.activities || [];
  const hotels = state.hotel_suggestions || [];

  return (
    <div className="trip-result">
      <section className="result-hero">
        <div>
          <p className="eyebrow">Generated Trip</p>
          <h2>{state.destination ? `${state.destination} Itinerary` : "Trip Itinerary"}</h2>
          <div className="trip-meta">
            <span>
              <MapPinned size={15} />
              {state.source || "Source"} to {state.destination || "Destination"}
            </span>
            <span>
              <CalendarDays size={15} />
              {state.start_date || "Start"} - {state.end_date || "End"}
            </span>
            <span>
              <Users size={15} />
              {state.travelers || "-"} travellers
            </span>
            <span>
              <Wallet size={15} />
              {state.budget || "Budget"}
            </span>
          </div>
        </div>
      </section>

      <ResultSection title="Itinerary" icon={<Compass size={18} />}>
        <div className="markdown-panel">
          <ReactMarkdown>{state.itinerary || result.response || "No itinerary returned."}</ReactMarkdown>
        </div>
      </ResultSection>

      <ResultSection title="Route Options" icon={<Route size={18} />}>
        {routes.length ? (
          <div className="result-grid">
            {routes.slice(0, 6).map((route, index) => (
              <InfoCard
                key={`${route.mode}-${index}`}
                title={route.route_name || route.title || route.mode || `Route ${index + 1}`}
                subtitle={route.provider || route.airline || "Transport option"}
                icon={<Plane size={17} />}
                rows={[
                  ["Mode", route.mode],
                  ["Duration", route.duration_text || formatHours(route.duration_hours)],
                  ["Distance", route.distance_km ? `${route.distance_km} km` : null],
                  ["Cost", route.price || route.estimated_cost],
                ]}
              />
            ))}
          </div>
        ) : (
          <EmptySection text="No route options returned." />
        )}
      </ResultSection>

      <ResultSection title="Weather" icon={<CloudSun size={18} />}>
        {weatherDays.length ? (
          <div className="weather-strip">
            {weatherDays.map((day) => (
              <div className="weather-card" key={day.date}>
                <strong>{day.date}</strong>
                <span>{day.climate}</span>
                <small>
                  {day.min_temp}°C - {day.max_temp}°C
                </small>
                <small>Rain: {day.rain_chance}%</small>
              </div>
            ))}
          </div>
        ) : (
          <EmptySection text={state.weather_message || "No weather data returned."} />
        )}
      </ResultSection>

      <ResultSection title="Activities" icon={<Sparkles size={18} />}>
        {activities.length ? (
          <div className="result-grid">
            {activities.slice(0, 8).map((activity, index) => (
              <InfoCard
                key={`${activity.name}-${index}`}
                title={activity.name || `Activity ${index + 1}`}
                subtitle={activity.category || activity.location_hint}
                icon={<Sparkles size={17} />}
                rows={[
                  ["Best time", activity.best_time],
                  ["Duration", activity.duration_hours ? `${activity.duration_hours} hrs` : null],
                  ["Cost", activity.estimated_cost],
                  ["Weather", activity.weather_suitability],
                ]}
              >
                {activity.description && <p>{activity.description}</p>}
              </InfoCard>
            ))}
          </div>
        ) : (
          <EmptySection text="No activities returned." />
        )}
      </ResultSection>

      <ResultSection title="Accommodation" icon={<BedDouble size={18} />}>
        {hotels.length ? (
          <div className="result-grid">
            {hotels.slice(0, 6).map((hotel, index) => (
              <InfoCard
                key={`${hotel.name}-${index}`}
                title={hotel.name || `Stay ${index + 1}`}
                subtitle={hotel.category || hotel.city}
                icon={<BedDouble size={17} />}
                rows={[
                  ["Area", hotel.address || hotel.area_or_address],
                  ["City", hotel.city],
                  ["Price", hotel.estimated_price || hotel.price_total],
                  ["Availability", hotel.availability],
                ]}
              />
            ))}
          </div>
        ) : (
          <EmptySection text="No accommodation options returned." />
        )}
      </ResultSection>

      <details className="state-details">
        <summary>Everything else returned by backend</summary>
        <pre>{JSON.stringify(state, null, 2)}</pre>
      </details>
    </div>
  );
}

function ResultSection({ title, icon, children }) {
  return (
    <section className="result-section">
      <div className="result-section-title">
        {icon}
        <h3>{title}</h3>
      </div>
      {children}
    </section>
  );
}

function InfoCard({ title, subtitle, icon, rows, children }) {
  const visibleRows = rows.filter(([, value]) => value !== undefined && value !== null && value !== "");

  return (
    <article className="info-card">
      <div className="info-card-head">
        <div className="info-icon">{icon}</div>
        <div>
          <h4>{title}</h4>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>
      {children}
      {visibleRows.length > 0 && (
        <dl>
          {visibleRows.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{String(value)}</dd>
            </div>
          ))}
        </dl>
      )}
    </article>
  );
}

function EmptySection({ text }) {
  return <p className="empty-section">{text}</p>;
}

function formatHours(hours) {
  if (!hours) return null;
  return `${hours} hrs`;
}

export default TripResult;
