import { useState, useEffect } from 'react';

export default function CookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) setShow(true);
  }, []);

  const accept = () => {
    localStorage.setItem('cookieConsent', 'true');
    setShow(false);
  };

  if (!show) return null;

  return (
    <div style={{position: 'fixed', bottom: 0, width: '100%', background: '#333', color: '#fff', padding: '1rem', textAlign: 'center'}}>
      <p>We use cookies to improve your experience. <button onClick={accept} style={{marginLeft: '1rem', padding: '0.5rem 1rem'}}>Accept</button></p>
    </div>
  );
}
