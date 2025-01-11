import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import splashGif from '../assets/Review.gif'; 
import '../styles/SplashScreen.css';


const SplashScreen = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/introduction'); 
    }, 3000); 
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="splash-container">
      <img src={splashGif} alt="Splash Logo" className="splash-image" />
    </div>
  );
};

export default SplashScreen;
