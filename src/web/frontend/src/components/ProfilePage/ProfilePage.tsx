import React from "react";
import "./ProfilePage.css";
import Header from "../Header/Header";

const ProfilePage: React.FC = () => {
  return (
    <div className="profile-page">
      <Header />
      <div className="profile-content-wrapper">
        <aside className="profile-sidebar">
          <nav>
            <ul>
              <li>
                <a href="#">Profile</a>
              </li>
              <li>
                <a href="#">Favorites</a>
              </li>
              <li>
                <a href="#">Past Searches</a>
              </li>
              <li>
                <a href="#">Preferences</a>
              </li>
              <li>
                <a href="#">Trending</a>
              </li>
              <li>
                <a href="#">Upload History</a>
              </li>
            </ul>
          </nav>
        </aside>
        <main className="profile-content">
          <section className="profile-section">
            <h2>Profile Picture</h2>
            <img
              src="https://via.placeholder.com/150"
              alt="Profile"
              className="profile-picture"
            />
            <input type="file" />
          </section>
          <section className="profile-section">
            <h2>Save your favorites</h2>
            <p>Any products you favorite will appear here</p>
            <a href="#" className="see-all-link">
              See all →
            </a>
          </section>
          <section className="profile-section">
            <h2>View your past searches</h2>
            <p>We'll show you the products you've searched for.</p>
            <a href="#" className="see-all-link">
              See all →
            </a>
          </section>
          <section className="profile-section">
            <h2>Manage your preferences</h2>
            <p>
              Want to see more of the things you love? Tell us what you're
              interested in
            </p>
            <a href="#" className="manage-preferences-link">
              Manage preferences →
            </a>
          </section>
          <section className="profile-section">
            <h2>Last Viewed Products</h2>
            <div className="last-viewed-products">
              <div className="product-card">
                <img src="https://via.placeholder.com/200x250" alt="Product" />
                <p className="product-title">The Perfect White Shirt</p>
                <p className="product-viewed-date">Viewed in 25.05.2024</p>
              </div>
              <div className="product-card">
                <img src="https://via.placeholder.com/200x250" alt="Product" />
                <p className="product-title">Summer Party Looks</p>
                <p className="product-viewed-date">Viewed in 25.05.2024</p>
              </div>
              <div className="product-card">
                <img src="https://via.placeholder.com/200x250" alt="Product" />
                <p className="product-title">Best Sunscreen</p>
                <p className="product-viewed-date">Viewed in 25.05.2024</p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default ProfilePage;
