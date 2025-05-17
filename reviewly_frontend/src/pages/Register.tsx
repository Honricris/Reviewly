import React, { useState, useEffect } from 'react';
import '../styles/Login.css';
import { useNavigate } from 'react-router-dom';
import { AuthService } from '../services/authService';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import PasswordHelper from '../components/PasswordHelper';
import { useAuth } from '../context/AuthContext';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { GithubLoginButton, GoogleLoginButton } from 'react-social-login-buttons';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false); 
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      handleGitHubCallback(code);
    }
  }, []);

  const validateEmail = (email: string) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const validatePassword = (password: string) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long.';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter.';
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter.';
    }
    if (!/[0-9]/.test(password)) {
      return 'Password must contain at least one number.';
    }
    if (!/[!@#$%^&*]/.test(password)) {
      return 'Password must contain at least one special character (e.g., !@#$%^&*).';
    }
    return null;
  };

  const generateRandomPassword = () => {
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const specialChars = '!@#$%^&*';

    const allChars = lowercase + uppercase + numbers + specialChars;

    let password = '';
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += specialChars[Math.floor(Math.random() * specialChars.length)];

    for (let i = password.length; i < 12; i++) {
      password += allChars[Math.floor(Math.random() * allChars.length)];
    }

    password = password.split('').sort(() => Math.random() - 0.5).join('');
    return password;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!acceptPrivacy) {
      setError('You must accept the privacy policy to register.');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      const response = await AuthService.register({ email, password });
      console.log('Registration successful:', response);

      const userData = login(response.access_token);
      navigate(userData.role === 'admin' ? '/admin/dashboard' : '/products');
    } catch (err) {
      console.error('Error during registration:', err);

      if (err.response) {
        console.error('Response data:', err.response.data);

        if (err.response.status === 409) {
          const errorMessage = err.response.data.message || 'User with that email already exists.';
          setError(errorMessage);
        } else {
          setError('Error registering user. Please try again.');
        }
      } else {
        setError('Network error or server is unavailable. Please try again.');
      }
    }
  };

  const handleGoogleLoginSuccess = async (credentialResponse) => {
    if (!acceptPrivacy) {
      setError('You must accept the privacy policy to register.');
      return;
    }

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
    if (!acceptPrivacy) {
      setError('You must accept the privacy policy to register.');
      return;
    }

    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${import.meta.env.VITE_GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent('http://localhost:5173/register')}&scope=user:email`;
    window.location.href = githubAuthUrl;
  };

  const handleGitHubCallback = async (code) => {
    if (!acceptPrivacy) {
      setError('You must accept the privacy policy to register.');
      return;
    }

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
    <div className="register-container">
      <form className="form" onSubmit={handleRegister}>
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
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <span
            className="password-toggle"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
          </span>
        </div>

        <div className="flex-column">
          <label>Confirm Password</label>
        </div>
        <div className="inputForm">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" viewBox="-64 0 512 512" height="20">
            <path d="m336 512h-288c-26.453125 0-48-21.523438-48-48v-224c0-26.476562 21.546875-48 48-48h288c26.453125 0 48 21.523438 48 48v224c0 26.476562-21.546875 48-48 48zm-288-288c-8.8125 0-16 7.167969-16 16v224c0 8.832031 7.1875 16 16 16h288c8.8125 0 16-7.167969 16-16v-224c0-8.832031-7.1875-16-16-16zm0 0"></path>
            <path d="m304 224c-8.832031 0-16-7.167969-16-16v-80c0-52.929688-43.070312-96-96-96s-96 43.070312-96 96v80c0 8.832031-7.167969 16-16 16s-16-7.167969-16-16v-80c0-70.59375 57.40625-128 128-128s128 57.40625 128 128v80c0 8.832031-7.167969 16-16 16zm0 0"></path>
          </svg>
          <input
            placeholder="Confirm your Password"
            className="input"
            type={showConfirmPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <span
            className="password-toggle"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
          </span>
        </div>

        {/* Privacy Policy Checkbox */}
        <div className="flex-row" style={{ marginTop: '10px', alignItems: 'center' }}>
          <input
            type="checkbox"
            id="acceptPrivacy"
            checked={acceptPrivacy}
            onChange={(e) => setAcceptPrivacy(e.target.checked)}
            style={{ marginRight: '10px' }}
          />
          <label htmlFor="acceptPrivacy" style={{ fontSize: '14px', color: '#151717' }}>
            I accept the{' '}
            <span
              className="span"
              onClick={() => setShowPrivacyModal(true)}
              style={{ cursor: 'pointer' }}
            >
              Privacy Policy
            </span>
          </label>
        </div>

        {error && (
          <div style={{ color: 'red', marginBottom: '10px', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <button type="submit" className="button-submit">Sign Up</button>
        <p className="p">
          Already have an account?{' '}
          <span className="span" onClick={() => navigate('/login')} style={{ cursor: 'pointer' }}>
            Sign In
          </span>
        </p>
        <p className="p line">Or With</p>

        <div className="flex-row">
          <GoogleLogin
            onSuccess={handleGoogleLoginSuccess}
            onError={handleGoogleLoginError}
          />
          <GithubLoginButton
            onClick={handleGitHubLogin}
            style={{ height: '40px' }}
          />
        </div>
      </form>

      {/* Privacy Policy Modal */}
      {showPrivacyModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Privacy Policy</h2>
            <div className="modal-body">
              <p>
                <strong>1. Responsible Party</strong><br />
                Reviewly, located at C/Ruby León 24007, is responsible for processing your personal data.
              </p>
              <p>
                <strong>2. Data Collected</strong><br />
                We collect: email address, GitHub ID, IP address, login timestamps, and search queries you submit.
              </p>
              <p>
                <strong>3. Purpose</strong><br />
                Your data is used to manage your account, provide our services, ensure security, and improve our platform.
              </p>
              <p>
                <strong>4. Legal Basis</strong><br />
                We process your data based on your consent and the need to fulfill our contract with you.
              </p>
              <p>
                <strong>5. Data Retention</strong><br />
                We keep your data only as long as necessary for the purposes described or as required by law.
              </p>
              <p>
                <strong>6. Data Sharing</strong><br />
                We may share your data with third-party services (e.g., Google, GitHub) for authentication. These parties are GDPR-compliant.
              </p>
              <p>
                <strong>7. Your Rights</strong><br />
                You have the right to access, rectify, delete, restrict, or port your data. Contact us at email@example.com to exercise these rights.
              </p>
              <p>
                <strong>8. Security</strong><br />
                We use encryption and other measures to protect your data.
              </p>
              <p>
                <strong>9. Contact</strong><br />
                For questions, contact us at email@example.com.
              </p>
            </div>
            <button
              className="modal-close-button"
              onClick={() => setShowPrivacyModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      <PasswordHelper
        onGeneratePassword={() => {
          const randomPassword = generateRandomPassword();
          setPassword(randomPassword);
          setConfirmPassword(randomPassword);
        }}
      />
    </div>
  );
};

export default Register;