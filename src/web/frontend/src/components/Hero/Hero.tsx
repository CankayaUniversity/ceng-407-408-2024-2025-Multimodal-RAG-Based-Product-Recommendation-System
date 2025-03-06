import { useNavigate } from "react-router-dom";
import React from "react";
import "./Hero.css";

function Hero(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <section className="hero-section">
      <div className="hero-image-container">
        <img
          src="https://placehold.co/1200x400"
          alt="Fashion model"
          className="hero-image"
        />
        <div className="hero-overlay">
          <h1 className="hero-title">Find the perfect style match</h1>
          <div className="hero-buttons"></div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
