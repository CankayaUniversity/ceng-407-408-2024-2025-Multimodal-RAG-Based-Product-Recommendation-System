import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import "./ProfilePage.css";
import Header from "../Header/Header";
import axios from "axios";

interface PhotoResponse {
  photo_data?: string;
  content_type?: string;
  photo_url?: string;
  message?: string;
}

const ProfilePage: React.FC = () => {
  const [profilePhoto, setProfilePhoto] = useState<string>("https://via.placeholder.com/150");
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const userEmail = localStorage.getItem('email');

  useEffect(() => {
    if (userEmail) {
      fetchProfilePhoto();
    }
  }, [userEmail]);

  const fetchProfilePhoto = async () => {
    try {
      const response = await axios.get<PhotoResponse>(`http://localhost:3001/api/get-profile-photo?email=${userEmail}`);
      if (response.data.photo_data && response.data.content_type) {
        // Construct data URL from base64 data and content type
        const dataUrl = `data:${response.data.content_type};base64,${response.data.photo_data}`;
        setProfilePhoto(dataUrl);
      } else if (response.data.photo_url) {
        setProfilePhoto(response.data.photo_url);
      }
    } catch (error: any) {
      console.error('Error fetching profile photo:', error);
    }
  };

  const handlePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid image file (JPEG, PNG, or GIF)');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size should be less than 5MB');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('photo', file);

    try {
      console.log('Uploading photo for email:', userEmail);
      const response = await axios.post<PhotoResponse>('http://localhost:3001/api/upload-photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-User-Email': userEmail
        },
      });
      console.log('Upload response:', response.data);
      
      // Fetch the updated photo after successful upload
      await fetchProfilePhoto();
    } catch (error: any) {
      console.error('Error uploading photo:', error);
      if (error.response) {
        console.error('Error details:', error.response.data);
      }
      alert('Failed to upload photo. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const triggerFileInput = () => {
    if (!userEmail) {
      alert('Please log in to upload a profile photo');
      return;
    }
    fileInputRef.current?.click();
  };

  return (
    <div className="profile-page">
      <Header />
      <div className="profile-content-wrapper">
        <aside className="profile-sidebar">
          <nav>
            <ul>
              <li><Link to="/profile">Profile</Link></li>
              <li><Link to="/profile/past-recommendations">Past Recommendations</Link></li>
              <li><Link to="/profile/preferences">Preferences</Link></li>
            </ul>
          </nav>
        </aside>
        <main className="profile-content">
          <section className="profile-section">
            <h2>Profile Picture</h2>
            <div className="profile-photo-container">
              <img
                src={profilePhoto}
                alt="Profile"
                className="profile-picture"
              />
              <div className="profile-photo-overlay" onClick={triggerFileInput}>
                <span>Change Photo</span>
              </div>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handlePhotoUpload}
              accept="image/*"
              style={{ display: 'none' }}
            />
            {isUploading && <p className="upload-status">Uploading...</p>}
          </section>

          <section className="profile-section">
            <h2>View your past searches</h2>
            <p>We'll show you the products you've searched for.</p>
            <Link to="/profile/past-searches" className="see-all-link">See all →</Link>
          </section>

          <section className="profile-section">
            <h2>Manage your preferences</h2>
            <p>Want to see more of the things you love? Tell us what you're interested in</p>
            <Link to="/profile/preferences" className="manage-preferences-link">Manage preferences →</Link>
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




