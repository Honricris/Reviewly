import '../styles/Login.css'; 
import { useNavigate } from 'react-router-dom';
import { AuthService } from '../services/authService';
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {  GoogleLogin } from '@react-oauth/google';
import { GithubLoginButton } from 'react-social-login-buttons';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();



   useEffect(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
  
      if (code) {
        handleGitHubCallback(code);
      }
    }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    try {
      const response = await AuthService.login({ email, password });
      console.log('Login successful:', response);

      const user = login(response.access_token);

      if (user?.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/products');
      }
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Invalid email or password.');
      } else if (err.response && err.response.status === 404) {
        setError('Email not found.');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };


  const handleGoogleLoginSuccess = async (credentialResponse) => {
    try {
      const response = await AuthService.googleAuth({ token: credentialResponse.credential });
      console.log('Google authentication successful:', response);

      const userData = login(response.access_token);
      navigate(userData.role === 'admin' ? '/admin/dashboard' : '/products');
    } catch (err) {
      setError('Error during Google authentication. Please try again.');
    }
  };

  const handleGoogleLoginError = () => {
    setError('Google authentication failed. Please try again.');
  };

  
  const handleGitHubLogin = () => {
      const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${import.meta.env.VITE_GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent('http://localhost:5173/login')}&scope=user:email`;
      window.location.href = githubAuthUrl;
  };
  const handleGitHubCallback = async (code) => {
      try {
        const response = await AuthService.githubAuth({ code });
        console.log('GitHub authentication successful:', response);
  
        const userData = login(response.access_token);
        navigate(userData.role === 'admin' ? '/admin/dashboard' : '/products');
      } catch (err) {
        setError('Error during GitHub authentication. Please try again.');
      }
    };
  
  

  return (
    <div className="login-container">
      <form className="form" onSubmit={handleLogin}>
        <div className="flex-column">
          <label>Email</label>
        </div>
        <div className="inputForm">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" viewBox="0 0 32 32" height="20">
            <g data-name="Layer 3" id="Layer_3">
              <path d="m30.853 13.87a15 15 0 0 0 -29.729 4.082 15.1 15.1 0 0 0 12.876 12.918 15.6 15.6 0 0 0 2.016.13 14.85 14.85 0 0 0 7.715-2.145 1 1 0 1 0 -1.031-1.711 13.007 13.007 0 1 1 5.458-6.529 2.149 2.149 0 0 1 -4.158-.759v-10.856a1 1 0 0 0 -2 0v1.726a8 8 0 1 0 .2 10.325 4.135 4.135 0 0 0 7.83.274 15.2 15.2 0 0 0 .823-7.455zm-14.853 8.13a6 6 0 1 1 6-6 6.006 6.006 0 0 1 -6 6z"></path>
            </g>
          </svg>
          <input
            placeholder="Enter your Email"
            className="input"
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="flex-column">
          <label>Password</label>
        </div>
        <div className="inputForm">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" viewBox="-64 0 512 512" height="20">
            <path d="m336 512h-288c-26.453125 0-48-21.523438-48-48v-224c0-26.476562 21.546875-48 48-48h288c26.453125 0 48 21.523438 48 48v224c0 26.476562-21.546875 48-48 48zm-288-288c-8.8125 0-16 7.167969-16 16v224c0 8.832031 7.1875 16 16 16h288c8.8125 0 16-7.167969 16-16v-224c0-8.832031-7.1875-16-16-16zm0 0"></path>
            <path d="m304 224c-8.832031 0-16-7.167969-16-16v-80c0-52.929688-43.070312-96-96-96s-96 43.070312-96 96v80c0 8.832031-7.167969 16-16 16s-16-7.167969-16-16v-80c0-70.59375 57.40625-128 128-128s128 57.40625 128 128v80c0 8.832031-7.167969 16-16 16zm0 0"></path>
          </svg>
          <input
            placeholder="Enter your Password"
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error && (
          <div style={{ color: 'red', marginBottom: '10px', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <div className="flex-row">
          <div>
            <input type="radio" />
            <label>Remember me</label>
          </div>
          <span className="span">Forgot password?</span>
        </div>
        <button type="submit" className="button-submit">Sign In</button>
        <p className="p">
          Don't have an account?{' '}
          <span className="span" onClick={() => navigate('/register')} style={{ cursor: 'pointer' }}>
            Sign Up
          </span>
        </p>
        <p className="p line">Or With</p>

        <div className="flex-row">
        <div className="w-100 p-1" style={{ height: '40px' }}>
            <GoogleLogin
              onSuccess={handleGoogleLoginSuccess}
              onError={handleGoogleLoginError}
          />
          </div>

            <GithubLoginButton onClick={handleGitHubLogin}
            style={{ height: '40px' }}  />
          
        </div>
      </form>
        
    </div>
  );
};

export default Login;