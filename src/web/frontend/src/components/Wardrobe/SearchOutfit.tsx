import React, { useState } from 'react';
import { X, Search, Plus, Loader2, AlertCircle, Filter, ShoppingBag, Star } from 'lucide-react';
import './Wardrobe.css';

interface SearchOutfitProps {
  isOpen: boolean;
  onClose: () => void;
  onAddToWardrobe: (item: any) => void;
}

interface SearchResult {
  id: string;
  name: string;
  category: string;
  brand: string;
  color: string;
  price: number;
  currency: string;
  image_url: string;
  rating?: number;
  description?: string;
}

const SearchOutfit: React.FC<SearchOutfitProps> = ({ isOpen, onClose, onAddToWardrobe }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [addingItemId, setAddingItemId] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    colors: [] as string[],
    categories: [] as string[],
    priceRange: { min: 0, max: 1000 }
  });
  const [searchContext, setSearchContext] = useState<'item' | 'outfit'>('item');
  
  // Common colors and categories for filters
  const availableColors = [
    'Black', 'White', 'Blue', 'Red', 'Green', 'Yellow', 'Purple', 'Pink', 'Orange', 'Brown', 'Grey', 'Navy', 'Beige'
  ];
  const availableCategories = [
    'Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Footwear', 'Accessories', 'Activewear'
  ];

  if (!isOpen) return null;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    
    try {
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('You must be logged in to search for outfits');
      }
      
      // Determine endpoint based on search context
      const endpoint = searchContext === 'outfit' ? '/api/outfits/compose' : '/api/outfits/search';
      
      // Build request body based on search context
      let requestBody = {};
      
      if (searchContext === 'outfit') {
        // For outfit composition
        requestBody = {
          theme: searchQuery,
          occasion: filters.categories.length > 0 ? filters.categories[0] : undefined,
          color_scheme: filters.colors.length > 0 ? filters.colors.join(' and ') : undefined,
          include_wardrobe_items: true
        };
      } else {
        // For regular search
        let enhancedQuery = searchQuery;
        
        // Enhance query with color if filters are set
        if (filters.colors.length > 0) {
          enhancedQuery = `${filters.colors.join(' ')} ${enhancedQuery}`;
        }
        
        // Enhance query with category if filters are set
        if (filters.categories.length > 0) {
          enhancedQuery = `${enhancedQuery} ${filters.categories.join(' ')}`;
        }
        
        requestBody = { query: enhancedQuery };
      }
      
      // Make API call
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to search for outfits');
      }
      
      const data = await response.json();
      
      if (searchContext === 'outfit') {
        // Handle outfit response structure
        if (data.outfit && (data.outfit.search_items || data.outfit.items)) {
          const outfitItems = data.outfit.search_items || [];
          
          // Format outfit items for display
          const formattedItems = outfitItems.map((item: any) => ({
            id: item.id,
            name: item.name,
            category: item.category,
            brand: item.brand || 'Unknown',
            color: item.color || 'Various',
            price: item.price || 0,
            currency: item.currency || 'USD',
            image_url: item.image_url || `https://placehold.co/300x400/9CA3AF/FFFFFF?text=${encodeURIComponent(item.name)}`
          }));
          
          setSearchResults(formattedItems);
          
          if (formattedItems.length === 0) {
            setError('No outfit items found. Try a different search query.');
          }
        } else {
          setError('No outfit items found. Try a different search query.');
          setSearchResults([]);
        }
      } else {
        // Handle regular search response
        if (data.items?.length > 0) {
          setSearchResults(data.items);
        } else {
          setError('No results found for your search. Try a different query.');
          setSearchResults([]);
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while searching. Please try again.');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddToWardrobe = async (item: SearchResult) => {
    setAddingItemId(item.id);
    
    try {
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('You must be logged in to add items to your wardrobe');
      }
      
      // Make API call to add item to wardrobe
      const response = await fetch('/api/outfits/add-to-wardrobe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          item_id: item.id,
          item_details: {
            product_id: item.id,
            category: item.category,
            color: item.color,
            brand: item.brand,
            image_url: item.image_url,
            product_name: item.name
          }
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to add item to wardrobe');
      }
      
      // Call the parent component's handler
      onAddToWardrobe(item);
      
      // Remove the item from search results to indicate it's been added
      setSearchResults(prevResults => prevResults.filter(result => result.id !== item.id));
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while adding to wardrobe. Please try again.');
    } finally {
      setAddingItemId(null);
    }
  };

  const toggleColorFilter = (color: string) => {
    setFilters(prev => {
      if (prev.colors.includes(color)) {
        return { ...prev, colors: prev.colors.filter(c => c !== color) };
      } else {
        return { ...prev, colors: [...prev.colors, color] };
      }
    });
  };

  const toggleCategoryFilter = (category: string) => {
    setFilters(prev => {
      if (prev.categories.includes(category)) {
        return { ...prev, categories: prev.categories.filter(c => c !== category) };
      } else {
        return { ...prev, categories: [...prev.categories, category] };
      }
    });
  };

  const resetFilters = () => {
    setFilters({
      colors: [],
      categories: [],
      priceRange: { min: 0, max: 1000 }
    });
  };

  const renderFilters = () => (
    <div className="wardrobe-filters">
      <div className="filter-header">
        <h2>Filter Options</h2>
        <button onClick={resetFilters} className="reset-filters">Reset All</button>
      </div>
      
      <div className="filter-section">
        <h3>Search Type</h3>
        <div className="filter-options">
          <div className={`filter-option ${searchContext === 'item' ? 'selected' : ''}`} onClick={() => setSearchContext('item')}>
            <div className="checkbox">{searchContext === 'item' && <Check />}</div>
            <span>Individual Items</span>
          </div>
          <div className={`filter-option ${searchContext === 'outfit' ? 'selected' : ''}`} onClick={() => setSearchContext('outfit')}>
            <div className="checkbox">{searchContext === 'outfit' && <Check />}</div>
            <span>Complete Outfits</span>
          </div>
        </div>
      </div>
      
      <div className="filter-section">
        <h3>Colors</h3>
        <div className="filter-options">
          {availableColors.map(color => (
            <div 
              key={color}
              className={`filter-option ${filters.colors.includes(color) ? 'selected' : ''}`}
              onClick={() => toggleColorFilter(color)}
            >
              <div className="checkbox">{filters.colors.includes(color) && <Check />}</div>
              <span>{color}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="filter-section">
        <h3>Categories</h3>
        <div className="filter-options">
          {availableCategories.map(category => (
            <div 
              key={category}
              className={`filter-option ${filters.categories.includes(category) ? 'selected' : ''}`}
              onClick={() => toggleCategoryFilter(category)}
            >
              <div className="checkbox">{filters.categories.includes(category) && <Check />}</div>
              <span>{category}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="wardrobe-modal-overlay" onClick={onClose}>
      <div className="wardrobe-modal search-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Search for {searchContext === 'outfit' ? 'Complete Outfits' : 'Fashion Items'}</h2>
          <button className="close-modal" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-content">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              className="outfit-search-input"
              placeholder={`Search for ${searchContext === 'outfit' ? 'outfits' : 'clothes and accessories'}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button 
              type="button" 
              className="wardrobe-action-button filter"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter size={18} />
              Filters
            </button>
            <button 
              type="submit" 
              className="search-outfit-button"
              disabled={isSearching || !searchQuery.trim()}
            >
              {isSearching ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search size={18} />
                  Search
                </>
              )}
            </button>
          </form>
          
          {showFilters && renderFilters()}
          
          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              <p>{error}</p>
            </div>
          )}
          
          {isSearching ? (
            <div className="searching-indicator">
              <div className="spinner"></div>
              <p>Searching for {searchContext === 'outfit' ? 'outfits' : 'items'} matching "{searchQuery}"...</p>
            </div>
          ) : searchResults.length > 0 ? (
            <div className="search-results">
              <h3>Search Results ({searchResults.length})</h3>
              <div className="search-results-grid">
                {searchResults.map(item => (
                  <div key={item.id} className="search-result-item">
                    <div className="result-image">
                      <img src={item.image_url} alt={item.name} onError={(e) => {
                        (e.target as HTMLImageElement).src = "https://placehold.co/300x400/9CA3AF/FFFFFF?text=No+Image";
                      }} />
                    </div>
                    <div className="result-info">
                      <h4>{item.name}</h4>
                      <p>{item.brand}</p>
                      <p>{item.category} • {item.color}</p>
                      {item.rating && (
                        <p className="result-rating">
                          <Star size={14} fill="gold" color="gold" /> 
                          {item.rating.toFixed(1)}
                        </p>
                      )}
                      <p className="result-price">
                        {item.currency} {item.price.toFixed(2)}
                      </p>
                    </div>
                    <button 
                      className="add-to-wardrobe-button"
                      onClick={() => handleAddToWardrobe(item)}
                      disabled={addingItemId === item.id}
                    >
                      {addingItemId === item.id ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Adding...
                        </>
                      ) : (
                        <>
                          <Plus size={16} />
                          Add to Wardrobe
                        </>
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : searchQuery && !isSearching ? (
            <div className="no-results">
              <p>No results found for "{searchQuery}". Try a different search term or browse our recommendations.</p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

// Helper component for checkbox icons
const Check = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export default SearchOutfit; 