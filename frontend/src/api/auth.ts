import apiClient from './client';
import type { UserCredentials, RegisterData, TokenResponse } from '../types';

export const login = async (credentials: UserCredentials): Promise<TokenResponse> => {
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);
  
  const response = await apiClient.post<TokenResponse>('/auth/login', formData);
  return response.data;
};

export const register = async (data: RegisterData): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/register', data);
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};
