import React from 'react';
import ProductCard from './ProductCard';

interface ProductsDisplayProps {
  title: string;
  products: {
    id: number;
    name: string;
    imageUrl: string;
    store: string;
    price: number;
    averageRating: number;
  }[];
}

const ProductsDisplay: React.FC<ProductsDisplayProps> = ({ title, products }) => {
  return (
    <div className="products-display-container">
      <h2 className="products-title">{title}</h2>
      <div className="products-grid">
        {products.map((product) => (
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
    </div>
  );
};

export default ProductsDisplay;
