import React from "react";
import Header from "../Header/Header";
import Hero from "../Hero/Hero";
import Brands from "../Brands/Brands";
import "./LandingPage.css";
import { Bot } from "lucide-react";
import { useNavigate } from "react-router-dom";

function LandingPage(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Hero />

        <div className="chat-button-wrapper">
          <button className="btn btn-primary" onClick={() => navigate("/chat")}>
            <Bot className="bot-icon" style={{ width: 36, height: 36 }} />
            Start chatting with AI for recommendations!
          </button>
        </div>
        <Brands />
      </main>
    </div>
  );
}

export default LandingPage;
