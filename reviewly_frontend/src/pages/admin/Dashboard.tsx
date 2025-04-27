import '../../styles/AdminDashboard.css';
import ChatBubble from '../../components/ChatBubble';
import React, { useState, useEffect, useRef } from 'react';
import userService from '../../services/userService';
import { getProductCount } from '../../services/productService';

const AdminDashboard = () => {
    const [showChat, setShowChat] = useState(false);
    const [userCount, setUserCount] = useState<number | null>(null);
    const [productCount, setProductCount] = useState<number | null>(null);

    useEffect(() => {
        const fetchCounts = async () => {
        try {
            const [userCount, productCount] = await Promise.all([
            userService.getUserCount(),
            getProductCount(),
            ]);
            setUserCount(userCount);
            setProductCount(productCount);
        } catch (error) {
            console.error('Failed to fetch counts:', error);
            setUserCount(0);
            setProductCount(0);
        }
        };
        fetchCounts();
    }, []);

    const toggleChat = () => {
        setShowChat((prev) => !prev);
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

    const recentOrders = [
        { id: "#12345", customer: "Juan Pérez", date: "2023-05-15", amount: "$125.00", status: "Completado" },
        { id: "#12346", customer: "María García", date: "2023-05-15", amount: "$89.50", status: "En proceso" },
        { id: "#12347", customer: "Carlos López", date: "2023-05-14", amount: "$234.00", status: "Completado" },
        { id: "#12348", customer: "Ana Martínez", date: "2023-05-14", amount: "$56.75", status: "Cancelado" }
    ];

    return (
        <div className="admin-dashboard">
            <header className="dashboard-header">
                <h1>Admin Panel</h1>
                <div className="user-profile">
                    <span>Admin</span>
                    <div className="avatar">A</div>
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
                <section className="recent-orders">
                    <h2>Órdenes Recientes</h2>
                    <div className="orders-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Cliente</th>
                                    <th>Fecha</th>
                                    <th>Monto</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentOrders.map((order, index) => (
                                    <tr key={index}>
                                        <td>{order.id}</td>
                                        <td>{order.customer}</td>
                                        <td>{order.date}</td>
                                        <td>{order.amount}</td>
                                        <td><span className={`status-badge ${order.status.toLowerCase().replace(' ', '-')}`}>{order.status}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
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