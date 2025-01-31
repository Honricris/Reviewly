import React from 'react';
import ProductCard from './ProductCard';

interface ProductsDisplayProps {
  title: string;
  
    products: {
      product_id: number;
      title: string;
      images: string;
      store: string;
      price: number;
      average_rating: number;
    }[];
 
}


const ProductsDisplay: React.FC<ProductsDisplayProps> = ({ title, products }) => {
  const productList = products || []; 

  console.log("Products received:", productList); 
  console.log("Number of products:", productList.length);

  return (
    <div className="products-display-container">
      <h2 className="products-title">{title}</h2>
      <div className="products-grid">
        {productList.length > 0 ? (
          productList.map((product) => (
            <ProductCard
              key={product.product_id} 
              id={product.product_id}
              name={product.title} 
              imageUrl={product.images.length > 0 ? product.images[0] : ""}
              store={product.store}
              price={product.price}
              averageRating={product.average_rating} 
            />
          ))
        ) : (
          <p>No products found</p>
        )}
      </div>
    </div>
  );
};

export default ProductsDisplay;
