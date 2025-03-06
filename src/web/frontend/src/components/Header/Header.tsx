import React from 'react';
import { Search, Camera } from 'lucide-react';
import './Header.css';

function Header(): React.ReactElement {
  return (
    <header className="header">
      <div className="logo">Landing Page</div>
      <div className="search-container">
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