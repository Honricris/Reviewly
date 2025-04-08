import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { AuthService } from '../services/authService'; 

interface User {
    id: string;
    email: string;
    role: string; 
}

const AuthContext = createContext<{
    user: User | null;
    login: (token: string) => void;
    logout: () => void;
    isAdmin: () => boolean;
}>({
    user: null,
    login: () => {},
    logout: () => {},
    isAdmin: () => false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);

    const login = (token: string): User => {
        localStorage.setItem('token', token);
        const decoded = jwtDecode<User>(token);
        setUser({
            id: decoded.id,
            email: decoded.email,
            role: decoded.role
          });

        return decoded
    };

    const logout = async () => {
        await AuthService.logout();
        localStorage.removeItem('token');
        setUser(null);
    };

    const isAdmin = () => {
        return user?.role === 'admin';
    };


    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const decoded = jwtDecode<User>(token);
            setUser(decoded);
        }
    }, []);

    return (
        <AuthContext.Provider value={{ user, login, logout, isAdmin }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);