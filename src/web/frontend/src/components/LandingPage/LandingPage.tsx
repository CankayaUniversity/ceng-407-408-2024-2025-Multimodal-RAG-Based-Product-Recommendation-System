import React from "react";
import Header from "../Header/Header";
import Hero from "../Hero/Hero";
import Brands from "../Brands/Brands";
import "./LandingPage.css";
import { Bot, Search, Sparkles, Shirt, Zap, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";

function LandingPage(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Hero />

        <div className="chat-button-wrapper animate-fade-in-up">
          <button className="btn btn-primary" onClick={() => navigate("/chat")}>
            <Bot className="bot-icon" style={{ width: 28, height: 28 }} />
            Start chatting with AI for recommendations!
          </button>
        </div>

        <section className="section-container animate-fade-in-up animate-delay-1">
          <div className="section-header">
            <h2 className="section-title">Find Your Perfect Style</h2>
            <p className="section-description">
              Discover fashion recommendations tailored to your personal taste. Our AI-powered solution helps you find the perfect outfit for any occasion.
            </p>
          </div>
          
          <div className="features-section">
            <div className="feature-card animate-fade-in-up animate-delay-1">
              <div className="feature-icon">
                <Sparkles size={24} />
              </div>
              <h3 className="feature-title">AI-Powered Recommendations</h3>
              <p className="feature-description">
                Get personalized style suggestions based on your preferences and the latest fashion trends.
              </p>
            </div>
            
            <div className="feature-card animate-fade-in-up animate-delay-2">
              <div className="feature-icon">
                <Search size={24} />
              </div>
              <h3 className="feature-title">Visual Search</h3>
              <p className="feature-description">
                Upload an image of an outfit you like, and we'll find similar or complementary pieces.
              </p>
            </div>
            
            <div className="feature-card animate-fade-in-up animate-delay-3">
              <div className="feature-icon">
                <Shirt size={24} />
              </div>
              <h3 className="feature-title">Virtual Try-On</h3>
              <p className="feature-description">
                See how clothes would look on you with our virtual try-on feature before making a purchase.
              </p>
            </div>
          </div>
        </section>

        <section className="section-container">
          <div className="section-header animate-fade-in-up animate-delay-2">
            <h2 className="section-title">Latest Fashion Trends</h2>
            <p className="section-description">
              Stay updated with the most recent styles and fashion trends from around the world.
            </p>
          </div>
          <Brands />
        </section>

        <section className="section-container animate-fade-in-up animate-delay-3">
          <div className="section-header">
            <h2 className="section-title">Start Your Fashion Journey</h2>
            <p className="section-description">
              Get personalized recommendations by chatting with our AI assistant or browse the latest trends.
            </p>
            <div className="chat-button-wrapper" style={{ marginTop: "30px" }}>
              <button className="btn btn-primary" onClick={() => navigate("/chat")}>
                <MessageSquare size={20} />
                Chat with Fashion AI
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LandingPage;
