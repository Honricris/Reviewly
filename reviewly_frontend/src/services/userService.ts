export interface UserQuery {
    id: number;
    query_text: string;
    created_at: string;
  }
  
export interface UserCount {
  total_users: number;
}

  const userService = {
    async saveQuery(queryText: string): Promise<void> {
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
          body: JSON.stringify({ query_text: queryText }),
        });
  
        if (!response.ok) {
          throw new Error(`Error saving query: ${response.status} ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error saving user query:', error);
      }
    },
  
    async getRecentQueries(): Promise<UserQuery[]> {
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL;
        const apiUrl = `${baseUrl}/user/queries`;
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
  };
  
  export default userService;