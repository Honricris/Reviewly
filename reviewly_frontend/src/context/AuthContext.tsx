import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import { AuthService } from '../services/authService';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean; 
  login: (token: string) => User;
  logout: () => void;
  isAdmin: () => boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: false,
  login: () => ({} as User),
  logout: () => {},
  isAdmin: () => false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); 

  const login = (token: string): User => {
    localStorage.setItem('token', token);
    const decoded = jwtDecode<User>(token);
    setUser({
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
    });
    setIsLoading(false);
    return decoded;
  };

  const logout = async () => {
    await AuthService.logout();
    localStorage.removeItem('token');
    setUser(null);
    setIsLoading(false); 
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode<User>(token);
        setUser(decoded);
      } catch (error) {
        console.error('Error decoding token:', error);
        localStorage.removeItem('token'); 
      }
    }
    setIsLoading(false); 
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);