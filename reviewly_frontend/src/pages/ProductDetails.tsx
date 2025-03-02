import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { getProductById, getProductReviews } from '../services/productService';
import '../styles/ProductDetails.css';
import ChatBubble from '../components/ChatBubble';
import { Rating, Button } from '@mui/material';
import Header from '../components/Header';

const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [highlightedReviewIds, setHighlightedReviewIds] = useState<number[]>([]);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const reviewsContainerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  useEffect(() => {
    const fetchProductDetails = async () => {
      try {
        const productData = await getProductById(id!);
        setProduct(productData);
        setSelectedImage(productData.images[0].large);
      } catch (err) {
        setError('Failed to fetch product details.');
      } finally {
        setLoading(false);
      }
    };

    const fetchProductReviews = async (page: number) => {
      try {
        setReviewsLoading(true);
        const reviewsData = await getProductReviews(id!, page);
        setReviews(reviewsData.reviews || []);
        setTotalPages(reviewsData.total_pages || 1);
      } catch (err) {
        console.error('Error fetching reviews:', err);
        setReviews([]);
      } finally {
        setReviewsLoading(false);
      }
    };
  
    fetchProductDetails();
    fetchProductReviews(currentPage);
  }, [id, currentPage]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!reviewsContainerRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - reviewsContainerRef.current.offsetLeft);
    setScrollLeft(reviewsContainerRef.current.scrollLeft);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !reviewsContainerRef.current) return;
    e.preventDefault();
    const x = e.pageX - reviewsContainerRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    reviewsContainerRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handlePageChange = async (direction: 'previous' | 'next') => {
    if (direction === 'previous' && currentPage > 1) {
      setCurrentPage((prevPage) => prevPage - 1);
    } else if (direction === 'next' && currentPage < totalPages) {
      setCurrentPage((prevPage) => prevPage + 1);
    }
  };

  const SearchHandler = () => {};


  const handleImageClick = (image: string) => {
    setSelectedImage(image);
  };

  const handleChatResponse = (botAnswer: { answer: string; reviews: number[] }) => {
    
    setHighlightedReviewIds(botAnswer.reviews || []);
  };

  const scrollToHighlightedReview = async (reviewId: number) => {
    console.log(`Attempting to scroll to review with ID: ${reviewId}`);
  
    let found = false;
    let page = 1;
  
    while (!found && page <= totalPages) {
      console.log(`Checking page: ${page}`);
      
      const reviewsData = await getProductReviews(id!, page);
  
      const reviewIndex = reviewsData.reviews.findIndex((review: any) => review.review_id === reviewId);
  
      if (reviewIndex !== -1) {
        found = true;
        console.log(`Review found on page ${page} at index ${reviewIndex}`);
        setCurrentPage(page);
  
        setTimeout(() => {
          const reviewElement = document.getElementById(`review-${reviewId}`);
          if (reviewElement) {
            console.log(`Scrolling to review element with ID: review-${reviewId}`);
            
            reviewElement.scrollIntoView({
              behavior: 'smooth',
              block: 'center',
              inline: 'center',
            });
          } else {
            console.error(`Review element with ID review-${reviewId} not found.`);
          }
        }, 500); 
      } else {
        page++;
      }
    }
  
    if (!found) {
      console.error(`Review with ID ${reviewId} not found in any page.`);
    }
  };
  

  if (loading) return <div>Loading product details...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="product-details-container">
      <Header onSearch={SearchHandler}/>
      <h1>{product.title}</h1>
      <div className={`content-layout ${isChatOpen ? 'chat-open' : ''}`}>
        <div className="product-layout">
          <div className="product-images">
            <div className="main-image">
              <img src={selectedImage} alt={product.title} />
            </div>
            <div className="thumbnail-images">
              {product.images.map((image: any, index: number) => (
                <img
                  key={index}
                  src={image.large}
                  alt={`Thumbnail ${index}`}
                  onClick={() => handleImageClick(image.large)}
                  className="thumbnail"
                />
              ))}
            </div>
          </div>
          <div className="product-details">
            {product.price !== 0 && <p><strong>Price:</strong> ${product.price}</p>}
            {product.description.length > 0 && <p><strong>Description:</strong> {product.description}</p>}
            <p>
              <strong>Average Rating:</strong>
              <span className="rating-container">
                <Rating value={product.average_rating} precision={0.1} readOnly size="small" />
                <span className="rating-text">
                  {product.average_rating} ({product.rating_number} reviews)
                </span>
              </span>
            </p>
            <h2>Features:</h2>
            <ul>
              {product.features.map((feature: string, index: number) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="reviews-section">
          <h2>Reviews</h2>
          <hr className="section-divider" />
          <div className="reviews-wrapper">
            <Button
              variant="contained"
              color="primary"
              onClick={() => handlePageChange('previous')}
              disabled={currentPage === 1}
            >
              Previous Page
            </Button>
            <div
              className="reviews-container"
              ref={reviewsContainerRef}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            >
              {reviewsLoading ? (
                <div>Loading reviews...</div>
              ) : reviews.length > 0 ? (
                <div className="reviews-carousel">
                  {reviews.map((review, index) => (
                    <div
                      id={`review-${review.review_id}`}
                      key={index}
                      className={`review-card ${
                        highlightedReviewIds.includes(review.review_id) ? 'highlighted' : ''
                      }`}
                    >
                      <h3>{review.title}</h3>
                      <p>{review.text}</p>
                      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Rating
                          name={`review-rating-${index}`}
                          value={review.rating}
                          precision={0.1}
                          readOnly
                          size="small"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No reviews available for this product.</p>
              )}
            </div>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handlePageChange('next')}
              disabled={currentPage === totalPages}
            >
              Next Page
            </Button>
          </div>
          <p>Page {currentPage} of {totalPages}</p>
        </div>
        <a href={product.amazon_link} target="_blank" rel="noopener noreferrer">View on Amazon</a>
      </div>

      <ChatBubble 
        onClick={() => setIsChatOpen(!isChatOpen)} 
        isOpen={isChatOpen} 
        productId={id} 
        onResponse={handleChatResponse}
        scrollToHighlightedReview={scrollToHighlightedReview}
      />
    </div>
  );
};

export default ProductDetails;
