import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ProfilePreferences.css";

const preferencesData = {
  "Clothing Items": [
    "Dress",
    "Jacket",
    "Jeans",
    "Skirt",
    "Hoodie",
    "T-shirt",
    "Sneakers",
    "Boots",
    "Blazer",
    "Coat",
    "Jumpsuit",
    "Crop Top",
  ],
  Styles: [
    "Casual",
    "Formal",
    "Sporty",
    "Streetwear",
    "Chic",
    "Boho",
    "Minimalist",
    "Vintage",
    "Y2K",
    "Preppy",
    "Grunge",
  ],
  Colors: [
    "Black",
    "White",
    "Beige",
    "Pastel",
    "Red",
    "Emerald Green",
    "Navy Blue",
    "Neon",
    "Earth Tones",
    "Monochrome",
  ],
  Seasons: [
    "Summer",
    "Winter",
    "Spring",
    "Fall",
    "Rainwear",
    "Beachwear",
    "Layering",
  ],
  Materials: [
    "Denim",
    "Cotton",
    "Wool",
    "Silk",
    "Linen",
    "Leather",
    "Faux Fur",
    "Knit",
  ],
  "Fits & Cuts": [
    "Oversized",
    "Cropped",
    "High-waisted",
    "Ripped",
    "Pleated",
    "Flared",
    "Asymmetrical",
    "Sheer",
    "Cut-out",
    "Sustainable",
  ],
  Demographics: ["Men's", "Women's", "Unisex", "Kids", "Plus Size", "Petite"],
};

const ProfilePreferences: React.FC = () => {
  const [selected, setSelected] = useState<string[]>([]);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const userEmail = localStorage.getItem("email");

  // Fetch saved preferences on component mount
  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const response = await fetch("http://localhost:3001/api/get_keywords", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ email: userEmail }),
        });

        if (!response.ok) {
          throw new Error("Failed to fetch preferences");
        }

        const result = await response.json();
        setSelected(result.preferences || []);
      } catch (error) {
        console.error("Error loading preferences:", error);
      }
    };

    fetchPreferences();
  }, []);

  const togglePreference = (pref: string) => {
    setSelected((prev) =>
      prev.includes(pref) ? prev.filter((p) => p !== pref) : [...prev, pref]
    );
  };

  const removePreference = (pref: string) => {
    setSelected((prev) => prev.filter((p) => p !== pref));
  };

  const handleSave = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/save_keywords", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          email: userEmail,
          preferences: selected,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to save preferences");
      }

      alert("Preferences saved successfully!");
      console.log("Saved preferences:", selected);
    } catch (error) {
      console.error("Save failed:", error);
      alert("Error saving preferences.");
    }
  };

  return (
    <div className="container">
      <div className="header">
        <button className="back-link" onClick={() => navigate("/profile")}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round">
            <path d="M15 18L9 12l6-6" />
          </svg>
          Back to Profile
        </button>
      </div>

      <h1>Fashion Preferences</h1>
      <p className="description">
        Select the fashion categories you're interested in to personalize your
        experience.
      </p>

      <div className="preferences-container">
        {Object.entries(preferencesData).map(([category, items]) => (
          <div key={category} className="category">
            <h2>{category}</h2>
            <div className="pills">
              {items.map((item) => (
                <button
                  key={item}
                  className={`pill ${
                    selected.includes(item) ? "selected" : ""
                  }`}
                  onClick={() => togglePreference(item)}>
                  {item}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="summary">
        <h3>Selected Preferences ({selected.length})</h3>
        <div className="selected-pills">
          {selected.length === 0 ? (
            <p className="empty-message">No preferences selected yet</p>
          ) : (
            selected.map((pref) => (
              <div key={pref} className="selected-pill">
                {pref}
                <span
                  className="remove-preference"
                  onClick={() => removePreference(pref)}>
                  ×
                </span>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="save-button-container">
        <button id="save-button" onClick={handleSave}>
          Save Preferences
        </button>
      </div>
    </div>
  );
};

export default ProfilePreferences;
