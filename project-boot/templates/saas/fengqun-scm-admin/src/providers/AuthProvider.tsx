import { useAuthStore } from '@/stores/authStore';
import { FC, ReactNode, createContext, useContext, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  isAuthenticated: false,
  isLoading: true,
});

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { accessToken, user } = useAuthStore();

  const isAuthenticated = !!accessToken && !!user;

  useEffect(() => {
    // 白名单路由
    const whiteList = ['/login'];
    if (whiteList.includes(location.pathname)) {
      return;
    }

    // 未登录重定向到登录页
    if (!isAuthenticated) {
      navigate('/login', { replace: true, state: { from: location } });
    }
  }, [isAuthenticated, navigate, location]);

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading: false }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
