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
  const [applianceProducts, setApplianceProducts] = useState<any[]>([]);
  const [musicalProducts, setMusicalProducts] = useState<any[]>([]);
  const [videoGameProducts, setVideoGameProducts] = useState<any[]>([]);  
  const [clothesProducts, setClothesProducts] = useState<any[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProductsByCategory = async (category: string) => {
    try {
      const data = await getProducts(1, 7, category);
      return data.products
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
      const videoGames = await fetchProductsByCategory('Videogames'); 
      const clothes = await fetchProductsByCategory('Clothes'); 


      setApplianceProducts(appliances);
      setMusicalProducts(musical);
      setVideoGameProducts(videoGames); 
      setClothesProducts(clothes);
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
    clothesProducts,
    musicalProducts,
    loading,
    error,
  };
};

export default useProductsMenu;
