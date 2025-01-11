import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import FiltersMenu from '../components/FiltersMenu';
import ChatBubble from '../components/ChatBubble';
import useProductsMenu from '../hooks/useProductsMenu';
import Header from '../components/Header'; 
import '../styles/ProductsMenu.css';

const ProductsMenu: React.FC = () => {
  const [showChat, setShowChat] = useState(false);

  const {
    searchQuery,
    setSearchQuery,
    isExpanded,
    setIsExpanded,
    searchBarRef,
    filteredProducts,
    loading,
    error,
    selectedCategory,
    setSelectedCategory,
    selectedStore,
    setSelectedStore,
    priceRange,
    setPriceRange,
    categoryExpanded,
    setCategoryExpanded,
    currentPage,
    goToPreviousPage,
    totalPages,
    goToNextPage,
    storeExpanded,
    setStoreExpanded,
    priceExpanded,
    setPriceExpanded,
  } = useProductsMenu();

  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchBarRef.current &&
        !searchBarRef.current.contains(event.target as Node)
      ) {
        setIsExpanded(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [searchBarRef, setIsExpanded]);

  if (loading) return <div>Loading products...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="products-menu-container">
      <Header />
      <div className="products-content">
        {!showChat && (
          <FiltersMenu
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            selectedStore={selectedStore}
            setSelectedStore={setSelectedStore}
            priceRange={priceRange}
            setPriceRange={setPriceRange}
            categoryExpanded={categoryExpanded}
            setCategoryExpanded={setCategoryExpanded}
            storeExpanded={storeExpanded}
            setStoreExpanded={setStoreExpanded}
            priceExpanded={priceExpanded}
            setPriceExpanded={setPriceExpanded}
          />
        )}

        <div className="products-display-container">
          <div className="products-grid">
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                id={product.id}
                name={product.name}
                imageUrl={product.imageUrl}
                store={product.store}
                price={product.price}
                averageRating={product.averageRating}
              />
            ))}
          </div>
          <div className="pagination-controls">
            <button
              disabled={currentPage === 1}
              onClick={goToPreviousPage}
              className="pagination-button"
            >
              Previous
            </button>
            <span>Page {currentPage} of {totalPages}</span>
            <button
              disabled={currentPage === totalPages}
              onClick={goToNextPage}
              className="pagination-button"
            >
              Next
            </button>
          </div>
        </div>
      </div>
      <ChatBubble 
        onClick={toggleChat} 
        isOpen={showChat} 
        queryEndpoint="/chat/query"
        highlightedReviewIds={[]}  
        scrollToHighlightedReview={() => {}} 
      />
    </div>
  );
};

export default ProductsMenu;
