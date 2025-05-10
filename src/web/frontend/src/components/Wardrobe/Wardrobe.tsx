import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../Header/Header";
import { 
  Plus, Trash2, Filter, Grid, List, Upload, Search, X, CheckCircle, Shirt, Scissors 
} from "lucide-react";
import Button from "../ui/Button";
import SearchOutfit from "./SearchOutfit";
import "./Wardrobe.css";

// Define wardrobe item type
interface WardrobeItem {
  id: string;
  category: string;
  color: string;
  style: string;
  season: string[];
  occasions: string[];
  image_url: string;
  product_name: string;
  custom_name: string | null;
  added_at: string;
}

// Filter type
interface Filters {
  category: string;
  color: string;
  season: string;
  occasion: string;
}

const Wardrobe: React.FC = () => {
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    category: "",
    color: "",
    season: "",
    occasion: ""
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  // Categories, colors, seasons, and occasions for filters and form
  const categories = [
    "Tops", "Bottoms", "Dresses", "Outerwear", "Footwear", 
    "Accessories", "Activewear", "Swimwear", "Formal Wear"
  ];
  
  const colors = [
    "Black", "White", "Red", "Blue", "Green", "Yellow", "Purple", 
    "Pink", "Orange", "Brown", "Grey", "Navy", "Beige", "Multicolor"
  ];
  
  const seasons = ["Spring", "Summer", "Fall", "Winter"];
  
  const occasions = [
    "Casual", "Formal", "Business", "Party", "Workout", 
    "Beach", "Outdoor", "Special Occasion"
  ];

  // Form state for adding new item
  const [newItem, setNewItem] = useState({
    category: "",
    color: "",
    style: "",
    season: [] as string[],
    occasions: [] as string[],
    image_url: "",
    product_name: "",
    custom_name: ""
  });
  
  // State for file upload
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login", { state: { from: "/wardrobe" } });
      return;
    }

    // Fetch wardrobe items
    const fetchWardrobeItems = async () => {
      try {
        const response = await fetch("http://localhost:3001/api/profile/wardrobe", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch wardrobe items");
        }

        const data = await response.json();
        setItems(data.data || []);
        setLoading(false);
      } catch (err) {
        setError("Failed to load wardrobe items. Please try again later.");
        setLoading(false);
        console.error("Error fetching wardrobe:", err);
      }
    };

    fetchWardrobeItems();
  }, [navigate]);

  // Filter items based on selected filters and search query
  const filteredItems = items.filter(item => {
    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch = 
        (item.product_name && item.product_name.toLowerCase().includes(query)) ||
        (item.custom_name && item.custom_name.toLowerCase().includes(query)) ||
        (item.category && item.category.toLowerCase().includes(query)) ||
        (item.color && item.color.toLowerCase().includes(query));
        
      if (!matchesSearch) return false;
    }
    
    // Apply category filter
    if (filters.category && item.category !== filters.category) return false;
    
    // Apply color filter
    if (filters.color && item.color !== filters.color) return false;
    
    // Apply season filter
    if (filters.season && !item.season.includes(filters.season)) return false;
    
    // Apply occasion filter
    if (filters.occasion && !item.occasions.includes(filters.occasion)) return false;
    
    return true;
  });

  // Handle file upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Toggle season selection in new item form
  const toggleSeason = (season: string) => {
    if (newItem.season.includes(season)) {
      setNewItem({
        ...newItem,
        season: newItem.season.filter(s => s !== season)
      });
    } else {
      setNewItem({
        ...newItem,
        season: [...newItem.season, season]
      });
    }
  };

  // Toggle occasion selection in new item form
  const toggleOccasion = (occasion: string) => {
    if (newItem.occasions.includes(occasion)) {
      setNewItem({
        ...newItem,
        occasions: newItem.occasions.filter(o => o !== occasion)
      });
    } else {
      setNewItem({
        ...newItem,
        occasions: [...newItem.occasions, occasion]
      });
    }
  };

  // Handle adding new item
  const handleAddItem = async () => {
    setUploadStatus("uploading");
    const token = localStorage.getItem("token");
    
    // Validate required fields
    if (!newItem.category || !newItem.product_name) {
      alert("Please fill out category and name fields");
      setUploadStatus("idle");
      return;
    }
    
    try {
      // In a real implementation, you would upload the image first
      // and then use the returned URL. For now, we'll use the preview
      // or a placeholder URL
      const imageUrl = uploadPreview || "https://placehold.co/300x300";
      
      // Prepare item data
      const itemData = {
        ...newItem,
        image_url: imageUrl
      };
      
      // Send to backend
      const response = await fetch("http://localhost:3001/api/profile/wardrobe", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(itemData)
      });
      
      if (!response.ok) {
        throw new Error("Failed to add item to wardrobe");
      }
      
      const result = await response.json();
      
      // Add new item to the state
      setItems([...items, result.data]);
      
      // Reset form
      setNewItem({
        category: "",
        color: "",
        style: "",
        season: [],
        occasions: [],
        image_url: "",
        product_name: "",
        custom_name: ""
      });
      
      setUploadedFile(null);
      setUploadPreview(null);
      setShowAddModal(false);
      setUploadStatus("success");
      
    } catch (err) {
      console.error("Error adding item:", err);
      setUploadStatus("error");
    }
  };

  // Handle deleting an item
  const handleDeleteItem = async (itemId: string) => {
    if (!confirm("Are you sure you want to delete this item?")) return;
    
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch(`http://localhost:3001/api/profile/wardrobe/${itemId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error("Failed to delete wardrobe item");
      }
      
      // Remove item from state
      setItems(items.filter(item => item.id !== itemId));
      
    } catch (err) {
      console.error("Error deleting item:", err);
      alert("Failed to delete item. Please try again.");
    }
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      category: "",
      color: "",
      season: "",
      occasion: ""
    });
    setSearchQuery("");
  };

  // Handle adding search result to wardrobe
  const handleAddSearchResultToWardrobe = (item: any) => {
    // Convert search result to wardrobe item
    const wardrobeItem = {
      ...items[0], // Get structure from existing item
      id: `temp-${Date.now()}`, // Temporary ID until backend responds
      category: item.category || "",
      color: item.color || "",
      style: "",
      season: [],
      occasions: [],
      image_url: item.image_url || "",
      product_name: item.name || "New Item",
      custom_name: null,
      added_at: new Date().toISOString()
    };
    
    // Add to state immediately for UI feedback
    setItems(prevItems => [...prevItems, wardrobeItem]);
  };

  return (
    <div className="wardrobe-container">
      <Header />
      <main className="wardrobe-main">
        <section className="wardrobe-header">
          <div className="wardrobe-title">
            <h1>My Wardrobe</h1>
            <p>Manage your clothing items and build outfit combinations</p>
          </div>
          <div className="wardrobe-actions">
            <button 
              className="wardrobe-action-button add-item"
              onClick={() => setShowAddModal(true)}
            >
              <Plus size={20} />
              Add Item
            </button>
            <button 
              className="wardrobe-action-button search"
              onClick={() => setShowSearchModal(true)}
            >
              <Search size={20} />
              Search Outfits
            </button>
            <button 
              className={`wardrobe-action-button filter ${showFilters ? 'active' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter size={20} />
              Filters
            </button>
            <div className="wardrobe-view-toggles">
              <button 
                className={`view-toggle ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode("grid")}
                aria-label="Grid view"
              >
                <Grid size={20} />
              </button>
              <button 
                className={`view-toggle ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode("list")}
                aria-label="List view"
              >
                <List size={20} />
              </button>
            </div>
          </div>
        </section>

        {/* Filters Section */}
        {showFilters && (
          <section className="wardrobe-filters">
            <div className="filter-header">
              <h2>Filter Items</h2>
              <button onClick={resetFilters} className="reset-filters">Reset</button>
            </div>
            <div className="filters-row">
              <div className="filter-group">
                <label>Search</label>
                <div className="search-input">
                  <Search size={18} />
                  <input 
                    type="text" 
                    placeholder="Search items..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery("")} className="clear-search">
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>
              <div className="filter-group">
                <label>Category</label>
                <select 
                  value={filters.category}
                  onChange={(e) => setFilters({...filters, category: e.target.value})}
                >
                  <option value="">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              <div className="filter-group">
                <label>Color</label>
                <select 
                  value={filters.color}
                  onChange={(e) => setFilters({...filters, color: e.target.value})}
                >
                  <option value="">All Colors</option>
                  {colors.map(color => (
                    <option key={color} value={color}>{color}</option>
                  ))}
                </select>
              </div>
              <div className="filter-group">
                <label>Season</label>
                <select 
                  value={filters.season}
                  onChange={(e) => setFilters({...filters, season: e.target.value})}
                >
                  <option value="">All Seasons</option>
                  {seasons.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>
              <div className="filter-group">
                <label>Occasion</label>
                <select 
                  value={filters.occasion}
                  onChange={(e) => setFilters({...filters, occasion: e.target.value})}
                >
                  <option value="">All Occasions</option>
                  {occasions.map(occasion => (
                    <option key={occasion} value={occasion}>{occasion}</option>
                  ))}
                </select>
              </div>
            </div>
          </section>
        )}

        {/* Wardrobe Content */}
        <section className={`wardrobe-content ${viewMode}`}>
          {loading ? (
            <div className="wardrobe-loading">
              <p>Loading your wardrobe...</p>
            </div>
          ) : error ? (
            <div className="wardrobe-error">
              <p>{error}</p>
              <Button onClick={() => window.location.reload()}>Try Again</Button>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="wardrobe-empty">
              <div className="empty-icon">
                <Shirt size={48} />
              </div>
              <h2>Your wardrobe is empty</h2>
              <p>Add items to your wardrobe to get started</p>
              <Button onClick={() => setShowAddModal(true)}>Add Your First Item</Button>
            </div>
          ) : (
            <>
              <div className="items-count">
                Showing {filteredItems.length} of {items.length} items
              </div>
              <div className={`wardrobe-items ${viewMode}`}>
                {filteredItems.map(item => (
                  <div key={item.id} className={`wardrobe-item ${viewMode}`}>
                    <div className="item-image">
                      <img 
                        src={item.image_url || "https://placehold.co/300x300"} 
                        alt={item.product_name} 
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = "https://placehold.co/300x300";
                        }}
                      />
                    </div>
                    <div className="item-info">
                      <h3>{item.custom_name || item.product_name}</h3>
                      <div className="item-details">
                        <span className="item-category">{item.category}</span>
                        {item.color && <span className="item-color">{item.color}</span>}
                      </div>
                      {viewMode === "list" && (
                        <div className="item-metadata">
                          {item.season && item.season.length > 0 && (
                            <div className="metadata-group">
                              <strong>Seasons:</strong> {item.season.join(", ")}
                            </div>
                          )}
                          {item.occasions && item.occasions.length > 0 && (
                            <div className="metadata-group">
                              <strong>Occasions:</strong> {item.occasions.join(", ")}
                            </div>
                          )}
                        </div>
                      )}
                      <div className="item-actions">
                        <button 
                          className="item-action delete"
                          onClick={() => handleDeleteItem(item.id)}
                          aria-label="Delete item"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </main>

      {/* Add Item Modal */}
      {showAddModal && (
        <div className="wardrobe-modal-overlay">
          <div className="wardrobe-modal">
            <div className="modal-header">
              <h2>Add New Item</h2>
              <button 
                className="close-modal" 
                onClick={() => setShowAddModal(false)}
                aria-label="Close modal"
              >
                <X size={24} />
              </button>
            </div>
            <div className="modal-content">
              <div className="modal-columns">
                <div className="form-column">
                  <div className="form-group">
                    <label>Item Name *</label>
                    <input 
                      type="text" 
                      value={newItem.product_name}
                      onChange={(e) => setNewItem({...newItem, product_name: e.target.value})}
                      placeholder="e.g., Blue Oxford Shirt"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Custom Name (Optional)</label>
                    <input 
                      type="text" 
                      value={newItem.custom_name}
                      onChange={(e) => setNewItem({...newItem, custom_name: e.target.value})}
                      placeholder="e.g., My Favorite Shirt"
                    />
                  </div>
                  <div className="form-group">
                    <label>Category *</label>
                    <select 
                      value={newItem.category}
                      onChange={(e) => setNewItem({...newItem, category: e.target.value})}
                      required
                    >
                      <option value="">Select Category</option>
                      {categories.map(category => (
                        <option key={category} value={category}>{category}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Color</label>
                    <select 
                      value={newItem.color}
                      onChange={(e) => setNewItem({...newItem, color: e.target.value})}
                    >
                      <option value="">Select Color</option>
                      {colors.map(color => (
                        <option key={color} value={color}>{color}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Style (Optional)</label>
                    <input 
                      type="text" 
                      value={newItem.style}
                      onChange={(e) => setNewItem({...newItem, style: e.target.value})}
                      placeholder="e.g., Casual, Formal, Bohemian"
                    />
                  </div>
                </div>
                
                <div className="image-column">
                  <div className="image-upload-container">
                    {uploadPreview ? (
                      <div className="image-preview">
                        <img src={uploadPreview} alt="Item preview" />
                        <button 
                          className="remove-image" 
                          onClick={() => {
                            setUploadedFile(null);
                            setUploadPreview(null);
                          }}
                        >
                          <X size={20} />
                        </button>
                      </div>
                    ) : (
                      <div className="upload-placeholder" onClick={() => document.getElementById("item-image-upload")?.click()}>
                        <Upload size={32} />
                        <p>Upload Image</p>
                        <span>Click to browse or drag an image here</span>
                      </div>
                    )}
                    <input 
                      type="file" 
                      id="item-image-upload"
                      onChange={handleFileChange}
                      accept="image/*"
                      style={{ display: "none" }}
                    />
                  </div>
                  
                  <div className="form-group seasons-group">
                    <label>Seasons</label>
                    <div className="checkbox-group">
                      {seasons.map(season => (
                        <div key={season} className="checkbox-item">
                          <input 
                            type="checkbox"
                            id={`season-${season}`}
                            checked={newItem.season.includes(season)}
                            onChange={() => toggleSeason(season)}
                          />
                          <label htmlFor={`season-${season}`}>{season}</label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="form-group occasions-group">
                    <label>Occasions</label>
                    <div className="checkbox-group">
                      {occasions.map(occasion => (
                        <div key={occasion} className="checkbox-item">
                          <input 
                            type="checkbox"
                            id={`occasion-${occasion}`}
                            checked={newItem.occasions.includes(occasion)}
                            onChange={() => toggleOccasion(occasion)}
                          />
                          <label htmlFor={`occasion-${occasion}`}>{occasion}</label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={() => setShowAddModal(false)}>
                Cancel
              </button>
              <button 
                className="add-button" 
                onClick={handleAddItem}
                disabled={uploadStatus === "uploading"}
              >
                {uploadStatus === "uploading" ? (
                  <>Saving...</>
                ) : uploadStatus === "success" ? (
                  <><CheckCircle size={18} /> Added</>
                ) : (
                  <>Add to Wardrobe</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search Outfit Modal */}
      <SearchOutfit 
        isOpen={showSearchModal} 
        onClose={() => setShowSearchModal(false)}
        onAddToWardrobe={handleAddSearchResultToWardrobe}
      />
    </div>
  );
};

export default Wardrobe; 