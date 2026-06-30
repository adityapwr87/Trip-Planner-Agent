import { CalendarClock, Map, MessageSquarePlus } from "lucide-react";
import { Link } from "react-router-dom";
import "./PastTripsPage.css";

function PastTripsPage({ sessions }) {
  return (
    <section className="past-trips-page">
      <div className="past-trips-header">
        <div>
          <p className="eyebrow">Trip History</p>
          <h2>Past Trips</h2>
          <p>Open a previous planning session and continue from where you left off.</p>
        </div>
        <Link to="/plan/new" className="past-trip-new">
          <MessageSquarePlus size={18} />
          New Trip
        </Link>
      </div>

      {sessions.length === 0 ? (
        <div className="past-trips-empty">
          <Map size={34} />
          <h3>No saved trips yet</h3>
          <p>Your planned trips will appear here after you start chatting.</p>
          <Link to="/plan/new">Plan your first trip</Link>
        </div>
      ) : (
        <div className="past-trips-grid">
          {sessions.map((session) => (
            <Link
              key={session.session_id}
              className="past-trip-card"
              to={`/plan/${session.session_id}`}
            >
              <div className="past-trip-icon">
                <Map size={20} />
              </div>
              <div>
                <h3>{session.title || "New Trip"}</h3>
                <p>
                  <CalendarClock size={15} />
                  Continue planning session
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}

export default PastTripsPage;
