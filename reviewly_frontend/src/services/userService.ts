export interface UserQuery {
  id: number;
  query_text: string;
  created_at: string;
  execution_time?: number;
}

export interface UserCount {
  total_users: number;
}

export interface FavoriteProduct {
  product_id: number;
  title: string;
  price: number;
  average_rating: number;
  store: string;
  image: string | null;
}

export interface User {
  id: number;
  email: string;
  role: string;
  github_id?: number;
  created_at: string;
}

export interface LoginLog {
  id: number;
  user_id: number;
  ip_address: string;
  login_at: string;
}

const userService = {
  async saveQuery(queryText: string, executionTime?: number): Promise<void> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/queries`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ 
          query_text: queryText,
          ...(executionTime !== undefined && { execution_time: executionTime })
        }),
      });

      if (!response.ok) {
        throw new Error(`Error saving query: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error saving user query:', error);
    }
  },

  async getRecentQueries(userId?: number): Promise<UserQuery[]> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = userId ? `${baseUrl}/user/${userId}/queries` : `${baseUrl}/user/queries`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching queries: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching user queries:', error);
      return [];
    }
  },

  async getExecutionTimes(startTime: string, endTime: string): Promise<UserQuery[]> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/execution-times?start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching execution times: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching execution times:', error);
      return [];
    }
  },

  async getUserCount(): Promise<number> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/count`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching user count: ${response.status} ${response.statusText}`);
      }

      const data: UserCount = await response.json();
      return data.total_users;
    } catch (error) {
      console.error('Error fetching user count:', error);
      return 0;
    }
  },

  async addFavorite(productId: number): Promise<boolean> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/favorites`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ product_id: productId }),
      });

      if (!response.ok) {
        throw new Error(`Error adding favorite: ${response.status} ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error adding favorite:', error);
      return false;
    }
  },

  async removeFavorite(productId: number): Promise<boolean> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/favorites`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ product_id: productId }),
      });

      if (!response.ok) {
        throw new Error(`Error removing favorite: ${response.status} ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error removing favorite:', error);
      return false;
    }
  },

  async getFavorites(userId?: number): Promise<number[]> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = userId ? `${baseUrl}/user/${userId}/favorites` : `${baseUrl}/user/favorites`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching favorites: ${response.status} ${response.statusText}`);
      }

      const favoriteIds: number[] = await response.json();
      return favoriteIds;
    } catch (error) {
      console.error('Error fetching favorites:', error);
      return [];
    }
  },

  async getLoginLogs(userId: number): Promise<LoginLog[]> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/${userId}/login-logs`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching login logs: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching login logs:', error);
      return [];
    }
  },

  async getAllUsers(): Promise<User[]> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error fetching users: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  },

  async updateUser(userId: number, data: Partial<User>): Promise<boolean> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/${userId}`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`Error updating user: ${response.status} ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error updating user:', error);
      return false;
    }
  },

  async getProductFavoriteCount(productId: number): Promise<number> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/products/${productId}/favorite-count`;
      const token = localStorage.getItem('token');
  
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });
  
      if (!response.ok) throw new Error(`Error fetching favorite count: ${response.status}`);
      const data = await response.json();
      return data.favoriteCount;
    } catch (error) {
      console.error('Error fetching favorite count:', error);
      return 0;
    }
  },

  async deleteUser(userId: number): Promise<boolean> {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}/user/${userId}`;
      const token = localStorage.getItem('token');

      const response = await fetch(apiUrl, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`Error deleting user: ${response.status} ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting user:', error);
      return false;
    }
  },
};

export default userService;


