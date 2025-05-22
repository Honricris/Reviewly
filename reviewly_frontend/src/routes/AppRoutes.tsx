import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
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
import UserManagementPage from '../pages/admin/UserManagementPage';
import ReportGeneratorPage from '../pages/admin/ReportGeneratorPage';
import { useAuth } from '../context/AuthContext';

const AppRoutes = () => {
  const { user, isAdmin, isLoading } = useAuth();
  const location = useLocation(); // Now safe, as AppRoutes is inside <Router>

  // Redirect admins to /admin/dashboard on any non-admin route
  if (!isLoading && user && isAdmin() && !location.pathname.startsWith('/admin')) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  const RootRedirect = () => {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    if (user && isAdmin()) {
      return <Navigate to="/admin/dashboard" replace />;
    }
    if (user) {
      return <Navigate to="/products" replace />;
    }
    return <Splash />;
  };

  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/introduction" element={<Introduction />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/products" element={<ProductsMenu />} />
        <Route path="/favourites" element={<Favourites />} />
      </Route>

      <Route element={<AdminRoute />}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<UserManagementPage />} />
        <Route path="/admin/reports" element={<ReportGeneratorPage />} />
      </Route>

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AppRoutes;