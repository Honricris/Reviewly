import React, { useState } from 'react';
import ProductsDisplay from '../components/ProductsDisplay';
import useProductsMenu from '../hooks/useProductsMenu';
import Header from '../components/Header';
import FiltersMenu from '../components/FiltersMenu'; // Asegúrate de importar correctamente este componente
import '../styles/ProductsMenu.css';
import ChatBubble  from '../components/ChatBubble';
import { getProducts } from '../services/productService';

const ProductsMenu: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const { applianceProducts, musicalProducts,videoGameProducts, loading, error } = useProductsMenu();
  const [products, setProducts] = useState<any[]>([]);
  
  const [showChat, setShowChat] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string >("");
  const [selectedStore, setSelectedStore] = useState<string >("");
  const [priceRange, setPriceRange] = useState<[number, number] >([0,1]);
  const [categoryExpanded, setCategoryExpanded] = useState(false);
  const [storeExpanded, setStoreExpanded] = useState(false);
  const [priceExpanded, setPriceExpanded] = useState(false);

  if (loading) return <div>Loading products...</div>;
  if (error) return <div>Error: {error}</div>;


  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    const fetchedProducts = await getProducts(1, 10, undefined, query);
    setProducts(fetchedProducts.products);
  };
  
  return (
    <div className="products-menu-container">
      <Header onSearch={handleSearch} />
      <div className="products-content">
        {/* Filtros */}
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

        {/* Productos */}
        <div className="products-display-wrapper">
          {searchQuery ? (
            <ProductsDisplay title="Search Results" products={products} />
          ) : (
            <>
              <ProductsDisplay title="Latest in Appliances" products={applianceProducts} />
              <ProductsDisplay title="Latest in Musical Instruments" products={musicalProducts} />
              <ProductsDisplay title="Latest in Video Games" products={videoGameProducts} />
            </>
          )}
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
