import apiClient from './apiClient';

interface ChatResponse {
  answer: string;    
  reviews: number[]; 
}

const chatService = {
  async queryChat(prompt: string, endpoint: string = '/chat/query'): Promise<ChatResponse> {
    try {
      const requestData = { prompt };
      const response = await apiClient.post<ChatResponse>(endpoint, requestData);
      return response.data; // Retorna el objeto con text y reviews
    } catch (error) {
      console.error('Error al comunicarse con el chat:', error);
      throw new Error('No se pudo obtener una respuesta del chat.');
    }
  },
};

export default chatService;
