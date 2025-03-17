import apiClient from './apiClient';

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
}

export const AuthService = {
  login: async (data: LoginData) => {
    try {
      const response = await apiClient.post('/auth/login', data);
      return response.data;
    } catch (error) {
      throw new Error('Error al iniciar sesión');
    }
  },

  register: async (data: RegisterData) => {
    try {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    } catch (error) {
      throw new Error('Error al registrar el usuario');
    }
  },
};