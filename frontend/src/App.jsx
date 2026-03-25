import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, SignIn, SignUp, useUser } from '@clerk/clerk-react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Analytics from './pages/Analytics';
import RequireAdmin from './components/RequireAdmin';
import MetadataForm from './components/MetadataForm';

const AppLayout = ({ children }) => {
  const { user, isLoaded } = useUser();
  const [showMetadataForm, setShowMetadataForm] = useState(false);

  useEffect(() => {
    if (isLoaded && user) {
      const metadata = user.unsafeMetadata;
      if (!metadata || !metadata.name || !metadata.company_name || !metadata.phone_number) {
        setShowMetadataForm(true);
      }
    }
  }, [isLoaded, user]);

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        {showMetadataForm && <MetadataForm onComplete={() => setShowMetadataForm(false)} />}
        {children}
      </div>
    </div>
  );
};

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/login/*" element={
        <div style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          width: "100vw",
          backgroundColor: "#0f172a"
        }}>
          <SignIn 
            routing="path" 
            path="/login" 
            signUpUrl="/register"
            forceRedirectUrl="/chat"
            fallbackRedirectUrl="/chat"
            appearance={{
              elements: {
                card: "shadow-xl rounded-2xl",
              }
            }}
          />
        </div>
      } />
      <Route path="/register/*" element={
        <div style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          width: "100vw",
          backgroundColor: "#0f172a"
        }}>
          <SignUp 
            routing="path" 
            path="/register" 
            signInUrl="/login"
            forceRedirectUrl="/chat"
            fallbackRedirectUrl="/chat"
            appearance={{
              elements: {
                card: "shadow-xl rounded-2xl",
              }
            }}
          />
        </div>
      } />
      
      <Route path="/dashboard" element={
        <>
          <SignedIn>
            <RequireAdmin>
              <AppLayout><Dashboard /></AppLayout>
            </RequireAdmin>
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />
      
      <Route path="/chat" element={
        <>
          <SignedIn>
            <AppLayout><Chat /></AppLayout>
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />
      
      <Route path="/documents" element={
        <>
          <SignedIn>
            <AppLayout>
              <RequireAdmin>
                <Documents />
              </RequireAdmin>
            </AppLayout>
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />
      
      <Route path="/analytics" element={
        <>
          <SignedIn>
            <AppLayout>
              <RequireAdmin>
                <Analytics />
              </RequireAdmin>
            </AppLayout>
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />

      <Route path="/" element={
        <>
          <SignedIn>
            <Navigate to="/chat" replace />
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />
      
      <Route path="*" element={
        <>
          <SignedIn>
            <Navigate to="/chat" replace />
          </SignedIn>
          <SignedOut>
            <Navigate to="/login" replace />
          </SignedOut>
        </>
      } />
    </Routes>
  </BrowserRouter>
);

export default App;
