import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ProductCard.css';
import { Rating } from '@mui/material';
import userService from '../services/userService';

interface ProductCardProps {
  id: number;
  name: string;
  imageUrl: string;
  store: string;
  price: number;
  averageRating: number;
  favoriteIds: number[]; 
}

const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  imageUrl,
  store,
  price,
  averageRating,
  favoriteIds,
}) => {
  const navigate = useNavigate();
  const [isFavorited, setIsFavorited] = useState(favoriteIds.includes(id)); 

  const handleClick = () => {
    navigate(`/products/${id}`);
  };

  const handleLikeClick = async (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();

    const newFavoriteState = e.target.checked;

    if (newFavoriteState) {
      const success = await userService.addFavorite(id);
      if (success) {
        setIsFavorited(true);
      } else {
        e.target.checked = false;
      }
    } else {
      const success = await userService.removeFavorite(id);
      if (success) {
        setIsFavorited(false);
      } else {
        e.target.checked = true;
      }
    }
  };

  const handleLabelClick = (e: React.MouseEvent<HTMLLabelElement>) => {
    e.stopPropagation();
  };

  return (
    <div className="product-card" onClick={handleClick}>
      <div className="product-image-container">
        <img src={imageUrl} alt={name} />
        <label className="ui-bookmark like-button" onClick={handleLabelClick}>
          <input
            type="checkbox"
            checked={isFavorited}
            onChange={handleLikeClick}
          />
          <div className="bookmark">
            <svg
              viewBox="0 0 16 16"
              style={{ marginTop: '4px' }}
              className="bi bi-heart-fill"
              height="25"
              width="25"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"
                fillRule="evenodd"
              />
            </svg>
          </div>
        </label>
      </div>
      <div className="product-card-details">
        <p className="product-store">{store}</p>
        <h3 className="product-name">{name}</h3>
        <div className="price-rating-container">
          <span className="product-price">${price > 0 ? price.toFixed(2) : 'N/A'}</span>
          <Rating
            value={averageRating}
            precision={0.1}
            readOnly
            size="small"
            className="product-rating"
          />
        </div>
      </div>
    </div>
  );
};

export default ProductCard;