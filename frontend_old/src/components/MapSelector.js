import React, { useState, useRef, useEffect } from 'react';

function MapSelector({ isOpen, onClose, onPointsSelect }) {
  const [selectedPoints, setSelectedPoints] = useState([]);
  const [map, setMap] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const mapContainerRef = useRef(null);

  useEffect(() => {
    if (isOpen && mapContainerRef.current && window.AMap) {
      initMap();
    }
    return () => {
      if (map) {
        map.destroy();
      }
    };
  }, [isOpen]);

  const initMap = () => {
    try {
      // 创建高德地图实例
      const mapInstance = new window.AMap.Map(mapContainerRef.current, {
        zoom: 13,
        center: [116.397428, 39.90923], // 北京天安门
        mapStyle: 'amap://styles/normal',
        resizeEnable: true,
        rotateEnable: true,
        pitchEnable: true,
        zoomEnable: true,
        dragEnable: true
      });

      // 设置地图实例到state
      setMap(mapInstance);
      
      // 立即设置为已加载，因为地图实例已经创建
      setMapLoaded(true);

      // 立即添加点击事件
      mapInstance.on('click', (e) => {
        console.log('地图被点击:', e.lnglat);
        handleMapClick(e, mapInstance);
      });

      // 等待地图完全加载
      mapInstance.on('complete', () => {
        console.log('地图完全加载完成');
      });

      // 添加地理定位
      const geolocation = new window.AMap.Geolocation({
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
        convert: true,
        showButton: true,
        buttonPosition: 'LB',
        showMarker: true,
        showCircle: true,
        panToLocation: true,
        zoomToAccuracy: true,
      });

      mapInstance.addControl(geolocation);
      
      // 延迟执行定位
      setTimeout(() => {
        try {
          geolocation.getCurrentPosition();
        } catch (error) {
          console.log('定位失败:', error);
        }
      }, 1000);

    } catch (error) {
      console.error('地图初始化失败:', error);
    }
  };

  const handleMapClick = (e, mapInstance) => {
    console.log('handleMapClick 被调用, mapLoaded:', mapLoaded);
    
    // 只要地图实例存在就可以操作
    if (!mapInstance) {
      console.log('地图实例不存在');
      return;
    }

    try {
      const lnglat = e.lnglat;
      const clickLng = lnglat.lng;
      const clickLat = lnglat.lat;
      console.log('点击位置:', clickLng, clickLat);

      // 使用函数式更新来检查当前点数
      setSelectedPoints(prev => {
        console.log('当前选择点数', prev.length);
        
        // 检查是否已达到最大选择数量
        if (prev.length >= 3) {
          alert('最多只能选择3个位置点，请先删除已有位置再添加新位置。');
          return prev; // 返回原数组，不添加新点
        }
        
        const newPoint = {
          id: Date.now(),
          lng: clickLng,
          lat: clickLat,
          address: `${clickLat.toFixed(6)}, ${clickLng.toFixed(6)}`
        };

        // 创建标记
        const marker = new window.AMap.Marker({
          position: [clickLng, clickLat],
          icon: new window.AMap.Icon({
            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
            size: new window.AMap.Size(19, 33),
            imageSize: new window.AMap.Size(19, 33)
          }),
          title: `位置点: ${newPoint.address}`,
          extData: { pointId: newPoint.id }
        });

        // 添加到地图
        mapInstance.add(marker);
        console.log('标记添加成功');

        // 更新 markers 状态
        setMarkers(prevMarkers => [...prevMarkers, { id: newPoint.id, marker }]);

        // 返回新的点数组
        return [...prev, newPoint];
      });

    } catch (error) {
      console.error('添加标记失败:', error);
    }
  };

  const removePoint = (pointId) => {
    console.log('开始删除点:', pointId);
    
    setSelectedPoints(prev => prev.filter(point => point.id !== pointId));
    
    setMarkers(prev => {
      const markerObj = prev.find(m => m.id === pointId);
      if (markerObj && markerObj.marker && map) {
        try {
          // 使用高德地图正确的删除方法
          map.remove(markerObj.marker);
          // 或者使用 markerObj.marker.setMap(null);
          console.log('标记删除成功');
        } catch (error) {
          console.error('删除标记失败:', error);
          // 备用删除方法
          try {
            markerObj.marker.setMap(null);
          } catch (err) {
            console.error('备用删除方法也失败:', err);
          }
        }
      }
      return prev.filter(m => m.id !== pointId);
    });
  };

  const handleConfirm = () => {
    onPointsSelect(selectedPoints);
    setSelectedPoints([]);
    setMarkers([]);
    onClose();
  };

  const handleClear = () => {
    if (!map) return;

    try {
      // 批量删除所有标记
      const allMarkers = markers.map(m => m.marker).filter(Boolean);
      if (allMarkers.length > 0) {
        map.remove(allMarkers);
      }
      setSelectedPoints([]);
      setMarkers([]);
      console.log('清除所有标记成功');
    } catch (error) {
      console.error('清除标记失败:', error);
      // 备用清除方法
      markers.forEach(markerObj => {
        try {
          if (markerObj.marker) {
            markerObj.marker.setMap(null);
          }
        } catch (err) {
          console.error('备用清除失败:', err);
        }
      });
      setSelectedPoints([]);
      setMarkers([]);
    }
  };

  const centerToCurrentLocation = () => {
    if (!map) return;

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        try {
          const center = [position.coords.longitude, position.coords.latitude];
          map.setCenter(center);
          map.setZoom(15);
        } catch (error) {
          console.error('定位失败:', error);
        }
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="map-selector-container">
      <div className="map-selector-header">
        <h4>高德地图选点</h4>
        <div className="map-controls">
          <button 
            className="map-btn" 
            onClick={centerToCurrentLocation} 
            title="定位到当前位置"
          >
            📍
          </button>
          <button 
            className="map-btn clear-btn" 
            onClick={handleClear}
          >
            清除({selectedPoints.length})
          </button>
          <button className="map-btn close-btn" onClick={onClose}>
            ✕
          </button>
        </div>
      </div>
      
      <div 
        ref={mapContainerRef}
        className="amap-container"
      />
      
      <div className="map-usage-info">
        <div className="usage-tips">
          💡 使用提示：点击地图添加标记 • 支持缩放和拖拽
        </div>
      </div>
      
      <div className="map-selector-footer">
        <div className="points-info">
          已选择 {selectedPoints.length}/3 个位置
          {selectedPoints.length > 0 && (
            <div className="points-list">
              {selectedPoints.map((point, index) => (
                <div key={point.id} className="point-item">
                  <span className="point-number">#{index + 1}</span>
                  <span className="point-coords">{point.lat.toFixed(4)}, {point.lng.toFixed(4)}</span>
                  <button 
                    className="point-remove-btn"
                    onClick={() => removePoint(point.id)}
                    title="删除此点"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        <button 
          className="map-btn confirm-btn" 
          onClick={handleConfirm}
          disabled={selectedPoints.length === 0}
        >
          确定选择 ({selectedPoints.length})
        </button>
      </div>
    </div>
  );
}

export default MapSelector;
