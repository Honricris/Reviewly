// src/hooks/useProductsMenu.ts
import { useState, useEffect, useRef } from 'react';
import { getProducts } from '../services/productService';

interface Product {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
  price: number;
  store: string;
  category: string;
  averageRating: number;
}


const useProductsMenu = () => {
  const [applianceProducts, setApplianceProducts] = useState<Product[]>([]);
  const [musicalProducts, setMusicalProducts] = useState<Product[]>([]);
  const [videoGameProducts, setVideoGameProducts] = useState<Product[]>([]);  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProductsByCategory = async (category: string) => {
    try {
      const data = await getProducts(1, 8, category);
      return data.products.map((product: any) => ({
        id: product.product_id,
        name: product.title,
        imageUrl: product.images?.[0] || 'https://via.placeholder.com/150',
        price: product.price,
        store: product.store,
        category: product.category,
        averageRating: product.average_rating || 0,
      }));
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching products');
      return [];
    }
  };

  const fetchAllCategories = async () => {
    setLoading(true);
    try {
      const appliances = await fetchProductsByCategory('Appliances');
      const musical = await fetchProductsByCategory('Musical_Instruments');
      const videoGames = await fetchProductsByCategory('Videogames'); // Obtener productos de Video Games

      setApplianceProducts(appliances);
      setMusicalProducts(musical);
      setVideoGameProducts(videoGames); 
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllCategories();
  }, []);

  return {
    applianceProducts,
    videoGameProducts,  

    musicalProducts,
    loading,
    error,
  };
};

export default useProductsMenu;
