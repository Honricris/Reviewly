import '../../styles/AdminDashboard.css';
import ChatBubble from '../../components/ChatBubble';
import React, { useState, useEffect, useRef } from 'react';
import userService from '../../services/userService';
import { getProductCount } from '../../services/productService';
import { getHeatmapData } from '../../services/heathmapService';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet.heat';
import 'leaflet/dist/leaflet.css';

interface Stat {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
}

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
  const [mapError, setMapError] = useState<string | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const [userCount, productCount, heatData] = await Promise.all([
          userService.getUserCount(),
          getProductCount(),
          getHeatmapData(),
        ]);
        setUserCount(userCount);
        setProductCount(productCount);
        setHeatmapData(heatData);
      } catch (error) {
        console.error('Failed to fetch counts:', error);
        setUserCount(0);
        setProductCount(0);
        setHeatmapData([]);
      }
    };
    fetchCounts();
  }, []);

  // Initialize map with fallback
  useEffect(() => {
    if (!mapRef.current) {
      try {
        // Initialize base map
        const map = L.map('map').setView([20, 0], 2);
        mapRef.current = map;

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          noWrap: true
        }).addTo(map);

        // Try to add heatmap if data is available
        if (heatmapData.length > 0) {
          try {
            const heatPoints = heatmapData.map(point => [point.lat, point.lng, point.weight]);
            (L as any).heatLayer(heatPoints, {
              radius: 25,
              blur: 15,
              maxZoom: 17,
              minOpacity: 0.5
            }).addTo(map);

            // Fit map to show all points
            const bounds = L.latLngBounds(heatmapData.map(point => [point.lat, point.lng]));
            map.fitBounds(bounds, { padding: [50, 50] });
          } catch (heatError) {
            console.error('Failed to create heatmap:', heatError);
            setMapError('Heatmap no disponible - mostrando mapa base');
            // Center on first point if available
            if (heatmapData.length > 0) {
              map.setView([heatmapData[0].lat, heatmapData[0].lng], 8);
            }
          }
        }

        // Handle map resize issues
        setTimeout(() => {
          map.invalidateSize();
        }, 100);

        // Add error handler
        map.on('load', () => setMapError(null));
        map.on('error', (e) => {
          console.error('Map error:', e);
          setMapError('Error al cargar el mapa');
        });
      } catch (mapInitError) {
        console.error('Failed to initialize map:', mapInitError);
        setMapError('No se pudo cargar el mapa');
      }
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [heatmapData]);

  const toggleChat = () => {
    setShowChat((prev) => !prev);
  };

  const handleLogout = () => {
    navigate('/login');
  };
    
  const stats = [
    {
      title: 'Total Users',
      value: userCount !== null ? userCount.toString() : 'Loading...',
      change: userCount !== null ? '+12%' : '',
      trend: 'up',
    },
    {
      title: 'Products',
      value: productCount !== null ? productCount.toString() : 'Loading...',
      change: productCount !== null ? '+5%' : '',
      trend: 'up',
    },
    { title: "Products saved today", value: "87", change: "-2%", trend: "down" },
    { title: "Income", value: "$12,345", change: "+18%", trend: "up" }
  ];

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>Admin Panel</h1>
        <div className="user-profile">
          <span>Admin</span>
          <div className="avatar">A</div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
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
          <h2>Heatmap de Accesos</h2>
          {mapError && <div className="map-error">{mapError}</div>}
          <div id="map" style={{ height: '400px', width: '100%' }}></div>
        </section>

        <section className="quick-actions">
          <h2>Acciones Rápidas</h2>
          <div className="action-buttons">
            <button className="action-btn">
              <span>+</span> Añadir Producto
            </button>
            <button className="action-btn">
              <span>👥</span> Gestionar Usuarios
            </button>
            <button className="action-btn">
              <span>📊</span> Generar Reporte
            </button>
            <button className="action-btn">
              <span>⚙️</span> Configuración
            </button>
          </div>
        </section>
      </div>
      <ChatBubble
        onClick={toggleChat}
        isOpen={showChat}
        onResponse={() => {}}
      />
    </div>
  );
};

export default AdminDashboard;