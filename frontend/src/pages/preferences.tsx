import { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';

export default function Preferences() {
  const { theme, toggleTheme } = useTheme();
  const [language, setLanguage] = useState('en');

  return (
    <div style={{padding: '2rem'}}>
      <h1>User Preferences</h1>
      <div style={{marginTop: '2rem'}}>
        <h2>Theme</h2>
        <button onClick={toggleTheme}>
          Current: {theme} - Click to toggle
        </button>
      </div>
      <div style={{marginTop: '2rem'}}>
        <h2>Language</h2>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>
      </div>
    </div>
  );
}
