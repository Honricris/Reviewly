interface ChatResponse {
  answer: string;
  reviews: number[];
  products: {
    product_id: number;
    title: string;
    main_category: string;
    average_rating: number;
    rating_number: number;
    price: number;
    images: string[];
    store: string;
  }[];
}

const chatService = {
  async queryChat(
    prompt: string,
    productId?: string,
    endpoint: string = '/chat/query'
  ): Promise<ReadableStreamDefaultReader> {
    try {
      const requestData = productId ? { prompt, product_id: productId } : { prompt };

      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const apiUrl = `${baseUrl}${endpoint}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Error en la respuesta: ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error("No se recibió un cuerpo de respuesta.");
      }

      return response.body.getReader();  
    } catch (error) {
      console.error('Error al comunicarse con el chat:', error);
      throw new Error('No se pudo obtener una respuesta del chat.');
    }
  },
};

export default chatService;
