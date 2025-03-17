import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Splash from '../pages/SplashScreen';
import Introduction from '../pages/Introduction';
import ProductsMenu from '../pages/ProductsMenu';
import ProductDetails from '../pages/ProductDetails';
import Register from '../pages/Register';
import Login from '../pages/Login'; 
import NotFound from '../pages/NotFound';
import React from 'react';

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/introduction" element={<Introduction />} />
        <Route path="/products" element={<ProductsMenu />} />
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />}  />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default AppRoutes;

