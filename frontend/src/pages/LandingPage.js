import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Compass, Map, Calendar } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-wrapper">
      <nav className="landing-nav">
        <div className="landing-brand">
          <Plane size={28} />
          <span>Fleet</span>
        </div>
        <div className="landing-auth-buttons">
          <button className="btn-login" onClick={() => navigate('/login')}>Log In</button>
          <button className="btn-signup" onClick={() => navigate('/signup')}>Sign Up</button>
        </div>
      </nav>

      <main className="landing-main">
        <div className="landing-hero">
          <h1>Your Ultimate AI Trip Planner</h1>
          <p>
            Discover new destinations, generate personalized itineraries instantly, 
            and chat with your personal AI travel assistant to perfect every detail of your trip.
          </p>
          <button className="btn-cta" onClick={() => navigate('/signup')}>
            Start Planning for Free
          </button>
        </div>

        <div className="landing-features">
          <div className="feature-card">
            <Compass size={40} />
            <h3>Discover</h3>
            <p>Find nearby attractions, trending cities, and hidden gems.</p>
          </div>
          <div className="feature-card">
            <Calendar size={40} />
            <h3>Plan</h3>
            <p>Generate detailed daily itineraries tailored to your preferences.</p>
          </div>
          <div className="feature-card">
            <Map size={40} />
            <h3>Navigate</h3>
            <p>Direct integration with Google Maps to guide your journey.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
