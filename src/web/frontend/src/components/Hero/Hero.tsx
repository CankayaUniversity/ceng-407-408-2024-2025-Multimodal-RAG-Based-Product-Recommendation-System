import { useNavigate } from "react-router-dom";
import React from "react";
import "./Hero.css";

function Hero(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <section className="hero-section">
      <div className="hero-image-container">
        <img
          src="https://r.fashionunited.com/5JF18OUXEkW2rGLscgPUTi8r69burUbgcaTQeI_JC-M/resize:fit:1200:630:0/gravity:ce/quality:70/aHR0cHM6Ly9mYXNoaW9udW5pdGVkLmNvbS9pbWcvdXBsb2FkLzIwMjEvMTIvMTcvZGlvci13bWVwcTAxeS0yMDIxLTEyLTE3LmpwZWc.jpeg"
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
