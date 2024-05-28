import React from 'react';
import logoAnimation from './logoAnimation.gif';
import './Loader.css'; // Import CSS file for Loader component styles

const Loader = () => (
  <div className="loader-overlay">
    <div className="loader-content">
      <img src={logoAnimation} className="red-logo" alt="logo animation" />
    </div>
  </div>
);

export default Loader;
