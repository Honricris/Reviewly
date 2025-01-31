import apiClient from './apiClient';


export const getProducts = async (page: number, limit: number, category?: string, name?: string, price_min?: number, price_max?: number) => {
  try {
    const response = await apiClient.get('/products', {
      params: {
        limit,
        page,
        ...(category && { category }),
        ...(name && { name }),
        ...(price_min !== undefined && { price_min }),
        ...(price_max !== undefined && { price_max }),
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
