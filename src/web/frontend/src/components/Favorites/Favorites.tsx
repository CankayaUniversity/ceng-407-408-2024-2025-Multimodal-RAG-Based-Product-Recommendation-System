import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../Header/Header";
import Button from "../ui/Button";
import { Heart, Grid, List, Filter, Search, Trash2, X, Star, StarOff, ShoppingBag, ShoppingCart, ChevronDown, Loader } from "lucide-react";
import "./Favorites.css";

interface FavoriteProduct {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  currency: string;
  image_url: string;
  rating: number;
  color: string;
  size?: string;
  date_added: string;
  available: boolean;
}

interface Filters {
  categories: string[];
  brands: string[];
  priceRange: {
    min: number;
    max: number;
  };
  rating: number | null;
}

const Favorites: React.FC = () => {
  const [favorites, setFavorites] = useState<FavoriteProduct[]>([]);
  const [filteredFavorites, setFilteredFavorites] = useState<FavoriteProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [username, setUsername] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);
  const [sortBy, setSortBy] = useState<'date' | 'price_low' | 'price_high' | 'name'>('date');
  const navigate = useNavigate();

  const [filters, setFilters] = useState<Filters>({
    categories: [],
    brands: [],
    priceRange: {
      min: 0,
      max: 1000
    },
    rating: null
  });
  
  // Available options for filtering
  const [availableFilters, setAvailableFilters] = useState({
    categories: [] as string[],
    brands: [] as string[],
    maxPrice: 1000
  });

  // Extract unique categories and brands for filters
  const categories = Array.from(new Set(favorites.map(item => item.category)));
  const brands = Array.from(new Set(favorites.map(item => item.brand)));

  useEffect(() => {
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("email");
    
    if (!token) {
      navigate("/login", { state: { from: "/favorites" } });
      return;
    }
    
    if (email) {
      const name = email.split("@")[0];
      setUsername(name.charAt(0).toUpperCase() + name.slice(1));
    }

    // Fetch user's favorites
    const fetchFavorites = async () => {
      try {
        const response = await fetch("http://localhost:3001/api/profile/favorites", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch favorites");
        }

        const data = await response.json();
        setFavorites(data.data || []);
        setFilteredFavorites(data.data || []);
        setLoading(false);

        // Extract available filter options from the data
        const categories = [...new Set(data.data.map(item => item.category))];
        const brands = [...new Set(data.data.map(item => item.brand))];
        const maxPrice = Math.max(...data.data.map(item => item.price));
        
        setAvailableFilters({
          categories,
          brands,
          maxPrice: Math.ceil(maxPrice / 100) * 100 // Round up to nearest 100
        });
        
        setFilters(prev => ({
          ...prev,
          priceRange: {
            min: 0,
            max: Math.ceil(maxPrice / 100) * 100
          }
        }));
      } catch (err) {
        setError("Failed to load favorites. Please try again later.");
        setLoading(false);
        console.error("Error fetching favorites:", err);
      }
    };

    fetchFavorites();
  }, [navigate]);

  useEffect(() => {
    // Apply filters and search when favorites, filters or search query changes
    applyFiltersAndSearch();
  }, [favorites, filters, searchQuery, sortBy]);

  const applyFiltersAndSearch = () => {
    let results = [...favorites];
    
    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      results = results.filter(
        item => 
          item.name.toLowerCase().includes(query) || 
          item.brand.toLowerCase().includes(query) ||
          item.category.toLowerCase().includes(query)
      );
    }
    
    // Apply category filters
    if (filters.categories.length > 0) {
      results = results.filter(item => filters.categories.includes(item.category));
    }
    
    // Apply brand filters
    if (filters.brands.length > 0) {
      results = results.filter(item => filters.brands.includes(item.brand));
    }
    
    // Apply price range filter
    results = results.filter(
      item => item.price >= filters.priceRange.min && item.price <= filters.priceRange.max
    );
    
    // Apply rating filter
    if (filters.rating) {
      results = results.filter(item => item.rating >= filters.rating);
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'date':
        results.sort((a, b) => new Date(b.date_added).getTime() - new Date(a.date_added).getTime());
        break;
      case 'price_low':
        results.sort((a, b) => a.price - b.price);
        break;
      case 'price_high':
        results.sort((a, b) => b.price - a.price);
        break;
      case 'name':
        results.sort((a, b) => a.name.localeCompare(b.name));
        break;
    }
    
    setFilteredFavorites(results);
  };

  // Toggle category selection
  const toggleCategory = (category: string) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  // Toggle brand selection
  const toggleBrand = (brand: string) => {
    if (selectedBrands.includes(brand)) {
      setSelectedBrands(selectedBrands.filter(b => b !== brand));
    } else {
      setSelectedBrands([...selectedBrands, brand]);
    }
  };

  // Handle price range change
  const handlePriceChange = (type: "min" | "max", value: string) => {
    const numValue = parseInt(value) || 0;
    if (type === "min") {
      setPriceRange([numValue, priceRange[1]]);
    } else {
      setPriceRange([priceRange[0], numValue]);
    }
  };

  // Remove from favorites
  const removeFromFavorites = async (itemId: string) => {
    if (!window.confirm("Are you sure you want to remove this item from your favorites?")) {
      return;
    }
    
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch(`http://localhost:3001/api/profile/favorites/${itemId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to remove from favorites");
      }

      // Update state to remove the item
      setFavorites(favorites.filter(item => item.id !== itemId));
      setFilteredFavorites(filteredFavorites.filter(item => item.id !== itemId));
    } catch (err) {
      console.error("Error removing from favorites:", err);
      alert("Failed to remove item from favorites. Please try again.");
    }
  };

  // Add to shopping cart
  const addToCart = async (product: FavoriteProduct) => {
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch("http://localhost:3001/api/cart/add", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          product_id: product.id,
          quantity: 1
        })
      });

      if (!response.ok) {
        throw new Error("Failed to add to cart");
      }

      alert("Item added to your shopping cart!");
    } catch (err) {
      console.error("Error adding to cart:", err);
      alert("Failed to add item to cart. Please try again.");
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setSearchQuery("");
    setSelectedCategories([]);
    setSelectedBrands([]);
    setPriceRange([0, 1000]);
    setFilters({
      categories: [],
      brands: [],
      priceRange: {
        min: 0,
        max: availableFilters.maxPrice
      },
      rating: null
    });
  };

  // Format price with currency
  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: currency || 'USD' 
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className="favorites-container">
      <Header />
      <main className="favorites-main">
        <section className="favorites-header">
          <div className="favorites-title">
            <h1><Heart size={28} className="heart-icon" /> My Favorites</h1>
            {!loading && !error && (
              <p>{filteredFavorites.length} {filteredFavorites.length === 1 ? 'item' : 'items'}</p>
            )}
          </div>
          <div className="favorites-actions">
            <div className="view-toggle">
              <button 
                className={`view-button ${viewMode === "grid" ? "active" : ""}`}
                onClick={() => setViewMode("grid")}
                aria-label="Grid view"
              >
                <Grid size={20} />
              </button>
              <button 
                className={`view-button ${viewMode === "list" ? "active" : ""}`}
                onClick={() => setViewMode("list")}
                aria-label="List view"
              >
                <List size={20} />
              </button>
            </div>
            <Button onClick={() => setShowFilters(!showFilters)}>
              <Filter size={16} />
              {showFilters ? "Hide Filters" : "Filter Items"}
            </Button>
          </div>
        </section>

        <section className="favorites-search">
          <div className="search-container">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search your favorites..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button 
                className="clear-search"
                onClick={() => setSearchQuery("")}
                aria-label="Clear search"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </section>

        {showFilters && (
          <section className="favorites-filters">
            <div className="filters-header">
              <h2>Filters</h2>
              <button 
                className="clear-all-filters"
                onClick={clearFilters}
              >
                Clear All
              </button>
            </div>
            <div className="filters-content">
              <div className="filter-group">
                <h3>Categories</h3>
                <div className="filter-options">
                  {categories.map(category => (
                    <div 
                      key={category} 
                      className={`filter-option ${selectedCategories.includes(category) ? 'selected' : ''}`}
                      onClick={() => toggleCategory(category)}
                    >
                      <span className="checkbox">
                        {selectedCategories.includes(category) && "✓"}
                      </span>
                      <span>{category}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="filter-group">
                <h3>Brands</h3>
                <div className="filter-options">
                  {brands.map(brand => (
                    <div 
                      key={brand} 
                      className={`filter-option ${selectedBrands.includes(brand) ? 'selected' : ''}`}
                      onClick={() => toggleBrand(brand)}
                    >
                      <span className="checkbox">
                        {selectedBrands.includes(brand) && "✓"}
                      </span>
                      <span>{brand}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="filter-group">
                <h3>Price Range</h3>
                <div className="price-range">
                  <div className="price-input">
                    <label>Min:</label>
                    <input 
                      type="number" 
                      min="0" 
                      value={priceRange[0]} 
                      onChange={(e) => handlePriceChange("min", e.target.value)}
                    />
                  </div>
                  <div className="price-input">
                    <label>Max:</label>
                    <input 
                      type="number" 
                      min="0" 
                      value={priceRange[1]} 
                      onChange={(e) => handlePriceChange("max", e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        <section className={`favorites-content ${viewMode}`}>
          {loading ? (
            <div className="favorites-loading">
              <div className="loading-spinner"></div>
              <p>Loading your favorite items...</p>
            </div>
          ) : error ? (
            <div className="favorites-error">
              <p>{error}</p>
              <Button onClick={() => window.location.reload()}>Try Again</Button>
            </div>
          ) : filteredFavorites.length === 0 ? (
            <div className="no-favorites">
              <h2>No favorites yet</h2>
              {favorites.length > 0 ? (
                <p>No items match your current filters. Try adjusting your search or filter criteria.</p>
              ) : (
                <p>Start adding your favorite items to your collection by clicking the heart icon on any product.</p>
              )}
              <Button onClick={() => navigate("/browse")}>Explore Products</Button>
            </div>
          ) : (
            <div className={`favorites-items ${viewMode}`}>
              {filteredFavorites.map(item => (
                <div key={item.id} className="favorite-item">
                  <div className="item-image">
                    <img 
                      src={item.image_url} 
                      alt={item.name}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "https://placehold.co/300x400?text=Product";
                      }}
                    />
                    {!item.available && (
                      <div className="unavailable-badge">
                        Currently Unavailable
                      </div>
                    )}
                  </div>
                  <div className="item-details">
                    <div className="item-name-rating">
                      <h3>{item.name}</h3>
                      {item.rating && (
                        <div className="item-rating">
                          {[...Array(5)].map((_, i) => (
                            <span key={i}>
                              {i < Math.floor(item.rating || 0) ? (
                                <Star size={16} className="star-filled" />
                              ) : (
                                <StarOff size={16} className="star-empty" />
                              )}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <p className="item-brand">{item.brand}</p>
                    <p className="item-price">{formatPrice(item.price, item.currency)}</p>
                    <p className="item-description">{item.description}</p>
                    <div className="item-meta">
                      <span className="item-category">{item.category}</span>
                      {item.color && <span className="item-color">Color: {item.color}</span>}
                      {item.size && <span className="item-size">Size: {item.size}</span>}
                    </div>
                    <div className="item-tags">
                      {item.tags && item.tags.map(tag => (
                        <span key={tag} className="item-tag">{tag}</span>
                      ))}
                    </div>
                    <div className="item-actions">
                      <button 
                        className="remove-button"
                        onClick={() => removeFromFavorites(item.id)}
                        aria-label="Remove from favorites"
                      >
                        <Trash2 size={18} />
                        Remove
                      </button>
                      <button 
                        className="add-to-cart-button"
                        onClick={() => addToCart(item)}
                        disabled={!item.available}
                        aria-label="Add to cart"
                      >
                        <ShoppingBag size={18} />
                        Add to Cart
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default Favorites; 