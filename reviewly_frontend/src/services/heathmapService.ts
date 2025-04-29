import apiClient from './apiClient';

interface HeatmapPoint {
  lat: number;
  lng: number;
  weight: number;
}

export const getHeatmapData = async (
  startDate: string | null = null,
  endDate: string | null = null
): Promise<HeatmapPoint[]> => {
  try {
    const response = await apiClient.get<HeatmapPoint[]>('/heatmap/heatmap_data', {
      params: {
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate }),
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching heatmap data:', error);
    throw error;
  }
};