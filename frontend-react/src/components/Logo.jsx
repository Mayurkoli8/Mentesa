import React from 'react';

// Renders the actual Mentesa logo image at a given size.
const Logo = ({ size = 36, className = '' }) => (
    <img
        src="/logo.png"
        alt="Mentesa logo"
        width={size}
        height={size}
        className={`mts-logo ${className}`}
        style={{ width: size, height: size, objectFit: 'contain' }}
    />
);

export default Logo;
