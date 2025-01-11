import apiClient from './apiClient';


export const getProducts = async (page : number) => {
  try {
    const response = await apiClient.get('/products', {
      params: {
        limit: 63,
        page,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};


export const getProductById = async (productId: string) => {
  try {
    const response = await apiClient.get(`/products/${productId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching product details:', error);
    throw error;
  }
};


export const getProductReviews = async (productId: string, page: number = 1) => {
  try {
    const response = await apiClient.get(`/products/${productId}/reviews?page=${page}`);
    return response.data; 
  } catch (error) {
    console.error('Error fetching product reviews:', error);
    throw error;
  }
};
