import React from 'react';

const PasswordHelper = ({ onGeneratePassword }) => {
  return (
    <div className="password-helper">
      <div className="password-requirements">
        <p>Your password must meet the following requirements:</p>
        <ul>
          <li>At least 8 characters long.</li>
          <li>At least one uppercase letter.</li>
          <li>At least one lowercase letter.</li>
          <li>At least one number.</li>
          <li>At least one special character (e.g., !@#$%^&*).</li>
        </ul>
      </div>
      <button
        type="button"
        className="generate-password-button"
        onClick={onGeneratePassword}
      >
        Generate Password
      </button>
    </div>
  );
};

export default PasswordHelper;