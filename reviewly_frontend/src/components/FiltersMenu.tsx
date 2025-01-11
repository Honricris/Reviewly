import React from 'react';
import FilterListIcon from '@mui/icons-material/FilterList'; 
import '../styles/FiltersMenu.css';
import AddIcon from '@mui/icons-material/Add'; 


interface FiltersMenuProps {
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  selectedStore: string;
  setSelectedStore: (store: string) => void;
  priceRange: [number, number];
  setPriceRange: (range: [number, number]) => void;
  categoryExpanded: boolean;
  setCategoryExpanded: (expanded: boolean) => void;
  storeExpanded: boolean;
  setStoreExpanded: (expanded: boolean) => void;
  priceExpanded: boolean;
  setPriceExpanded: (expanded: boolean) => void;
}

const FiltersMenu: React.FC<FiltersMenuProps> = ({
  selectedCategory,
  setSelectedCategory,
  selectedStore,
  setSelectedStore,
  priceRange,
  setPriceRange,
  categoryExpanded,
  setCategoryExpanded,
  storeExpanded,
  setStoreExpanded,
  priceExpanded,
  setPriceExpanded,
}) => (
  <div className="filters-menu">
    <div className="filters-header">
      <FilterListIcon className="filters-icon" />
      <h3>Filters</h3>
    </div>
    <hr />
    {/* Filtros de categoría */}
    <div className="filter-button" onClick={() => setCategoryExpanded(!categoryExpanded)}>
      <h4 className="filter-text">CATEGORIES</h4>
      <AddIcon className="icon" />
    </div>
    {categoryExpanded && (
      <div className="filter-options">
        <button onClick={() => setSelectedCategory('Category1')}>Category 1</button>
        <button onClick={() => setSelectedCategory('Category2')}>Category 2</button>
        <button onClick={() => setSelectedCategory('Category3')}>Category 3</button>
      </div>
    )}

    {/* Filtros de tienda */}
    <div className="filter-button" onClick={() => setStoreExpanded(!storeExpanded)}>
      <h4 className="filter-text">STORE</h4>
      <AddIcon className="icon" />
    </div>
    {storeExpanded && (
      <div className="filter-options">
        <button onClick={() => setSelectedStore('Store1')}>Store 1</button>
        <button onClick={() => setSelectedStore('Store2')}>Store 2</button>
        <button onClick={() => setSelectedStore('Store3')}>Store 3</button>
      </div>
    )}

    {/* Filtros de precio */}
    <div className="filter-button" onClick={() => setPriceExpanded(!priceExpanded)}>
      <h4 className="filter-text">PRICE</h4>
      <AddIcon className="icon" />
    </div>
    {priceExpanded && (
      <div className="filter-options">
        <input
          type="range"
          min="0"
          max="1000"
          value={priceRange[0]}
          onChange={(e) => setPriceRange([parseInt(e.target.value), priceRange[1]])}
        />
        <input
          type="range"
          min="0"
          max="1000"
          value={priceRange[1]}
          onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
        />
        <p>${priceRange[0]} - ${priceRange[1]}</p>
      </div>
    )}
  </div>
);

export default FiltersMenu;
