import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, signupApi } from '../api/client';

export const AuthContext = createContext({
  token: null,
  login: async () => {},
  signup: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await loginApi(email, password);
      setToken(data.access_token);
      return { success: true };
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || "Login failed" };
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password, fullName) => {
    setLoading(true);
    try {
      const data = await signupApi(email, password, fullName);
      setToken(data.access_token);
      return { success: true };
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || "Signup failed" };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
  };

  const value = {
    token,
    isAuthenticated: !!token,
    loading,
    login,
    signup,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
