import axios from 'axios';
import { useSettingsStore } from '../utils/settingsStore';

const getBaseUrl = () => useSettingsStore.getState().apiUrl;

const api = axios.create({
  timeout: 300000,
});

api.interceptors.request.use((config) => {
  config.baseURL = getBaseUrl();
  return config;
});

export const runResearch = async (payload: { query: string; molecule?: string }) => {
  const response = await api.post('/run', payload);
  return response.data;
};

export const getArchives = async () => {
  const response = await api.get('/archives');
  return response.data;
};

export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export default api;
