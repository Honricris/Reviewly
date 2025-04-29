import React, { useState, useEffect } from 'react';
import ProductsDisplay from '../components/ProductsDisplay';
import Header from '../components/Header';
import '../styles/ProductsMenu.css';
import { getProductById } from '../services/productService';
import userService from '../services/userService';

const Favourites: React.FC = () => {
  const [favoriteProducts, setFavoriteProducts] = useState<any[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchActive, setSearchActive] = useState(false);

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        setLoading(true);
        // Obtener los IDs de favoritos
        const ids = await userService.getFavorites();
        setFavoriteIds(ids);

        if (ids.length === 0) {
          setFavoriteProducts([]);
          setLoading(false);
          return;
        }

        // Obtener detalles de los productos favoritos
        const productPromises = ids.map(id => getProductById(id.toString()));
        const products = await Promise.all(productPromises);
        setFavoriteProducts(products);
      } catch (err) {
        console.error('Error fetching favorites:', err);
        setError('Failed to load favorite products');
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);

  const handleSearchFocus = () => {
    setSearchActive(true);
  };

  const handleSearchBlur = () => {};

  const handleSearch = (query: string) => {
    console.log('Search query:', query);
  };

  return (
    <div className="products-menu-container">
      {loading && <div>Loading favorite products...</div>}
      {error && <div>Error: {error}</div>}
      {!loading && !error && (
        <>
          <Header 
            onSearch={handleSearch}
            onSearchFocus={handleSearchFocus}
            onSearchBlur={handleSearchBlur}
          />
          <div className="products-content">
            <div className="inspiration-container">
              <div className="inspiration-text">
                <h2>Your Favorites</h2>
                <p>View and manage your favorite products all in one place.</p>
              </div>
            </div>

            {favoriteProducts.length > 0 ? (
              <div className="products-display-wrapper">
                <ProductsDisplay 
                  title="Your Favorite Products" 
                  products={favoriteProducts}
                  favoriteIds={favoriteIds} // Pasamos favoriteIds como prop
                />
              </div>
            ) : (
              <div className="no-favorites-message">
                <p>You haven't added any favorite products yet.</p>
                <p>Start exploring products and add your favorites!</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Favourites;