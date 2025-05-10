import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ShoppingBag, Heart, X, SlidersHorizontal, Check } from 'lucide-react';
import Header from '../Header/Header';
import './BrowseProducts.css';

interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  currency: string;
  image_url: string;
  colors: string[];
  sizes: string[];
  description: string;
  rating: number;
  availability: boolean;
  tags: string[];
}

const BrowseProducts: React.FC = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [sortOption, setSortOption] = useState('recommended');
  
  // Available filter options (would normally be fetched from API)
  const categoryOptions = [
    'Dresses', 'Tops', 'Pants', 'Jackets', 'Shoes', 'Accessories', 
    'T-shirts', 'Jeans', 'Skirts', 'Sweaters'
  ];
  
  const brandOptions = [
    'Zara', 'H&M', 'Nike', 'Adidas', 'Uniqlo', 'Levi\'s', 
    'Gap', 'Mango', 'Gucci', 'Prada'
  ];
  
  const colorOptions = [
    'Black', 'White', 'Red', 'Blue', 'Green', 'Yellow', 
    'Pink', 'Purple', 'Brown', 'Gray', 'Beige'
  ];
  
  const sortOptions = [
    { value: 'recommended', label: 'Recommended' },
    { value: 'price-low', label: 'Price: Low to High' },
    { value: 'price-high', label: 'Price: High to Low' },
    { value: 'newest', label: 'Newest First' },
    { value: 'popularity', label: 'Most Popular' }
  ];

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login', { state: { from: '/browse' } });
      return;
    }
    
    fetchProducts();
  }, [navigate]);

  useEffect(() => {
    applyFilters();
  }, [searchQuery, selectedCategories, selectedBrands, priceRange, selectedColors, sortOption, products]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      // In a real app, this would be an API call. For now, using mock data
      const mockProducts: Product[] = Array(24).fill(null).map((_, index) => ({
        id: `product-${index + 1}`,
        name: `Fashion Item ${index + 1}`,
        brand: brandOptions[Math.floor(Math.random() * brandOptions.length)],
        category: categoryOptions[Math.floor(Math.random() * categoryOptions.length)],
        price: Math.floor(Math.random() * 200) + 20,
        currency: 'USD',
        image_url: `https://picsum.photos/seed/${index + 1}/400/600`,
        colors: [colorOptions[Math.floor(Math.random() * colorOptions.length)]],
        sizes: ['S', 'M', 'L', 'XL'],
        description: 'A stylish fashion item for any occasion.',
        rating: Math.floor(Math.random() * 5) + 1,
        availability: Math.random() > 0.2,
        tags: ['trending', 'seasonal']
      }));

      setProducts(mockProducts);
      setFilteredProducts(mockProducts);
      setLoading(false);
    } catch (err) {
      setError('Failed to load products. Please try again later.');
      setLoading(false);
      console.error('Error fetching products:', err);
    }
  };

  const applyFilters = () => {
    let filtered = [...products];
    
    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        product => 
          product.name.toLowerCase().includes(query) || 
          product.brand.toLowerCase().includes(query) ||
          product.description.toLowerCase().includes(query)
      );
    }
    
    // Apply category filter
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(product => 
        selectedCategories.includes(product.category)
      );
    }
    
    // Apply brand filter
    if (selectedBrands.length > 0) {
      filtered = filtered.filter(product => 
        selectedBrands.includes(product.brand)
      );
    }
    
    // Apply price range filter
    filtered = filtered.filter(product => 
      product.price >= priceRange.min && product.price <= priceRange.max
    );
    
    // Apply color filter
    if (selectedColors.length > 0) {
      filtered = filtered.filter(product => 
        product.colors.some(color => selectedColors.includes(color))
      );
    }
    
    // Apply sorting
    switch (sortOption) {
      case 'price-low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'newest':
        // In a real app, would sort by date
        filtered.sort((a, b) => a.id.localeCompare(b.id));
        break;
      case 'popularity':
        // In a real app, would sort by popularity metric
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      default:
        // 'recommended' - would be personalized in a real app
        break;
    }
    
    setFilteredProducts(filtered);
  };

  const toggleCategoryFilter = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const toggleBrandFilter = (brand: string) => {
    setSelectedBrands(prev => 
      prev.includes(brand)
        ? prev.filter(b => b !== brand)
        : [...prev, brand]
    );
  };

  const toggleColorFilter = (color: string) => {
    setSelectedColors(prev => 
      prev.includes(color)
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
  };

  const handlePriceChange = (type: 'min' | 'max', value: string) => {
    const numValue = parseInt(value) || 0;
    setPriceRange(prev => ({
      ...prev,
      [type]: numValue
    }));
  };

  const resetFilters = () => {
    setSelectedCategories([]);
    setSelectedBrands([]);
    setPriceRange({ min: 0, max: 1000 });
    setSelectedColors([]);
    setSortOption('recommended');
    setSearchQuery('');
  };

  const addToFavorites = async (productId: string) => {
    try {
      // This would be an API call in a real app
      console.log(`Added product ${productId} to favorites`);
      // Show success feedback
      alert('Product added to favorites!');
    } catch (err) {
      console.error('Error adding to favorites:', err);
    }
  };

  const addToCart = async (productId: string) => {
    try {
      // This would be an API call in a real app
      console.log(`Added product ${productId} to cart`);
      // Show success feedback
      alert('Product added to cart!');
    } catch (err) {
      console.error('Error adding to cart:', err);
    }
  };

  const viewProductDetails = (productId: string) => {
    navigate(`/product/${productId}`);
  };

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(price);
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (selectedCategories.length) count++;
    if (selectedBrands.length) count++;
    if (selectedColors.length) count++;
    if (priceRange.min > 0 || priceRange.max < 1000) count++;
    return count;
  };

  return (
    <div className="browse-container">
      <Header />
      <main className="browse-main">
        <div className="browse-header">
          <h1>Browse Products</h1>
          <p>Discover fashion items tailored to your style</p>
          
          <div className="search-and-filter">
            <div className="search-bar">
              <Search size={20} />
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button 
                  className="clear-search"
                  onClick={() => setSearchQuery('')}
                >
                  <X size={16} />
                </button>
              )}
            </div>
            
            <button 
              className={`filter-toggle ${showFilters ? 'active' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
            >
              <SlidersHorizontal size={20} />
              Filters
              {getActiveFilterCount() > 0 && (
                <span className="filter-count">{getActiveFilterCount()}</span>
              )}
            </button>
          </div>
        </div>

        <div className="browse-content">
          {showFilters && (
            <aside className="browse-filters">
              <div className="filters-header">
                <h2>Filters</h2>
                <button 
                  className="reset-filters"
                  onClick={resetFilters}
                >
                  Reset All
                </button>
              </div>
              
              <div className="filter-section">
                <h3>Categories</h3>
                <div className="filter-options">
                  {categoryOptions.map(category => (
                    <div 
                      key={category}
                      className={`filter-option ${selectedCategories.includes(category) ? 'selected' : ''}`}
                      onClick={() => toggleCategoryFilter(category)}
                    >
                      <div className="checkbox">
                        {selectedCategories.includes(category) && <Check size={14} />}
                      </div>
                      {category}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="filter-section">
                <h3>Brands</h3>
                <div className="filter-options">
                  {brandOptions.map(brand => (
                    <div 
                      key={brand}
                      className={`filter-option ${selectedBrands.includes(brand) ? 'selected' : ''}`}
                      onClick={() => toggleBrandFilter(brand)}
                    >
                      <div className="checkbox">
                        {selectedBrands.includes(brand) && <Check size={14} />}
                      </div>
                      {brand}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="filter-section">
                <h3>Price Range</h3>
                <div className="price-range">
                  <div className="price-input">
                    <label>Min</label>
                    <input
                      type="number"
                      min="0"
                      max={priceRange.max}
                      value={priceRange.min}
                      onChange={(e) => handlePriceChange('min', e.target.value)}
                    />
                  </div>
                  <div className="price-input">
                    <label>Max</label>
                    <input
                      type="number"
                      min={priceRange.min}
                      value={priceRange.max}
                      onChange={(e) => handlePriceChange('max', e.target.value)}
                    />
                  </div>
                </div>
              </div>
              
              <div className="filter-section">
                <h3>Colors</h3>
                <div className="color-options">
                  {colorOptions.map(color => (
                    <div 
                      key={color}
                      className={`color-option ${selectedColors.includes(color) ? 'selected' : ''}`}
                      onClick={() => toggleColorFilter(color)}
                      title={color}
                    >
                      <div 
                        className="color-swatch" 
                        style={{ backgroundColor: color.toLowerCase() }}
                      />
                      {selectedColors.includes(color) && (
                        <div className="color-check">
                          <Check size={12} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          )}
          
          <div className="products-section">
            <div className="products-header">
              <div className="products-count">
                {filteredProducts.length} products
              </div>
              
              <div className="sort-dropdown">
                <label>Sort by:</label>
                <select 
                  value={sortOption}
                  onChange={(e) => setSortOption(e.target.value)}
                >
                  {sortOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            {loading ? (
              <div className="products-loading">
                <div className="loading-spinner"></div>
                <p>Loading products...</p>
              </div>
            ) : error ? (
              <div className="products-error">
                <p>{error}</p>
                <button onClick={fetchProducts}>Try Again</button>
              </div>
            ) : filteredProducts.length === 0 ? (
              <div className="no-products">
                <p>No products found matching your criteria.</p>
                <button onClick={resetFilters}>Reset Filters</button>
              </div>
            ) : (
              <div className="products-grid">
                {filteredProducts.map(product => (
                  <div key={product.id} className="product-card">
                    <div 
                      className="product-image" 
                      onClick={() => viewProductDetails(product.id)}
                    >
                      <img src={product.image_url} alt={product.name} />
                      {!product.availability && (
                        <div className="out-of-stock-badge">
                          Out of Stock
                        </div>
                      )}
                    </div>
                    <div className="product-details">
                      <h3 onClick={() => viewProductDetails(product.id)}>
                        {product.name}
                      </h3>
                      <div className="product-brand">{product.brand}</div>
                      <div className="product-price">
                        {formatPrice(product.price, product.currency)}
                      </div>
                      <div className="product-rating">
                        {Array(5).fill(0).map((_, i) => (
                          <span 
                            key={i} 
                            className={i < product.rating ? 'star-filled' : 'star-empty'}
                          >
                            ★
                          </span>
                        ))}
                      </div>
                      <div className="product-actions">
                        <button 
                          className="action-button favorite"
                          onClick={() => addToFavorites(product.id)}
                        >
                          <Heart size={18} />
                        </button>
                        <button 
                          className="action-button add-to-cart"
                          onClick={() => addToCart(product.id)}
                          disabled={!product.availability}
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
          </div>
        </div>
      </main>
    </div>
  );
};

export default BrowseProducts; 