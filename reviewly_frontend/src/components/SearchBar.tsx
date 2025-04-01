import React, { FC } from 'react';
import '../styles/SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isExpanded?: boolean;
  onBarClick?: () => void;
  searchBarRef?: React.RefObject<HTMLDivElement>;
  onFocus?: () => void;
  onBlur?: () => void;
}

const SearchBar: FC<SearchBarProps> = ({ 
  onSearch, 
  isExpanded, 
  onBarClick, 
  searchBarRef,
  onFocus,
  onBlur 
}) => {
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSearch(event.target.value);
  };

  return (
    <div 
      className={`search-container ${isExpanded ? 'expanded' : ''}`} 
      onClick={onBarClick}
      ref={searchBarRef}
    >
      <input
        type="text"
        placeholder="Search something...."
        onChange={handleInputChange}
        className="search-input"
        onFocus={onFocus}
        onBlur={onBlur}
      />
    </div>
  );
};

export default SearchBar;