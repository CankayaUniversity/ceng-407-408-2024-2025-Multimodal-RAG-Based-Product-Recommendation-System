import React from 'react';
import { Search, Camera, Bot } from 'lucide-react';
import { useNavigate } from "react-router-dom";
import './Header.css';

function Header(): React.ReactElement {
  const navigate = useNavigate();
  return (
    <header className="header">
      <div className="logo">Landing Page</div>
      <div className="search-container">
        <Bot className="bot-icon" onClick={() => navigate("/chat")} style={{ cursor: "pointer" }} />
        <div className="search-box">
          <Search className="search-icon" size={16} />
          <input type="text" placeholder="Search" className="search-input" />
        </div>
        <Camera className="camera-icon" size={20} />
      </div>
    </header>
  );
}

export default Header;