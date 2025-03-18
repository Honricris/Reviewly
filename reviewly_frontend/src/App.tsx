import React from 'react';
import AppRoutes from './routes/AppRoutes';
import { AuthProvider } from './context/AuthContext';

const App = () => {
  return (
    <div className="app">
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </div>
  );
};

export default App;
