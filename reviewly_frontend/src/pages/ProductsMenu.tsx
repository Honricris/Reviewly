import React, { useState, useEffect, useRef } from 'react';
import ProductsDisplay from '../components/ProductsDisplay';
import useProductsMenu from '../hooks/useProductsMenu';
import Header from '../components/Header';
import '../styles/ProductsMenu.css';
import ChatBubble from '../components/ChatBubble';
import { getProducts, searchProducts, autocompleteProducts, getCategories } from '../services/productService';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import { animated, useSpring } from '@react-spring/web';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import userService, { UserQuery } from '../services/userService';

const ProductsMenu: React.FC = () => {
  const [searchLoading, setSearchLoading] = useState(false);
  const [autocompleteLoading, setAutocompleteLoading] = useState(false);
  const [filterLoading, setFilterLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]); 
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
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const [filtersApplied, setFiltersApplied] = useState(false);

  useEffect(() => {
    const fetchCategoriesAndFavorites = async () => {
      try {
        const [fetchedCategories, ids] = await Promise.all([
          getCategories(),
          userService.getFavorites()
        ]);
        setCategories(fetchedCategories);
        setFavoriteIds(ids);
      } catch (error) {
        console.error('Error fetching categories or favorites:', error);
        setCategories(['Appliances', 'Musical_Instruments', 'Videogames', 'Clothes']);
        setFavoriteIds([]);
      }
    };
    fetchCategoriesAndFavorites();
  }, []);

  useEffect(() => {
    const fetchFilteredProducts = async () => {
      if (searchActive) return;

      const hasFilters = selectedCategory !== "" || selectedStore !== "" || priceRange !== "all";
      setFiltersApplied(hasFilters);

      if (!hasFilters) {
        setProducts([]);
        return;
      }

      setFilterLoading(true);
      try {
        let price_min, price_max;
        
        switch (priceRange) {
          case "0-25":
            price_min = 0;
            price_max = 25;
            break;
          case "25-50":
            price_min = 25;
            price_max = 50;
            break;
          case "50-100":
            price_min = 50;
            price_max = 100;
            break;
          case "100-500":
            price_min = 100;
            price_max = 500;
            break;
          case "500+":
            price_min = 500;
            price_max = undefined;
            break;
          default:
            price_min = undefined;
            price_max = undefined;
        }

        const response = await getProducts(
          1,
          10,
          selectedCategory || undefined,
          undefined,
          price_min,
          price_max,
          selectedStore || undefined
        );
        
        setProducts(response.products || []);
      } catch (error) {
        console.error('Error fetching filtered products:', error);
        setProducts([]);
      } finally {
        setFilterLoading(false);
      }
    };

    fetchFilteredProducts();
  }, [selectedCategory, selectedStore, priceRange, searchActive]);

  const loadRecentQueries = async () => {
    try {
      const queries = await userService.getRecentQueries();
      setRecentQueries(queries);
    } catch (error) {
      console.error('Error loading recent queries:', error);
    }
  };

  const handleAutocomplete = async (query: string) => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      setAutocompleteLoading(true);
      const result = await autocompleteProducts(query);
      setSuggestions(result.suggestions || []);
    } catch (error) {
      console.error('Error in autocomplete:', error);
      setSuggestions([]);
    } finally {
      setAutocompleteLoading(false);
    }
  };
  
  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };

  const toggleFilter = (filterName: string) => {
    setOpenFilter((prev) => (prev === filterName ? null : filterName));
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
    loadRecentQueries();
    setSearchActive(true);
    setTimeout(() => {
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, 0);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (query.trim().length >= 2) {
      searchTimeoutRef.current = setTimeout(() => {
        handleAutocomplete(query);
      }, 500);
    } else {
      setSuggestions([]);
    }
  };

  const handleSearchBlur = () => {};

  const handleSearchSubmit = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      try {
        setSearchLoading(true);
        setSuggestions([]);
        setRecentQueries([]);
        setGridMinHeight();
        
        const startTime = performance.now();
        const searchResults = await searchProducts(searchQuery.trim());
        const endTime = performance.now();
        const executionTime = (endTime - startTime) / 1000; 
        
        setProducts(searchResults.top_products || []);
        await userService.saveQuery(searchQuery.trim(), executionTime);
      } catch (error) {
        console.error('Error in search:', error);
        setProducts([]);
      } finally {
        setSearchLoading(false);
      }
    }
  };

  const handleCancelSearch = () => {
    setSuggestions([]);
    setSearchQuery("");
    setProducts([]);
    setSearchActive(false);
  };

  const handleSuggestionClick = (suggestion: any) => {
    setSearchQuery(suggestion.title);
    setSuggestions([]);
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };

  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

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
    const [isEditing, setIsEditing] = useState(false);
    const [inputValue, setInputValue] = useState(value);
    const inputRef = useRef<HTMLInputElement>(null);
    const isOpen = openFilter === type;
  
    const handleClick = () => {
      if (type === 'store') {
        setIsEditing(true);
        setInputValue("");
        setTimeout(() => {
          if (inputRef.current) {
            inputRef.current.focus();
          }
        }, 0);
      } else {
        toggleFilter(type); 
      }
    };
  
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setInputValue(e.target.value);
    };
  
    const handleInputBlur = () => {
      setIsEditing(false);
      if (inputValue.trim() === '') {
        setInputValue("All Stores");
        selectOption(type, "");
      }
      if (inputValue.trim() !== '' && inputValue.trim() !== "All Stores") {
        selectOption(type, inputValue.trim());
      }
    };
  
    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        setIsEditing(false);
        if (inputValue.trim() === '') {
          setInputValue("All Stores");
          selectOption(type, "");
        }
        if (inputValue.trim() !== '' && inputValue.trim() !== "All Stores") {
          selectOption(type, inputValue.trim());
        }
        if (inputRef.current) {
          inputRef.current.blur();
        }
      }
    };
  
    return (
      <div className={`filter-button ${type === 'store' ? 'store-filter' : ''} ${openFilter === type ? 'active' : ''}`}>
        <div className="filter-content" onClick={handleClick}>
          <span className="filter-label">{label}</span>
          <div className="filter-value-container">
            {type === 'store' ? (
              isEditing ? (
                <input
                  ref={inputRef}
                  type="text"
                  className="store-input"
                  value={inputValue}
                  onChange={handleInputChange}
                  onBlur={handleInputBlur}
                  onKeyDown={handleInputKeyDown}
                  placeholder={isEditing ? "" : "All Stores"} 
                />
              ) : (
                <span className="filter-value">
                  {inputValue === "All Stores" ? "All Stores" : inputValue}
                </span>
              )
            ) : (
              <>
                <span className="filter-value">{value}</span>
                <animated.div style={arrowAnimation}>
                  {openFilter === type ? (
                    <ArrowDropUpIcon className="dropdown-icon" />
                  ) : (
                    <ArrowDropDownIcon className="dropdown-icon" />
                  )}
                </animated.div>
              </>
            )}
          </div>
        </div>
  
        {openFilter === type && type !== 'store' && (
          <animated.div style={optionsAnimation} className="filter-options">
            {options.map((option) => (
              <div
                key={option.value}
                className={`option-item ${
                  (type === 'category' && selectedCategory === option.value) ||
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

  const categoryOptions = [
    { value: "", label: "All Categories" },
    ...categories.map(category => ({
      value: category,
      label: category.replace(/_/g, ' ')
    }))
  ];

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
                  options={categoryOptions}
                />
                
                <FilterButton
                  type="store"
                  label="Store"
                  value={selectedStore || "All Stores"}
                  options={[]}
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
                    onChange={handleSearchChange}
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

                {!searchLoading && suggestions.length > 0 && (
                  <div className="suggestions-container">
                    <div className="suggestions-header">
                      <SearchIcon className="search-icon" />
                      <span>Suggestions</span>
                    </div>
                    <ul className="suggestions-list">
                      {suggestions.map((suggestion, index) => (
                        <li 
                          key={index}
                          className="suggestion-item"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion.title}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {!searchLoading && suggestions.length === 0 && recentQueries.length > 0 && (
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
                  <ProductsDisplay 
                    title="Search Results" 
                    products={products} 
                    favoriteIds={favoriteIds} 
                  />
                )}
              </div>
            ) : (
              <div className={`products-display-wrapper ${showChat ? 'with-chat' : ''}`}>
                {filterLoading ? (
                  <div className="loader-container">
                    <div className="loader"></div>
                  </div>
                ) : filtersApplied && products.length > 0 ? (
                  <ProductsDisplay 
                    title="Search Results" 
                    products={products} 
                    favoriteIds={favoriteIds} 
                  />
                ) : (
                  <>
                    <ProductsDisplay 
                      title="Latest in Appliances" 
                      category="Appliances" 
                      products={applianceProducts} 
                      favoriteIds={favoriteIds} 
                    />
                    <ProductsDisplay 
                      title="Latest in Musical Instruments" 
                      category="Musical_Instruments" 
                      products={musicalProducts} 
                      favoriteIds={favoriteIds} 
                    />
                    <ProductsDisplay 
                      title="Latest in Videogames" 
                      category="Videogames" 
                      products={videoGameProducts} 
                      favoriteIds={favoriteIds} 
                    />
                    <ProductsDisplay 
                      title="Latest in Clothes" 
                      category="Clothes" 
                      products={clothesProducts} 
                      favoriteIds={favoriteIds}
                    />
                  </>
                )}
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