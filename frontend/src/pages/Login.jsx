import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (isRegister) {
      try {
        // Dynamic detection of API base to avoid localhost vs 127.0.0.1 mismatch
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const api_base = isLocal ? `http://${window.location.hostname}:8001` : '';
        
        const res = await fetch(`${api_base}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Registration failed');
        }
        setSuccess('Account created! You can now login.');
        setIsRegister(false);
      } catch (err) {
        setError(err.message);
      }
    } else {
      try {
        await login(email, password);
        navigate('/dashboard');
      } catch (err) {
        setError('Invalid email or password');
      }
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>{isRegister ? 'Create Account' : 'SOP Assistant Login'}</h2>
        
        {error && <p className="error">{error}</p>}
        {success && <p className="success" style={{ color: 'green', background: '#e6f4ea', padding: '10px', borderRadius: '4px' }}>{success}</p>}
        
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        <button type="submit">
          {isRegister ? 'Register' : 'Login'}
        </button>

        <p style={{ textAlign: 'center', fontSize: '14px', marginTop: '10px' }}>
          {isRegister ? 'Already have an account?' : 'Need an account?'} 
          <button 
            type="button" 
            className="nav-btn" 
            style={{ marginLeft: '10px', border: 'none', textDecoration: 'underline' }}
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? 'Login' : 'Register'}
          </button>
        </p>
      </form>
    </div>
  );
};

export default Login;
