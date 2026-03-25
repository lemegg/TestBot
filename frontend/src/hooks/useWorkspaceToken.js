import { useAuth } from '@clerk/clerk-react';
import { useCallback } from 'react';

/**
 * Custom hook to get a Clerk token.
 */
export const useWorkspaceToken = () => {
  const { getToken } = useAuth();

  const getWorkspaceToken = useCallback(async () => {
    return await getToken();
  }, [getToken]);

  return { getWorkspaceToken };
};
