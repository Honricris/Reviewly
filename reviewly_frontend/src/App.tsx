import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import AppRoutes from './routes/AppRoutes';
import { AuthProvider } from './context/AuthContext';
import { GoogleOAuthProvider } from '@react-oauth/google';

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const App = () => {
  return (
    <div className="app">
      <GoogleOAuthProvider clientId={clientId}>
        <AuthProvider>
          <Router> 
            <AppRoutes />
          </Router>
        </AuthProvider>
      </GoogleOAuthProvider>
    </div>
  );
};

export default App;