import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';
import { useSearchBar } from '../hooks/useSearchBar';
import '../styles/Header.css';
import reviewlyButtonImage from '../assets/Reviewly_button.png';
import { useAuth } from '../context/AuthContext';

interface HeaderProps {
  onSearch?: (query: string) => void;
  onSearchFocus?: () => void;
  onSearchBlur?: () => void;
  buttonConfig?: {
    showHome?: boolean;
    showFavourites?: boolean;
    showLogout?: boolean;
    isAdmin?: boolean;
  };
  showSearchBar?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  onSearch,
  onSearchFocus,
  onSearchBlur,
  buttonConfig = { showHome: true, showFavourites: true, showLogout: true, isAdmin: false },
  showSearchBar = true,
}) => {
  const { searchQuery, setSearchQuery, isExpanded, setIsExpanded, searchBarRef } = useSearchBar();
  const [isHeaderVisible, setIsHeaderVisible] = useState(true);
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    let lastScrollY = window.scrollY;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      if (currentScrollY === 0) {
        setIsHeaderVisible(true);
      } else if (currentScrollY > lastScrollY) {
        setIsHeaderVisible(false);
      } else {
        setIsHeaderVisible(true);
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleHome = () => {
    navigate('/products');
  };

  const handleFavourites = () => {
    navigate('/favourites');
  };

  const handleLogout = async () => {
    try {
      await logout();
      setSearchQuery('');
      navigate('/login');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

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

      <div className="home-link-container">
        {buttonConfig.showHome && (
          <button onClick={handleHome} className="nav-button">
            Home
          </button>
        )}
        {buttonConfig.showFavourites && (
          <button onClick={handleFavourites} className="nav-button">
            Favourites
          </button>
        )}
        {buttonConfig.isAdmin && (
          <>
            <button onClick={() => navigate('/admin/users')} className="nav-button">
              Manage Users
            </button>
            <button onClick={() => navigate('/admin/reports')} className="nav-button">
              Generate Report
            </button>
          </>
        )}
        {buttonConfig.showLogout && (
          <button onClick={handleLogout} className="nav-button">
            Logout
          </button>
        )}
      </div>

      {showSearchBar && (
        <div className="search-bar-container">
          <SearchBar
            onSearch={(query) => {
              setSearchQuery(query);
              onSearch?.(query);
            }}
            onBarClick={() => setIsExpanded(!isExpanded)}
            searchBarRef={searchBarRef}
            onFocus={onSearchFocus}
            onBlur={onSearchBlur}
          />
        </div>
      )}

      {buttonConfig.isAdmin && (
        <div className="admin-indicator">
          <span className="admin-text">Admin</span>
          <div className="admin-icon">A</div>
        </div>
      )}
    </header>
  );
};

export default Header;