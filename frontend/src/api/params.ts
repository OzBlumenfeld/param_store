import apiClient from './client';
import type { Parameter, ParameterRequest, ParameterResponse } from '../types';

export const listParameters = async (app?: string, name?: string): Promise<Parameter[]> => {
  const params = new URLSearchParams();
  if (app) params.append('app', app);
  if (name) params.append('name', name);
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const response = await apiClient.get<Parameter[]>(`/params/${queryString}`);
  return response.data;
};

export const getParameter = async (name: string, app: string = 'default'): Promise<{ name: string; value: string }> => {
  const response = await apiClient.get<{ name: string; value: string }>(`/params/${name}?app=${app}`);
  return response.data;
};

export const setParameter = async (data: ParameterRequest): Promise<ParameterResponse> => {
  const response = await apiClient.post<ParameterResponse>('/params/', data);
  return response.data;
};

export const deleteParameter = async (name: string, app: string = 'default'): Promise<{ name: string; message: string }> => {
  const response = await apiClient.delete<{ name: string; message: string }>(`/params/${name}?app=${app}`);
  return response.data;
};

export const updateParameter = async (name: string, value: string, app: string = 'default'): Promise<ParameterResponse> => {
  const response = await apiClient.put<ParameterResponse>(`/params/${name}?app=${app}`, { value });
  return response.data;
};
