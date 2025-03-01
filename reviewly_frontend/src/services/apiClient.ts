import axios from 'axios';

const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL}`,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  console.log('Realizando solicitud:', config.method?.toUpperCase(), config.url);
  console.log('Datos de la solicitud:', config.data);
  return config;
}, (error) => {
  console.error('Error en la solicitud:', error);
  return Promise.reject(error);
});

apiClient.interceptors.response.use((response) => {
  console.log('Respuesta recibida:', response.status, response.data);
  return response;
}, (error) => {
  console.error('Error en la respuesta:', error.response?.status, error.message);
  return Promise.reject(error);
});

export default apiClient;
