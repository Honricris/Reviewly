import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import SearchBar from './SearchBar';
import { useSearchBar } from '../hooks/useSearchBar';
import '../styles/Header.css';
import reviewlyButtonImage from '../assets/Reviewly_button.png';

const Header: React.FC<{ onSearch: (query: string) => void }> = ({ onSearch }) => {
  const { searchQuery, setSearchQuery, isExpanded, setIsExpanded, searchBarRef } = useSearchBar();
  const [isHeaderVisible, setIsHeaderVisible] = useState(true);

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY === 0) {
        // Si está en la parte superior, asegúrate de que el header esté visible
        setIsHeaderVisible(true);
      } else if (currentScrollY > lastScrollY) {
        // Scroll hacia abajo
        setIsHeaderVisible(false);
      } else {
        // Scroll hacia arriba
        setIsHeaderVisible(true);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <header
      className="products-menu-header"
      style={{
        transform: isHeaderVisible ? 'translateY(0)' : 'translateY(-100%)',
        transition: 'transform 0.3s ease-in-out',
      }}
    >
      <Link to="/products" className="home-button">
        <img src={reviewlyButtonImage} alt="Go to Products" className="home-button-image" />
      </Link>
      <SearchBar
        onSearch={(query) => {
          setSearchQuery(query);
          onSearch(query);
        }}
        isExpanded={isExpanded}
        onBarClick={() => setIsExpanded(!isExpanded)}
        searchBarRef={searchBarRef}
      />
    </header>
  );
};

export default Header;