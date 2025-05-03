import React, { useState, useRef, useEffect } from "react";
import { Search, Camera, User } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import "./Header.css";

function Header(): React.ReactElement {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/");
    window.location.reload();
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(event.target as Node)
    ) {
      setDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="header">
      <div className="logo" onClick={() => navigate("/")}>
        Fashion
      </div>

      <div className="header-center"></div>

      <div className="auth-buttons">
        {username ? (
          <div className="user-menu" ref={dropdownRef}>
            <div
              className="user-info"
              onClick={() => setDropdownOpen(!dropdownOpen)}>
              <User size={20} />
              <span className="user-username">{username}</span>
            </div>
            {dropdownOpen && (
              <div className="dropdown-menu">
                <button onClick={() => navigate("/settings")}>Settings</button>
                <button onClick={handleLogout}>Logout</button>
              </div>
            )}
          </div>
        ) : (
          <>
            <Link to="/login" className="auth-button">
              Sign In
            </Link>
            <Link to="/register" className="auth-button">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </header>
  );
}

export default Header;
