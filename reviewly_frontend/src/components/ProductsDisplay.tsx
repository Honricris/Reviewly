import React, { useEffect, useState } from 'react';
import ProductCard from './ProductCard';
import { Button, Stack } from '@mui/material';
import { getProducts } from '../services/productService';

interface ProductsDisplayProps {
  title: string;
  category?: string;
  products: {
    product_id: number;
    title: string;
    images: string;
    store: string;
    price: number;
    average_rating: number;
  }[];
  onPageChange?: (page: number) => void;
}

const ProductsDisplay: React.FC<ProductsDisplayProps> = ({
  title,
  category,
  products,
}) => {
  const [productList, setProductList] = useState(products);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchProducts = async (page: number) => {
      if (category) {
        setLoading(true);
        const response = await getProducts(page, 8, category);
        setProductList(response.products);
        setTotalPages(response.total_pages);
        setLoading(false);
      }
    };

    if (!category && products.length > 0) {
      // Si se pasan productos directamente, solo se muestran sin hacer llamada a la API
      setProductList(products);
      setTotalPages(1); // Solo una página si no estamos haciendo búsqueda
    } else {
      fetchProducts(currentPage);
    }
  }, [category, products, currentPage]);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    if (category) {
      setLoading(true);
      getProducts(newPage, 8, category).then((response) => {
        setProductList(response.products);
        setTotalPages(response.total_pages);
        setLoading(false);
      });
    }
  };

  return (
    <div className="products-display-container">
      <h2 className="products-title">{title}</h2>
      <div className="products-grid">
        {loading ? (
          <p>Loading...</p>
        ) : productList.length > 0 ? (
          productList.map((product) => (
            <ProductCard
              key={product.product_id}
              id={product.product_id}
              name={product.title}
              imageUrl={product.images.length > 0 ? product.images[0] : ''}
              store={product.store}
              price={product.price}
              averageRating={product.average_rating}
            />
          ))
        ) : (
          <p>No products found</p>
        )}
      </div>

      {category && (
        <div className="pagination-container">
          <Stack direction="row" spacing={2} justifyContent="center" style={{ marginTop: '20px' }}>
            <Button
              variant="outlined"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>

            <span>
              Page {currentPage} of {totalPages}
            </span>

            <Button
              variant="outlined"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages || productList.length === 0}
            >
              Next
            </Button>
          </Stack>
        </div>
      )}
    </div>
  );
};

export default ProductsDisplay;
