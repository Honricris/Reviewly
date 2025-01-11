import React, { FC } from 'react';
import '../styles/SearchBar.css';
import SearchIcon from '@mui/icons-material/Search';  

interface SearchBarProps {
  onSearch: (query: string) => void;
  isExpanded: boolean;
  onBarClick: () => void;
  searchBarRef: React.RefObject<HTMLDivElement>;
}

const SearchBar: FC<SearchBarProps> = ({ onSearch, isExpanded, onBarClick, searchBarRef }) => {
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSearch(event.target.value);
  };

  return (
    <div
      ref={searchBarRef}
      className={`search-bar-container ${isExpanded ? 'expanded' : ''}`}
      onClick={onBarClick}
    >
      <span className="search-icon">
        <SearchIcon style={{ fontSize: 24 }} />  
      </span>
      <input
        type="text"
        placeholder="Search for a product..."
        onChange={handleInputChange}
        className="search-bar-input"
      />
    </div>
  );
};

export default SearchBar;
