import React, { useState, useEffect } from 'react';
import ProductsDisplay from '../components/ProductsDisplay';
import useProductsMenu from '../hooks/useProductsMenu';
import Header from '../components/Header';
import FiltersMenu from '../components/FiltersMenu'; 
import '../styles/ProductsMenu.css';
import ChatBubble from '../components/ChatBubble';
import { getProducts } from '../services/productService';

const ProductsMenu: React.FC = () => {
  const { applianceProducts, musicalProducts, videoGameProducts,clothesProducts, loading, error } = useProductsMenu();
  const [products, setProducts] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showChat, setShowChat] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedStore, setSelectedStore] = useState<string>("");
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1]);
  const [categoryExpanded, setCategoryExpanded] = useState(false);
  const [storeExpanded, setStoreExpanded] = useState(false);
  const [priceExpanded, setPriceExpanded] = useState(false);

  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };


  const setGridMinHeight = () => {
    const grid = document.querySelector('.products-grid') as HTMLElement;
    if (!grid) return;

    const currentHeight = grid.offsetHeight;
    grid.style.minHeight = `${currentHeight}px`;
  };

  
  useEffect(() => {
    const delaySearch = setTimeout(async () => {
      console.log(searchQuery)
      if (searchQuery.trim() === "") {
        setProducts([]); 
        return;
      }

      setGridMinHeight();

      const fetchedProducts = await getProducts(1, 70, undefined, searchQuery);
      setProducts(fetchedProducts.products);
    }, 300);

    return () => clearTimeout(delaySearch);
  }, [searchQuery]);

  return (
    <div className="products-menu-container">
      {loading && <div>Loading products...</div>}
      {error && <div>Error: {error}</div>}
      {!loading && !error && (
        <>
          <Header onSearch={setSearchQuery} />
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

            <div className={`products-display-wrapper ${showChat ? 'with-chat' : ''}`}>

               {products.length > 0 ? (
                <ProductsDisplay title="Search Results" products={products} />
              ) : (
                <>
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
                </>
              )}
            </div>
          </div>
          <ChatBubble
            onClick={toggleChat}
            isOpen={showChat}
            onResponse={(botAnswer) => {
              if (botAnswer.text === "No products found.") {
                
              } else {
                if (botAnswer.products ) {
                  setProducts(botAnswer.products);
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
