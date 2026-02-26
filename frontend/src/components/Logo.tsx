import React from 'react';

interface LogoProps {
  className?: string;
  onClick?: () => void;
}

export default function Logo({ className = "", onClick }: LogoProps) {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* Magnifying glass circle */}
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
      
      {/* Magnifying glass handle */}
      <line x1="18" y1="18" x2="24" y2="24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      
      {/* Detective hat (simplified) */}
      <path d="M8 10 L12 6 L16 10" stroke="currentColor" strokeWidth="1.5" fill="none" />
      <line x1="6" y1="10" x2="18" y2="10" stroke="currentColor" strokeWidth="1.5" />
      
      {/* Checkmark inside magnifying glass */}
      <path d="M9 12 L11 14 L15 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}
