import { useState, useEffect } from 'react';

export default function InteractiveBackground() {
  const [mousePosition, setMousePosition] = useState({ x: 50, y: 50 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Convert mouse position to percentage of viewport
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      setMousePosition({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1,
        pointerEvents: 'none',
        background: `
          radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, 
            rgba(92, 225, 255, 0.15) 0%, 
            transparent 50%),
          radial-gradient(circle at ${100 - mousePosition.x}% ${100 - mousePosition.y}%, 
            rgba(255, 92, 225, 0.10) 0%, 
            transparent 50%),
          radial-gradient(circle at ${mousePosition.x}% ${100 - mousePosition.y}%, 
            rgba(124, 139, 255, 0.12) 0%, 
            transparent 50%),
          #000000
        `,
        transition: 'background 0.3s ease-out',
      }}
    />
  );
}
