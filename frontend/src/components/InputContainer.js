import React, { useRef, useEffect, useState } from 'react';
import MapSelector from './MapSelector';

function InputContainer({ 
  inputValue, 
  onInputChange, 
  onSendMessage, 
  isTyping,
  onImageUpload,
  onAudioUpload,
  onLocationSelect
}) {
  const inputRef = useRef(null);
  const imageInputRef = useRef(null);
  const audioInputRef = useRef(null);
  const [showMapSelector, setShowMapSelector] = useState(false);

  const adjustTextareaHeight = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      const height = inputRef.current.scrollHeight > 200 ? 200 : inputRef.current.scrollHeight;
      inputRef.current.style.height = height + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  const handleInputChange = (e) => {
    onInputChange(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && !isTyping) {
        onSendMessage();
      }
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      onImageUpload(file);
    }
    e.target.value = '';
  };

  const handleAudioUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      onAudioUpload(file);
    }
    e.target.value = '';
  };

  const handleLocationClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Location button clicked, current state:', showMapSelector);
    setShowMapSelector(prev => {
      console.log('Setting showMapSelector from', prev, 'to', !prev);
      return !prev;
    });
  };

  const handleMapClose = () => {
    console.log('Map closing'); // 添加调试日志
    setShowMapSelector(false);
  };

  const handlePointsSelect = (points) => {
    console.log('Points selected:', points); // 添加调试日志
    onLocationSelect(points);
    setShowMapSelector(false);
  };

  console.log('InputContainer render - showMapSelector:', showMapSelector);

  return (
    <>
      <div className="input-container">
        {showMapSelector && (
          <div className="map-selector-overlay">
            <MapSelector
              isOpen={showMapSelector}
              onClose={handleMapClose}
              onPointsSelect={handlePointsSelect}
            />
          </div>
        )}
        
        <div className="input-wrapper">
          <div className="input-actions">
            <button 
              className="action-btn"
              onClick={() => imageInputRef.current?.click()}
              title="上传图片"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21,15 16,10 5,21"/>
              </svg>
            </button>
            
            <button 
              className="action-btn"
              onClick={() => audioInputRef.current?.click()}
              title="上传音频"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>
            
            <button 
              className="action-btn"
              onClick={handleLocationClick}
              title="地图选点"
              type="button"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </button>
          </div>

          <textarea
            ref={inputRef}
            className="input-box"
            placeholder="输入消息..."
            rows="1"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
          />
          
          <button 
            className={`send-btn ${isTyping ? 'loading' : ''}`}
            onClick={onSendMessage}
            disabled={isTyping || !inputValue.trim()}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
            <div className="send-spinner"></div>
          </button>
        </div>

        {/* 隐藏的文件输入 */}
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleImageUpload}
        />
        
        <input
          ref={audioInputRef}
          type="file"
          accept="audio/*"
          style={{ display: 'none' }}
          onChange={handleAudioUpload}
        />
      </div>
    </>
  );
}

export default InputContainer;
