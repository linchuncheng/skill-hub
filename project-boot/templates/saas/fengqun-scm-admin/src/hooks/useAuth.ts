import { useAuthStore } from '@/stores/authStore';
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const navigate = useNavigate();
  const { user, permissions, menus, hasPermission, logout: storeLogout } =
    useAuthStore();

  const logout = useCallback(() => {
    storeLogout();
    navigate('/login');
  }, [navigate, storeLogout]);

  return {
    user,
    permissions,
    menus,
    hasPermission,
    logout,
    isAuthenticated: !!user,
  };
};
