import React, { useState, useEffect, useRef } from 'react';
import ProductsDisplay from '../components/ProductsDisplay';
import useProductsMenu from '../hooks/useProductsMenu';
import Header from '../components/Header';
import '../styles/ProductsMenu.css';
import ChatBubble from '../components/ChatBubble';
import { getProducts, searchProducts } from '../services/productService';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { animated, useSpring } from '@react-spring/web';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import userService, { UserQuery } from '../services/userService';

const ProductsMenu: React.FC = () => {
  const [searchLoading, setSearchLoading] = useState(false);

  const { applianceProducts, musicalProducts, videoGameProducts, clothesProducts, loading, error } = useProductsMenu();
  const [products, setProducts] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showChat, setShowChat] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedStore, setSelectedStore] = useState<string>("");
  const [priceRange, setPriceRange] = useState<string>("all");
  const [openFilter, setOpenFilter] = useState<string | null>(null);
  const [searchActive, setSearchActive] = useState(false);
  const [recentQueries, setRecentQueries] = useState<UserQuery[]>([]);
  const searchInputRef = useRef<HTMLInputElement>(null);


  const loadRecentQueries = async () => {
    try {
      const queries = await userService.getRecentQueries();
      setRecentQueries(queries);
    } catch (error) {
      console.error('Error loading recent queries:', error);
    }
  };


  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };

  const toggleFilter = (filterName: string) => {
    setOpenFilter(openFilter === filterName ? null : filterName);
  };

  const selectOption = (type: string, value: string) => {
    if (type === 'category') setSelectedCategory(value);
    if (type === 'store') setSelectedStore(value);
    if (type === 'price') setPriceRange(value);
    setOpenFilter(null);
  };

  const setGridMinHeight = () => {
    const grid = document.querySelector('.products-grid') as HTMLElement;
    if (!grid) return;

    const currentHeight = grid.offsetHeight;
    grid.style.minHeight = `${currentHeight}px`;
  };
  
  

  const handleSearchFocus = () => {
    loadRecentQueries()
    setSearchActive(true);
    setTimeout(() => {
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, 0);
  };

  const handleSearchBlur = () => {};

  const handleSearchSubmit = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      try {
        setSearchLoading(true);
        setRecentQueries([]);
        setGridMinHeight();
        const searchResults = await searchProducts(searchQuery.trim());
        setProducts(searchResults.top_products || []);
        await userService.saveQuery(searchQuery.trim());

      } catch (error) {
        console.error('Error in search:', error);
        setProducts([]);
      } finally {
        setSearchLoading(false);
      }
    }
  };

  const handleCancelSearch = () => {
    setSearchQuery("");
    setProducts([]);
    setSearchActive(false);
  };

  const arrowAnimation = useSpring({
    transform: openFilter ? 'rotate(180deg)' : 'rotate(0deg)',
    config: { tension: 300, friction: 20 }
  });

  const optionsAnimation = useSpring({
    opacity: openFilter ? 1 : 0,
    height: openFilter ? 'auto' : 0,
    marginTop: openFilter ? '0.5rem' : '0',
    config: { tension: 300, friction: 20 }
  });

  const FilterButton = ({ 
    type, 
    label, 
    value, 
    options 
  }: {
    type: string;
    label: string;
    value: string;
    options: { value: string; label: string }[];
  }) => {
    return (
      <div className={`filter-button ${openFilter === type ? 'active' : ''}`}>
        <div className="filter-content" onClick={() => toggleFilter(type)}>
          <span className="filter-label">{label}</span>
          <div className="filter-value-container">
            <span className="filter-value">{value}</span>
            <animated.div style={arrowAnimation}>
              {openFilter === type ? (
                <ArrowDropUpIcon className="dropdown-icon" />
              ) : (
                <ArrowDropDownIcon className="dropdown-icon" />
              )}
            </animated.div>
          </div>
        </div>
  
        {openFilter === type && (
          <animated.div style={optionsAnimation} className="filter-options">
            {options.map((option) => (
              <div
                key={option.value}
                className={`option-item ${
                  (type === 'category' && selectedCategory === option.value) ||
                  (type === 'store' && selectedStore === option.value) ||
                  (type === 'price' && priceRange === option.value)
                    ? 'selected'
                    : ''
                }`}
                onClick={() => selectOption(type, option.value)}
              >
                {option.label}
              </div>
            ))}
          </animated.div>
        )}
      </div>
    );
  };

  return (
    <div className="products-menu-container">
      {loading && <div>Loading products...</div>}
      {error && <div>Error: {error}</div>}
      {!loading && !error && (
        <>
          <Header 
            onSearch={() => {}}
            onSearchFocus={handleSearchFocus}
            onSearchBlur={handleSearchBlur}
          />
          <div className="products-content">
            <div className="inspiration-container">
              <div className="inspiration-text">
                <h2>Get inspired</h2>
                <p>Find exactly what you need with our hand-picked selection of top-rated Amazon products across all categories. Save time and shop with confidence - we've done the research so you get only the best!</p>
              </div>
              
              <div className="filters-selectors">
                <FilterButton
                  type="category"
                  label="Category"
                  value={selectedCategory || "All Categories"}
                  options={[
                    { value: "", label: "All Categories" },
                    { value: "Appliances", label: "Appliances" },
                    { value: "Musical_Instruments", label: "Musical Instruments" },
                    { value: "Videogames", label: "Videogames" },
                    { value: "Clothes", label: "Clothes" }
                  ]}
                />
                
                <FilterButton
                  type="store"
                  label="Store"
                  value={selectedStore || "All Stores"}
                  options={[
                    { value: "", label: "All Stores" },
                    { value: "Amazon US", label: "Amazon US" },
                    { value: "Amazon UK", label: "Amazon UK" },
                    { value: "Amazon DE", label: "Amazon DE" },
                    { value: "Amazon ES", label: "Amazon ES" }
                  ]}
                />
                
                <FilterButton
                  type="price"
                  label="Price"
                  value={
                    priceRange === "all" ? "All Prices" : 
                    priceRange === "0-25" ? "$0 - $25" :
                    priceRange === "25-50" ? "$25 - $50" :
                    priceRange === "50-100" ? "$50 - $100" :
                    priceRange === "100-500" ? "$100 - $500" : "$500+"
                  }
                  options={[
                    { value: "all", label: "All Prices" },
                    { value: "0-25", label: "$0 - $25" },
                    { value: "25-50", label: "$25 - $50" },
                    { value: "50-100", label: "$50 - $100" },
                    { value: "100-500", label: "$100 - $500" },
                    { value: "500+", label: "$500+" }
                  ]}
                />
              </div>
            </div>

            {searchActive ? (
            <div className="search-mode-container">
              <div className="search-input-container">
                <SearchIcon className="search-icon" />
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="what are you looking for?"
                  className="minimal-search-input"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchSubmit}
                  autoFocus
                />
                <button 
                  className="cancel-search-button"
                  onClick={handleCancelSearch}
                >
                  Cancel
                </button>
              </div>

              {searchLoading && (
                <div className="loader-container">
                  <div className="loader"></div>
                </div>
              )}

              {!searchLoading && recentQueries.length > 0 && (
                <div className="recent-queries-container">
                  <div className="recent-queries-header">
                    <HistoryIcon className="history-icon" />
                    <span>Recent searches</span>
                  </div>
                  <ul className="recent-queries-list">
                    {recentQueries.map((query) => (
                      <li 
                        key={query.id}
                        className="recent-query-item"
                        onClick={() => {
                          setSearchQuery(query.query_text);
                          searchInputRef.current?.focus();
                        }}
                      >
                        {query.query_text}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!searchLoading && products.length > 0 && (
                <ProductsDisplay title="Search Results" products={products} />
              )}
            </div>
          ) : (
              <div className={`products-display-wrapper ${showChat ? 'with-chat' : ''}`}>
                <ProductsDisplay 
                  title="Latest in Appliances" 
                  category="Appliances" 
                  products={applianceProducts} 
                />
                <ProductsDisplay 
                  title="Latest in Musical Instruments" 
                  category="Musical_Instruments" 
                  products={musicalProducts} 
                />
                <ProductsDisplay 
                  title="Latest in Videogames" 
                  category="Videogames" 
                  products={videoGameProducts} 
                />
                <ProductsDisplay 
                  title="Latest in Clothes" 
                  category="Clothes" 
                  products={clothesProducts} 
                />
              </div>
            )}
          </div>
          <ChatBubble
            onClick={toggleChat}
            isOpen={showChat}
            onResponse={(botAnswer) => {
              if (botAnswer.text === "No products found.") {
              } else {
                if (botAnswer.products) {
                  setProducts(botAnswer.products);
                  setSearchActive(true);

                }
              }
            }}
          />
        </>
      )}
    </div>
  );
};

export default ProductsMenu;