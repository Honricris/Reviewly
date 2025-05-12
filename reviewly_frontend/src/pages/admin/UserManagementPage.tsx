import React, { useState, useEffect } from 'react';
import Header from '../../components/Header';
import '../../styles/AdminDashboard.css';
import '../../styles/UserManagement.css';
import userService from '../../services/userService';

interface User {
  id: number;
  email: string | null;
  role: string;
  github_id?: number | null;
  created_at: string;
}

const UserManagementPage = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const userList = await userService.getAllUsers();
      setUsers(userList);
      setError(null);
    } catch (err) {
      setError('Error loading users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await userService.updateUser(userId, { role: newRole });
      setUsers(users.map(user => 
        user.id === userId ? { ...user, role: newRole } : user
      ));
    } catch (err) {
      setError('Error updating role');
      console.error(err);
    }
  };

  const handleDelete = async (userId: number) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await userService.deleteUser(userId);
        setUsers(users.filter(user => user.id !== userId));
      } catch (err) {
        setError('Error deleting user');
        console.error(err);
      }
    }
  };

  const filteredUsers = users.filter(user => {
    const email = user.email ?? '';
    return (
      email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.id.toString().includes(searchTerm)
    );
  });

  return (
    <div className="admin-dashboard">
      <Header
        buttonConfig={{ showHome: true, showFavourites: false, showLogout: true, isAdmin: true }}
        showSearchBar={false}
      />
      <div className="dashboard-container">
        <div className="user-management-page">
          <input
            type="text"
            placeholder="Search by email or ID..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-bar"
          />
          {error && <div className="error-message">{error}</div>}
          {loading ? (
            <div>Loading...</div>
          ) : (
            <div className="user-list">
              {filteredUsers.map(user => (
                <div key={user.id} className="user-item">
                  <div className="user-info">
                    <span>ID: {user.id}</span>
                    <span>{user.email ?? 'No email'}</span>
                    {user.github_id !== null && user.github_id !== undefined && (
                      <span className="github-indicator">Registered with GitHub</span>
                    )}
                  </div>
                  <div className="user-actions">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className="role-select"
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(user.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserManagementPage;