import React from 'react';
import { Navigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

const ADMIN_EMAILS = ["worshipgate1@gmail.com", "shivam@theaffordableorganicstore.com"];

const RequireAdmin = ({ children }) => {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div className="loading-state">Loading permissions...</div>;
  }

  const userEmail = user?.primaryEmailAddress?.emailAddress;
  const isAdmin = userEmail && ADMIN_EMAILS.includes(userEmail);

  if (!isAdmin) {
    return <Navigate to="/chat" replace />;
  }

  return children;
};

export default RequireAdmin;
