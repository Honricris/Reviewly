import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Splash from '../pages/SplashScreen';
import Introduction from '../pages/Introduction';
import ProductsMenu from '../pages/ProductsMenu';
import ProductDetails from '../pages/ProductDetails';
import Register from '../pages/Register';
import Login from '../pages/Login'; 
import NotFound from '../pages/NotFound';
import React from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import AdminRoute from '../components/AdminRoute';
import AdminDashboard from '../pages/admin/Dashboard';
import Favourites from '../pages/Favourites';

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/introduction" element={<Introduction />} />
        


        <Route element={<ProtectedRoute />}>
          <Route path="/products/:id" element={<ProductDetails />} />
          <Route path="/products" element={<ProductsMenu />} />
          <Route path="/favourites" element={<Favourites />} />

        </Route>
       

        <Route element={<AdminRoute />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
        </Route>
       
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />}  />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default AppRoutes;

