import React from 'react';
import ReactDOM from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App';
import './styles.css';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  console.error("Environment variables loaded:", import.meta.env);
  throw new Error("Missing Publishable Key. Ensure VITE_CLERK_PUBLISHABLE_KEY is set in frontend/.env");
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ClerkProvider 
      publishableKey={PUBLISHABLE_KEY}
      afterSignInUrl="/chat"
      afterSignUpUrl="/chat"
      signInForceRedirectUrl="/chat"
      signUpForceRedirectUrl="/chat"
    >
      <App />
    </ClerkProvider>
  </React.StrictMode>
);
