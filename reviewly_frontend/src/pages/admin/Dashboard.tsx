import '../../styles/AdminDashboard.css';
import ChatBubble from '../../components/ChatBubble';
import UserManagement from '../../components/admin/UserManagement';
import ReportGenerator from '../../components/admin/ReportGenerator';
import { generateReportPDF } from '../../components/admin/ReportGenerator';
import React, { useState, useEffect, useRef } from 'react';
import userService from '../../services/userService';
import { getProductCount, getProducts } from '../../services/productService';
import { getHeatmapData } from '../../services/heathmapService';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet.heat';
import 'leaflet/dist/leaflet.css';
import 'leaflet-fullscreen/dist/leaflet.fullscreen.css';
import 'leaflet-fullscreen';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface HeatmapPoint {
  lat: number;
  lng: number;
  weight: number;
}

const AdminDashboard = () => {
  const [showChat, setShowChat] = useState(false);
  const [userCount, setUserCount] = useState<number | null>(null);
  const [productCount, setProductCount] = useState<number | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [executionTimes, setExecutionTimes] = useState<any[]>([]);
  const [mapError, setMapError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('week');
  const [sliderValue, setSliderValue] = useState(7);
  const [showUserManagement, setShowUserManagement] = useState(false);
  const [showReportGenerator, setShowReportGenerator] = useState(false);
  const mapRef = useRef<L.Map | null>(null);
  const heatLayerRef = useRef<L.HeatLayer | null>(null);
  const navigate = useNavigate();
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  const getDateRange = (days: number) => {
    const now = new Date();
    const startDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    return {
      start: startDate.toISOString(),
      end: now.toISOString()
    };
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [userCount, productCount, executionData] = await Promise.all([
          userService.getUserCount(),
          getProductCount(),
          userService.getExecutionTimes(
            getDateRange(7).start,
            getDateRange(7).end
          )
        ]);
  
        setUserCount(userCount);
        setProductCount(productCount);
        setExecutionTimes(executionData);
  
        const heatData = await getHeatmapData();
        setHeatmapData(heatData);
      } catch (error) {
        console.error('Failed to fetch initial data:', error);
        setUserCount(0);
        setProductCount(0);
        setExecutionTimes([]);
        setHeatmapData([]);
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
          getHeatmapData(start.split('T')[0], end.split('T')[0]),
          userService.getExecutionTimes(start, end)
        ]);
        setHeatmapData(newHeatData);
        setExecutionTimes(newExecutionData);
      } catch (error) {
        console.error('Error updating data:', error);
      }
    }, 500);
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
  const toggleUserManagement = () => setShowUserManagement(prev => !prev);
  const toggleReportGenerator = () => setShowReportGenerator(prev => !prev);

  const handleReportGenerate = async (reportType: string, parameters: any) => {
    try {
      await generateReportPDF(reportType, parameters);
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };

  const stats = [
    { title: 'Total Users', value: userCount ?? 'Loading...', change: userCount !== null ? '+12%' : '', trend: 'up' },
    { title: 'Products', value: productCount ?? 'Loading...', change: productCount !== null ? '+5%' : '', trend: 'up' },
    { title: "Products saved today", value: "87", change: "-2%", trend: "down" },
    { title: "Income", value: "$12,345", change: "+18%", trend: "up" }
  ];

  const chartData = {
    labels: executionTimes.map(query => new Date(query.created_at).toLocaleDateString()),
    datasets: [{
      label: 'Query Execution Time (seconds)',
      data: executionTimes.map(query => query.execution_time || 0),
      fill: false,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Query Execution Times'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Execution Time (s)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>Admin Panel</h1>
        <div className="user-profile">
          <span>Admin</span>
          <div className="avatar">A</div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </header>

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
        <section className="map-section">
          <h2>Access Heatmap</h2>
          <div className="time-controls" style={{ marginBottom: '15px' }}>
            <div style={{ marginBottom: '10px' }}>
              <button
                onClick={() => { setTimeRange('week'); setSliderValue(7); }}
                className={timeRange === 'week' ? 'active' : ''}
                style={{ marginRight: '10px' }}
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
              style={{ width: '100%' }}
            />
            <div>
              Last {sliderValue} days
            </div>
          </div>
          {mapError && <div className="map-error">{mapError}</div>}
          <div id="map" style={{ height: '400px', width: '100%' }}></div>
        </section>

        <section className="chart-section">
          <h2>Query Performance</h2>
          <div style={{ height: '400px', width: '100%' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </section>

        <section className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button className="action-btn"><span>+</span> Add Product</button>
            <button className="action-btn" onClick={toggleUserManagement}>
              <span>👥</span> Manage Users
            </button>
            <button className="action-btn" onClick={toggleReportGenerator}>
              <span>📊</span> Generate Report
            </button>
            <button className="action-btn"><span>⚙️</span> Settings</button>
          </div>
        </section>
      </div>

      {showUserManagement && <UserManagement onClose={toggleUserManagement} />}
      {showReportGenerator && <ReportGenerator onClose={toggleReportGenerator} />}
      <ChatBubble 
        onClick={toggleChat} 
        isOpen={showChat} 
        onReportGenerate={handleReportGenerate} 
      />
    </div>
  );
};

export default AdminDashboard;