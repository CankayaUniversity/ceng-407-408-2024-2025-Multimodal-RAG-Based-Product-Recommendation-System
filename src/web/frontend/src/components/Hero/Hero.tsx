import { useNavigate } from "react-router-dom";
import React from "react";
import "./Hero.css";
import { ArrowRight, ShoppingBag } from "lucide-react";

function Hero(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <section className="hero-section">
      <div className="hero-image-container">
        <img
          src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2070&auto=format&fit=crop"
          alt="Fashion style showcase"
          className="hero-image"
        />
        <div className="hero-overlay">
          <div className="hero-content">
            <p className="hero-subtitle">AI-Powered Style Assistant</p>
            <h1 className="hero-title">Discover Your Perfect Style Match</h1>
            <p className="hero-description">
              Let our innovative AI technology guide you to find the perfect fashion pieces that match your style, preferences, and the latest trends.
            </p>
            <div className="hero-buttons">
              <button 
                className="btn btn-primary" 
                onClick={() => navigate("/chat")}
              >
                Get Personalized Recommendations
                <ArrowRight size={18} />
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => document.querySelector('.brands-section')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Explore Trends
                <ShoppingBag size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
