import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfile, updateProfile } from '../../api/profile';
import { logout } from '../../api/auth';
import './styles.css';

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getProfile();
      setProfile(data);
      setFormData({
        username: data.username || '',
        email: data.email || ''
      });
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Не удалось загрузить профиль');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const updatedProfile = await updateProfile(formData);
      setProfile(updatedProfile);
      setSuccess('Профиль успешно обновлен');
      setIsEditing(false);
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.details) {
        const details = err.response.data.details;
        const errorMessages = Object.values(details).flat().join(', ');
        setError(errorMessages);
      } else {
        setError('Не удалось обновить профиль');
      }
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout error:', err);
      navigate('/login');
    }
  };

  const handleCancel = () => {
    setFormData({
      username: profile.username || '',
      email: profile.email || ''
    });
    setIsEditing(false);
    setError('');
    setSuccess('');
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="profile-container" data-easytag="id1-react/src/components/Profile/index.jsx">
        <div className="profile-loading">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="profile-container" data-easytag="id1-react/src/components/Profile/index.jsx">
      <div className="profile-card">
        <div className="profile-header">
          <h1>Профиль</h1>
          <button 
            className="btn-back"
            onClick={() => navigate('/chat')}
            type="button"
          >
            ← Вернуться в чат
          </button>
        </div>

        {error && <div className="profile-error">{error}</div>}
        {success && <div className="profile-success">{success}</div>}

        <div className="profile-content">
          {!isEditing ? (
            <>
              <div className="profile-info">
                <div className="profile-field">
                  <label>Имя пользователя</label>
                  <div className="profile-value">{profile?.username}</div>
                </div>

                <div className="profile-field">
                  <label>Email</label>
                  <div className="profile-value">{profile?.email}</div>
                </div>

                {profile?.created_at && (
                  <div className="profile-field">
                    <label>Дата регистрации</label>
                    <div className="profile-value">{formatDate(profile.created_at)}</div>
                  </div>
                )}
              </div>

              <div className="profile-actions">
                <button 
                  className="btn-edit"
                  onClick={() => setIsEditing(true)}
                  type="button"
                >
                  Редактировать профиль
                </button>
                <button 
                  className="btn-logout"
                  onClick={handleLogout}
                  type="button"
                >
                  Выйти из аккаунта
                </button>
              </div>
            </>
          ) : (
            <form onSubmit={handleSubmit} className="profile-form">
              <div className="form-group">
                <label htmlFor="username">Имя пользователя</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="form-input"
                  maxLength={150}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="form-input"
                />
              </div>

              {profile?.created_at && (
                <div className="profile-field">
                  <label>Дата регистрации</label>
                  <div className="profile-value">{formatDate(profile.created_at)}</div>
                </div>
              )}

              <div className="form-actions">
                <button type="submit" className="btn-save">
                  Сохранить изменения
                </button>
                <button 
                  type="button" 
                  className="btn-cancel"
                  onClick={handleCancel}
                >
                  Отмена
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
