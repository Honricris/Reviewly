import React, { useState, useEffect } from 'react';
import userService from '../../services/userService';
import '../../styles/UserManagement.css';

interface User {
  id: number;
  email: string | null;
  role: string;
  github_id?: number | null; 
  created_at: string;
}

const UserManagement: React.FC<{ onClose: () => void }> = ({ onClose }) => {
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
    <div className="user-management-overlay">
      <div className="user-management-modal">
        <div className="modal-header">
          <h2>Manage Users</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
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
  );
};

export default UserManagement;