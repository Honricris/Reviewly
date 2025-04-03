import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
    const { user, isAdmin } = useAuth();
    const location = useLocation();

    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    const isAdminRoute = location.pathname.startsWith('/admin');

    if (isAdminRoute && !isAdmin()) {
        return <Navigate to="/products" replace />;
    }

    if (!isAdminRoute && isAdmin()) {
        return <Navigate to="/admin/dashboard" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;