import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { message } from 'antd';
import { authAPI } from '../services/api';
import type { User, LoginForm, RegisterForm, AuthToken } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: LoginForm) => Promise<boolean>;
  register: (data: RegisterForm) => Promise<boolean>;
  logout: () => void;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初始化时检查用户状态
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('accessToken');
      const savedUser = localStorage.getItem('user');
      
      if (token && savedUser) {
        try {
          // 验证token是否有效
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        } catch (error) {
          // token无效，清除存储
          localStorage.removeItem('accessToken');
          localStorage.removeItem('user');
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (data: LoginForm): Promise<boolean> => {
    try {
      setLoading(true);
      const tokenData: AuthToken = await authAPI.login(data);
      
      // 保存token
      localStorage.setItem('accessToken', tokenData.access_token);
      
      // 获取用户信息
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
      
      message.success('登录成功');
      return true;
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterForm): Promise<boolean> => {
    try {
      setLoading(true);
      await authAPI.register(data);
      message.success('注册成功，请登录');
      return true;
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    setUser(null);
    message.success('已退出登录');
  };

  const updateUser = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      updateUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
