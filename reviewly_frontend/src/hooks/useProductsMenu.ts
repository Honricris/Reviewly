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
  const [searchQuery, setSearchQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const searchBarRef = useRef<HTMLDivElement>(null);

  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedStore, setSelectedStore] = useState<string>('');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);

  const [categoryExpanded, setCategoryExpanded] = useState(false);
  const [storeExpanded, setStoreExpanded] = useState(false);
  const [priceExpanded, setPriceExpanded] = useState(false);

  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  const fetchProducts = async (page: number = 1) => {
    setLoading(true);
    try {
      const data = await getProducts(page);
      const transformedData = data.products.map((product: any) => ({
        id: product.product_id,
        name: product.title,
        imageUrl: product.images?.[0] || 'https://via.placeholder.com/150',
        description: product.main_category,
        price: product.price,
        store: product.store,
        category: product.category,
        averageRating: product.average_rating || 0,
      }));
      setProducts(transformedData);
      setFilteredProducts(transformedData);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts(currentPage);
  }, [currentPage]);

  useEffect(() => {
    const results = products.filter((product) => {
      const matchesSearchQuery =
        product.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory =
        !selectedCategory || product.category === selectedCategory;
      const matchesStore = !selectedStore || product.store === selectedStore;
      const matchesPrice =
        product.price >= priceRange[0] && product.price <= priceRange[1];

      return (
        matchesSearchQuery &&
        matchesCategory &&
        matchesStore &&
        matchesPrice
      );
    });
    setFilteredProducts(results);
  }, [searchQuery, products, selectedCategory, selectedStore, priceRange]);

  const goToNextPage = () => {
    if (currentPage < totalPages) setCurrentPage((prev) => prev + 1);
  };

  const goToPreviousPage = () => {
    if (currentPage > 1) setCurrentPage((prev) => prev - 1);
  };

  return {
    searchQuery,
    setSearchQuery,
    isExpanded,
    setIsExpanded,
    searchBarRef,
    products,
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
    storeExpanded,
    setStoreExpanded,
    priceExpanded,
    setPriceExpanded,
    currentPage,
    totalPages,
    goToNextPage,
    goToPreviousPage,
  };
};

export default useProductsMenu;
