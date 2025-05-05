import apiClient from './apiClient';


export const getProducts = async (
  page: number,
  limit?: number,
  category?: string,
  name?: string,
  price_min?: number,
  price_max?: number,
  store?: string,
  min_rating?: number,
  min_favorites?: number,
  include_favorites?: boolean
) => {
  try {
    const response = await apiClient.get('/products/', {
      params: {
        page,
        limit,
        category,
        name,
        price_min,
        price_max,
        store,
        min_rating,
        min_favorites,
        include_favorites
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

export const searchProducts = async (query: string, top_n?: number, category?: string, min_price?: number, max_price?: number) => {
  try {
    const response = await apiClient.post('/products/search', {
      query,
      ...(top_n && { top_n }),
      ...(category && { category }),
      ...(min_price && { min_price }),
      ...(max_price && { max_price }),
    });
    return response.data;
  } catch (error) {
    console.error('Error searching products:', error);
    throw error;
  }
};

export const autocompleteProducts = async (searchTerm: string, limit: number = 3) => {
  try {
    const response = await apiClient.get('/products/autocomplete', {
      params: {
        term: searchTerm,
        limit
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error in autocomplete:', error);
    throw error;
  }
};

export const getCategories = async () => {
  try {
    const response = await apiClient.get('/products/categories');
    return response.data.categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

export const getProductCount = async (): Promise<number> => {
  try {
    const response = await apiClient.get('/products/count');
    return response.data.total_products;
  } catch (error) {
    console.error('Error fetching product count:', error);
    return 0;
  }
};