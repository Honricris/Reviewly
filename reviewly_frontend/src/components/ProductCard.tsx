import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ProductCard.css';
import { Rating } from '@mui/material';

interface ProductCardProps {
  id: number;
  name: string;
  imageUrl: string;
  store: string;
  price: number;
  averageRating: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ id, name, imageUrl, store, price, averageRating }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/products/${id}`);
  };

  return (
    <div className="product-card" onClick={handleClick}>
      <img src={imageUrl} alt={name} />
      <div className="product-card-details">
        <h3 className="product-name">{name}</h3>
        <p className="product-store">{store}</p>
        <div className="product-price-rating">
          {price > 0 && <span className="product-price">${price.toFixed(2)}</span>}
          <span className="product-rating">
            <Rating value={averageRating} precision={0.1} readOnly size="small" />
          </span>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
