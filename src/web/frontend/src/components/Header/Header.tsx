import React, { useState, useRef, useEffect } from "react";
import { Search, Menu, X, Home, UserCircle, MessageCircle } from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import "./Header.css";

function Header(): React.ReactElement {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState<string | null>(localStorage.getItem("username") || null);
  const [email, setEmail] = useState<string | null>(localStorage.getItem("email") || null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem("token"));
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check authentication status whenever route changes
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
    setUsername(localStorage.getItem("username") || email?.split('@')[0] || null);
    setEmail(localStorage.getItem("email") || null);
  }, [location.pathname, email]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    setIsAuthenticated(false);
    setUsername(null);
    setEmail(null);
    setDropdownOpen(false);
    navigate("/");
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(event.target as Node)
    ) {
      setDropdownOpen(false);
    }
    
    if (
      mobileMenuRef.current &&
      !mobileMenuRef.current.contains(event.target as Node) &&
      !(event.target as HTMLElement).classList.contains('mobile-menu-toggle')
    ) {
      setMobileMenuOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Navigation items
  const navItems = [
    { name: "Home", path: "/", icon: <Home size={18} /> },
    { name: "Dashboard", path: "/dashboard", icon: <Home size={18} />, authRequired: true },
    { name: "Chat", path: "/chat", icon: <MessageCircle size={18} />, authRequired: true }
  ];

  // Filter nav items based on authentication status
  const filteredNavItems = navItems.filter(item => 
    !item.authRequired || (item.authRequired && isAuthenticated)
  );

  return (
    <header className="header">
      <div className="logo" onClick={() => navigate("/")}>
        Fashion<span className="logo-accent">AI</span>
      </div>

      {/* Desktop Navigation */}
      <nav className="desktop-nav">
        <ul className="nav-links">
          {filteredNavItems.map((item) => (
            <li key={item.path}>
              <Link 
                to={item.path} 
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.icon}
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="header-right">
        {/* Search Icon */}
        <button 
          className="search-button" 
          onClick={() => navigate("/search")}
          aria-label="Search"
        >
          <Search size={20} />
        </button>

        {/* Auth Buttons or User Menu */}
        {isAuthenticated ? (
          <div className="user-menu" ref={dropdownRef}>
            <div
              className="user-info"
              onClick={() => setDropdownOpen(!dropdownOpen)}>
              <UserCircle size={24} />
              <span className="user-username">{username}</span>
            </div>
            {dropdownOpen && (
              <div className="dropdown-menu">
                <Link to="/dashboard" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                  <Home size={16} />
                  Dashboard
                </Link>
                <Link to="/profile" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                  <UserCircle size={16} />
                  Profile
                </Link>
                <div className="dropdown-divider"></div>
                <button onClick={handleLogout} className="dropdown-item logout">
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <>
            <Link to="/login" className="auth-button">
              Sign In
            </Link>
            <Link to="/register" className="auth-button register">
              Sign Up
            </Link>
          </>
        )}

        {/* Mobile Menu Toggle */}
        <button 
          className="mobile-menu-toggle" 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation Menu */}
      {mobileMenuOpen && (
        <div className="mobile-menu" ref={mobileMenuRef}>
          <ul className="mobile-nav-links">
            {filteredNavItems.map((item) => (
              <li key={item.path}>
                <Link 
                  to={item.path} 
                  className={`mobile-nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.icon}
                  {item.name}
                </Link>
              </li>
            ))}
            {isAuthenticated && (
              <>
                <li className="mobile-divider"></li>
                <li>
                  <Link 
                    to="/profile" 
                    className="mobile-nav-link"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <UserCircle size={18} />
                    Profile
                  </Link>
                </li>
                <li>
                  <button 
                    className="mobile-nav-link logout"
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                  >
                    Logout
                  </button>
                </li>
              </>
            )}
          </ul>
        </div>
      )}
    </header>
  );
}

export default Header;
