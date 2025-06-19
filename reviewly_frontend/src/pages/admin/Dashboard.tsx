import '../../styles/AdminDashboard.css';
import ChatBubble from '../../components/ChatBubble';
import { generateReportPDF } from '../../components/admin/ReportGenerator';
import React, { useState, useEffect, useRef } from 'react';
import userService from '../../services/userService';
import { getProductCount, getMostFavoritedProducts, getProductById } from '../../services/productService';
import { getHeatmapData } from '../../services/heathmapService';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet.heat';
import 'leaflet/dist/leaflet.css';
import 'leaflet-fullscreen/dist/leaflet.fullscreen.css';
import 'leaflet-fullscreen';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Pie, Bar } from 'react-chartjs-2';
import Header from '../../components/Header';
import ProductCard from '../../components/ProductCard';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface HeatmapPoint {
  lat: number;
  lng: number;
  weight: number;
}

interface Product {
  product_id: number;
  title: string;
  images: string[];
  store: string;
  price: number;
  average_rating: number;
  main_category: string;
}

const AdminDashboard = () => {
  const [showChat, setShowChat] = useState(false);
  const [userCount, setUserCount] = useState<number | null>(null);
  const [productCount, setProductCount] = useState<number | null>(null);
  const [productsSavedToday, setProductsSavedToday] = useState<number | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [executionTimes, setExecutionTimes] = useState<any[]>([]);
  const [mapError, setMapError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('week');
  const [sliderValue, setSliderValue] = useState(7);
  const [mostFavoritedProducts, setMostFavoritedProducts] = useState<Product[]>([]);
  const [currentProductPage, setCurrentProductPage] = useState(0);
  const [startDate, setStartDate] = useState<Date | null>(new Date(Date.now() - 5 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);
  const [chartData, setChartData] = useState<{ id: string; chartType: string; data: any; options: any }[]>([]);  
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<L.HeatLayer | null>(null);
  const navigate = useNavigate();
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const PRODUCTS_PER_PAGE = 3;

  const getDateRange = (days: number) => {
    const now = new Date();
    const startDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    return {
      start: startDate.toISOString().split('T')[0],
      end: now.toISOString().split('T')[0]
    };
  };

  const getTodayDateRange = () => {
    const today = new Date();
    return {
      start: today.toISOString().split('T')[0],
      end: today.toISOString().split('T')[0]
    };
  };

  const fetchMostFavoritedProducts = async (start: string, end: string) => {
    try {
      const favoritedData = await getMostFavoritedProducts(start, end, 30);
      const productPromises = favoritedData.map((item: { product_id: number }) =>
        getProductById(item.product_id.toString())
      );
      const products = await Promise.all(productPromises);
      setMostFavoritedProducts(products);
    } catch (error) {
      console.error('Error fetching most favorited products:', error);
      setMostFavoritedProducts([]);
    }
  };

  const fetchProductsSavedToday = async () => {
    try {
      const { start, end } = getTodayDateRange();
      const favoritedData = await getMostFavoritedProducts(start, end, 1000);
      setProductsSavedToday(favoritedData.length);
    } catch (error) {
      console.error('Error fetching products saved today:', error);
      setProductsSavedToday(0);
    }
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [userCount, productCount, executionData, favoriteIdsData] = await Promise.all([
          userService.getUserCount(),
          getProductCount(),
          userService.getExecutionTimes(
            getDateRange(7).start,
            getDateRange(7).end
          ),
          userService.getFavorites()
        ]);

        setUserCount(userCount);
        setProductCount(productCount);
        setExecutionTimes(executionData);
        setFavoriteIds(favoriteIdsData);

        const heatData = await getHeatmapData();
        setHeatmapData(heatData);

        const { start, end } = getDateRange(5);
        await fetchMostFavoritedProducts(start, end);
        await fetchProductsSavedToday();
      } catch (error) {
        console.error('Failed to fetch initial data:', error);
        setUserCount(0);
        setProductCount(0);
        setProductsSavedToday(0);
        setExecutionTimes([]);
        setHeatmapData([]);
        setMostFavoritedProducts([]);
        setFavoriteIds([]);
      }
    };

    fetchInitialData();
  }, []);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    setSliderValue(value);
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
    debounceTimeout.current = setTimeout(async () => {
      const { start, end } = getDateRange(value);
      try {
        const [newHeatData, newExecutionData] = await Promise.all([
          getHeatmapData(start, end),
          userService.getExecutionTimes(start, end)
        ]);
        setHeatmapData(newHeatData);
        setExecutionTimes(newExecutionData);
      } catch (error) {
        console.error('Error updating data:', error);
      }
    }, 500);
  };

  const handleDateRangeChange = async () => {
    if (startDate && endDate) {
      const start = startDate.toISOString().split('T')[0];
      const end = endDate.toISOString().split('T')[0];
      await fetchMostFavoritedProducts(start, end);
      setCurrentProductPage(0);
    }
  };

  useEffect(() => {
    if (!mapRef.current) {
      const map = L.map('map', {
        fullscreenControl: true,
        fullscreenControlOptions: {
          position: 'topleft',
          title: {
            'false': 'View in fullscreen',
            'true': 'Exit fullscreen'
          }
        }
      }).setView([20, 0], 2);
      mapRef.current = map;
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        noWrap: true
      }).addTo(map);
    }

    if (mapRef.current && heatmapData.length > 0) {
      if (heatLayerRef.current) {
        mapRef.current.removeLayer(heatLayerRef.current);
      }
      const heatPoints = heatmapData.map(point => [point.lat, point.lng, point.weight]);
      heatLayerRef.current = (L as any).heatLayer(heatPoints, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        minOpacity: 0.5
      }).addTo(mapRef.current);
      const bounds = L.latLngBounds(heatmapData.map(point => [point.lat, point.lng]));
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        heatLayerRef.current = null;
      }
    };
  }, [heatmapData]);

  const toggleChat = () => setShowChat((prev) => !prev);
  const handleLogout = () => navigate('/login');

  const handleReportGenerate = async (reportType: string, parameters: any) => {
    try {
      await generateReportPDF(reportType, parameters);
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };

  const handleChartData = (chartConfig: any) => {
    const newChart = {
      id: Date.now().toString(),
      chartType: chartConfig.type || 'pie', 
      data: chartConfig.data,
      options: chartConfig.options,
    };
    setChartData((prev) => [...prev, newChart]);
  };

  const renderChart = (chart: { chartType: string; data: any; options: any }) => {
    switch (chart.chartType) {
      case 'bar':
        return <Bar data={chart.data} options={chart.options} />;
      case 'line':
        return <Line data={chart.data} options={chart.options} />;
      case 'pie':
        return <Pie data={chart.data} options={chart.options} />;
      case 'doughnut':
        return <Pie data={chart.data} options={chart.options} />; 
      default:
        return <Pie data={chart.data} options={chart.options} />; 
    }
  };

  const removeChart = (id: string) => {
    setChartData((prev) => prev.filter((chart) => chart.id !== id));
  };

  const stats = [
    { title: 'Total Users', value: userCount ?? 'Loading...', change: userCount !== null ? '+12%' : '', trend: 'up' },
    { title: 'Products', value: productCount ?? 'Loading...', change: productCount !== null ? '+5%' : '', trend: 'up' },
    { 
      title: 'Products saved today', 
      value: productsSavedToday ?? 'Loading...', 
      change: productsSavedToday !== null ? '-2%' : '', 
      trend: 'down' 
    },
    { title: 'Income', value: '$12,345', change: '+18%', trend: 'up' }
  ];

  const calculatePercentiles = (data: number[], percentiles: number[]) => {
    if (data.length === 0) return percentiles.map(() => 0);
    const sorted = [...data].sort((a, b) => a - b);
    return percentiles.map(p => {
      const index = Math.ceil((p / 100) * sorted.length) - 1;
      return sorted[index] || 0;
    });
  };

  const processedChartData = () => {
    const dates = executionTimes.map(query => new Date(query.created_at).toLocaleDateString());
    const times = executionTimes.map(query => query.execution_time || 0);

    const percentiles = calculatePercentiles(times, [10, 50, 90]);

    return {
      labels: dates,
      datasets: [
        {
          label: 'All Queries',
          data: times,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        },
        {
          label: '10th Percentile (Fastest)',
          data: Array(dates.length).fill(percentiles[0]),
          fill: false,
          borderColor: 'rgb(0, 128, 0)',
          borderDash: [5, 5],
          tension: 0,
          pointRadius: 0,
        },
        {
          label: '50th Percentile (Median)',
          data: Array(dates.length).fill(percentiles[1]),
          fill: false,
          borderColor: 'rgb(255, 165, 0)',
          borderDash: [5, 5],
          tension: 0,
          pointRadius: 0,
        },
        {
          label: '90th Percentile (Slowest)',
          data: Array(dates.length).fill(percentiles[2]),
          fill: false,
          borderColor: 'rgb(255, 0, 0)',
          borderDash: [5, 5],
          tension: 0,
          pointRadius: 0,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, 
    resizeDelay: 100, 
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: { size: 14 }, 
          color: '#333',
        },
      },
      title: {
        display: true,
        text: 'Query Execution Times with Percentiles',
        font: { size: 18 }, 
        color: '#333',
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${value.toFixed(3)}s`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Execution Time (s)',
          font: { size: 14 }, 
        },
      },
      x: {
        title: {
          display: true,
          text: 'Date',
          font: { size: 14 },
        },
      },
    },
  };

  const categoryChartData = () => {
    const categoryCounts: { [key: string]: number } = {};
    mostFavoritedProducts.forEach((product) => {
      const category = product.main_category || 'Unknown';
      categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });

    const labels = Object.keys(categoryCounts);
    const data = Object.values(categoryCounts);
    const colors = [
      '#FF6B6B',
      '#4ECDC4',
      '#45B7D1',
      '#96CEB4',
      '#FFEEAD',
      '#D4A5A5',
      '#9B59B6',
    ];

    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: '#ffffff',
          borderWidth: 2,
        },
      ],
    };
  };

  const categoryChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    resizeDelay: 100,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: { size: 14 },
          color: '#333',
        },
      },
      title: {
        display: true,
        text: 'Category Distribution',
        font: { size: 18 },
        color: '#333',
      },
    },
  };

  const handlePrevProducts = () => {
    setCurrentProductPage(prev => Math.max(prev - 1, 0));
  };

  const handleNextProducts = () => {
    const maxPage = Math.ceil(mostFavoritedProducts.length / PRODUCTS_PER_PAGE) - 1;
    setCurrentProductPage(prev => Math.min(prev + 1, maxPage));
  };

  const displayedProducts = mostFavoritedProducts.slice(
    currentProductPage * PRODUCTS_PER_PAGE,
    (currentProductPage + 1) * PRODUCTS_PER_PAGE
  );

  return (
    <div className="admin-dashboard">
      <Header
        buttonConfig={{ showHome: true, showFavourites: false, showLogout: true, isAdmin: true }}
        showSearchBar={false}
      />
      <div className="dashboard-container">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <h3>{stat.title}</h3>
              <div className="stat-value">{stat.value}</div>
              <div className={`stat-change ${stat.trend}`}>
                {stat.change} {stat.trend === 'up' ? '↑' : '↓'}
              </div>
            </div>
          ))}
        </div>

        <div className="dashboard-content">
          <div className="row">
            <section className="map-section">
              <h2>Access Heatmap</h2>
              <div className="time-controls">
                <div>
                  <button
                    onClick={() => { setTimeRange('week'); setSliderValue(7); }}
                    className={timeRange === 'week' ? 'active' : ''}
                  >
                    Week
                  </button>
                  <button
                    onClick={() => { setTimeRange('month'); setSliderValue(30); }}
                    className={timeRange === 'month' ? 'active' : ''}
                  >
                    Month
                  </button>
                </div>
                <input
                  type="range"
                  min="1"
                  max={timeRange === 'week' ? "7" : "30"}
                  value={sliderValue}
                  onChange={handleSliderChange}
                />
                <div>Last {sliderValue} days</div>
              </div>
              {mapError && <div className="map-error">{mapError}</div>}
              <div id="map"></div>
            </section>
            <section className="chart-section">
              <h2>Query Performance</h2>
              <div className="chart-container" style={{ position: 'relative', height: '450px', width: '600px' }}>
                <Line data={processedChartData()} options={chartOptions} />
              </div>
            </section>
          </div>

          <div className="row">
            <section className="most-favorited-section">
              <h2>Most Favorited Products</h2>
              <div className="date-range-selector">
                <label>Start Date:</label>
                <DatePicker
                  selected={startDate}
                  onChange={(date: Date) => setStartDate(date)}
                  dateFormat="yyyy-MM-dd"
                  maxDate={endDate || new Date()}
                  className="date-picker"
                />
                <label>End Date:</label>
                <DatePicker
                  selected={endDate}
                  onChange={(date: Date) => setEndDate(date)}
                  dateFormat="yyyy-MM-dd"
                  minDate={startDate}
                  maxDate={new Date()}
                  className="date-picker"
                />
                <button
                  onClick={handleDateRangeChange}
                  disabled={!startDate || !endDate}
                >
                  Update
                </button>
              </div>
              <div className="product-carousel">
                <button
                  onClick={handlePrevProducts}
                  disabled={currentProductPage === 0}
                  className="carousel-button prev"
                >
                  <ArrowBackIcon />
                </button>
                <div className="product-grid">
                  {displayedProducts.length > 0 ? (
                    displayedProducts.map((product) => (
                      <ProductCard
                        key={product.product_id}
                        id={product.product_id}
                        name={product.title}
                        imageUrl={product.images[0] || 'https://via.placeholder.com/150'}
                        store={product.store}
                        price={product.price}
                        averageRating={product.average_rating}
                        favoriteIds={favoriteIds}
                      />
                    ))
                  ) : (
                    <p>No products found for the selected date range.</p>
                  )}
                </div>
                <button
                  onClick={handleNextProducts}
                  disabled={currentProductPage >= Math.ceil(mostFavoritedProducts.length / PRODUCTS_PER_PAGE) - 1}
                  className="carousel-button next"
                >
                  <ArrowForwardIcon />
                </button>
              </div>
            </section>
            <section className="category-chart-section">
              <h2>Category Distribution</h2>
              <div className="chart-container" style={{ position: 'relative', height: '450px', width: '450px' }}>
                {mostFavoritedProducts.length > 0 ? (
                  <Pie data={categoryChartData()} options={categoryChartOptions} />
                ) : (
                  <p>No data available for category distribution.</p>
                )}
              </div>
            </section>
          </div>

          {chartData.length > 0 && (
            <div className="row">
              {chartData.map((chart) => (
                <section key={chart.id} className="dynamic-chart-section">
                  <div className="chart-header">
                    <h2>{chart.options.plugins.title.text}</h2>
                    <button
                      className="close-chart-button"
                      onClick={() => removeChart(chart.id)}
                      aria-label="Close chart"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="chart-container" style={{ position: 'relative', height: '450px', width: '450px' }}>
                    {renderChart(chart)}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>

        <ChatBubble 
          onClick={toggleChat} 
          isOpen={showChat} 
          onReportGenerate={handleReportGenerate} 
          onChartData={handleChartData} 
        />
      </div>
    </div>
  );
};

export default AdminDashboard;