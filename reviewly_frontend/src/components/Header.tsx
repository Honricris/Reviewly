import React from 'react';
import { Link } from 'react-router-dom';
import SearchBar from './SearchBar';
import { useSearchBar } from '../hooks/useSearchBar';
import '../styles/Header.css';
import reviewlyButtonImage from '../assets/Reviewly_button.png';

const Header: React.FC<{ onSearch: (query: string) => void }> = ({ onSearch }) => {
  const { searchQuery, setSearchQuery, isExpanded, setIsExpanded, searchBarRef } = useSearchBar();

  return (
    <header className="products-menu-header">
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
