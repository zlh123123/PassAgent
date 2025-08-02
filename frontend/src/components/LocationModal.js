import React, { useState, useEffect } from 'react';

function LocationModal({ isOpen, onClose, onLocationSelect }) {
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getCurrentLocation = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('您的浏览器不支持地理定位');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          address: `纬度: ${position.coords.latitude.toFixed(6)}, 经度: ${position.coords.longitude.toFixed(6)}`
        };
        setCurrentLocation(location);
        setLoading(false);
      },
      (error) => {
        setError('无法获取位置信息，请检查权限设置');
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 600000
      }
    );
  };

  const handleLocationSelect = () => {
    if (currentLocation) {
      onLocationSelect(currentLocation);
      onClose();
    }
  };

  useEffect(() => {
    if (isOpen) {
      getCurrentLocation();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>选择位置</h3>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div className="modal-body">
          {loading && (
            <div className="location-loading">
              <div className="spinner"></div>
              <p>正在获取位置信息...</p>
            </div>
          )}
          
          {error && (
            <div className="location-error">
              <p>{error}</p>
              <button className="retry-btn" onClick={getCurrentLocation}>
                重试
              </button>
            </div>
          )}
          
          {currentLocation && (
            <div className="location-info">
              <div className="location-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <div className="location-details">
                <p><strong>当前位置</strong></p>
                <p>{currentLocation.address}</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose}>
            取消
          </button>
          <button 
            className="confirm-btn" 
            onClick={handleLocationSelect}
            disabled={!currentLocation}
          >
            发送位置
          </button>
        </div>
      </div>
    </div>
  );
}

export default LocationModal;
