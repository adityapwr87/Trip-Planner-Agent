import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Calendar, Bot, Scale, ArrowRight } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  // Simple scroll-to-top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="landing-wrapper">
      {/* Navbar */}
      <nav className="landing-nav">
        <div className="landing-brand">
          <Plane size={32} className="brand-icon" />
          <span>Trip Planner AI</span>
        </div>
        <div className="landing-auth-buttons">
          <button className="btn-login" onClick={() => navigate('/login')}>Log In</button>
          <button className="btn-signup" onClick={() => navigate('/signup')}>Sign Up</button>
        </div>
      </nav>

      <main className="landing-main">
        {/* Hero Section */}
        <section className="landing-hero fade-in-up">
          <h1>Your Ultimate <span className="gradient-text">AI Travel Agent</span></h1>
          <p>
            Stop spending hours researching. Chat with our intelligent travel agents to generate detailed, day-by-day itineraries tailored exactly to your preferences. 
          </p>
          <button className="btn-cta" onClick={() => navigate('/signup')}>
            Start Planning for Free <ArrowRight size={20} />
          </button>
        </section>

        {/* Core Features Grid */}
        <section className="landing-features">
          <div className="feature-card glass">
            <div className="icon-wrapper blue"><Bot size={32} /></div>
            <h3>Conversational Planning</h3>
            <p>Just tell our AI where you want to go. It will ask follow-up questions to nail down your budget, vibe, and schedule.</p>
          </div>
          <div className="feature-card glass">
            <div className="icon-wrapper purple"><Scale size={32} /></div>
            <h3>Compare Destinations</h3>
            <p>Can't decide between Bali or Phuket? Compare cost, weather, and attractions side-by-side.</p>
          </div>
          <div className="feature-card glass">
            <div className="icon-wrapper pink"><Calendar size={32} /></div>
            <h3>Detailed Itineraries</h3>
            <p>Get a beautiful day-by-day breakdown with interactive maps, activities, and logistics all planned out.</p>
          </div>
        </section>

        {/* CTA Section */}
        <section className="landing-bottom-cta">
          <h2>Ready for your next adventure?</h2>
          <p>Join thousands of travelers planning smarter, not harder.</p>
          <button className="btn-cta large" onClick={() => navigate('/signup')}>
            Create Your Itinerary
          </button>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="landing-footer">
        <p>&copy; {new Date().getFullYear()} Trip Planner AI. All rights reserved.</p>
      </footer>
      
      {/* Decorative Background Elements */}
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>
    </div>
  );
}
