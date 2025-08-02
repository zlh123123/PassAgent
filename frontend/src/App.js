import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import WelcomeScreen from './components/WelcomeScreen';
import ChatContainer from './components/ChatContainer';
import InputContainer from './components/InputContainer';
import LocationModal from './components/LocationModal';
import { useChat } from './hooks/useChat';
import { useTheme } from './hooks/useTheme';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [locationModalOpen, setLocationModalOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const {
    conversations,
    currentConversationId,
    currentMessages,
    isTyping,
    showWelcome,
    createNewChat,
    loadConversation,
    sendMessage,
    addFileMessage
  } = useChat();

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleNewChatClick = () => {
    if (currentConversationId) {
      const currentConv = conversations.find(c => c.id === currentConversationId);
      if (currentConv && currentConv.messages.length === 0) {
        return;
      }
    }
    createNewChat();
  };

  const handleSendMessage = () => {
    sendMessage(inputValue);
    setInputValue('');
  };

  const handleExampleClick = (text) => {
    createNewChat();
    setInputValue(text);
    setTimeout(() => {
      sendMessage(text);
      setInputValue('');
    }, 100);
  };

  const handleImageUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageMessage = {
        type: 'image',
        content: `[图片: ${file.name}]`,
        imageData: e.target.result,
        fileName: file.name
      };
      addFileMessage(imageMessage);
    };
    reader.readAsDataURL(file);
  };

  const handleAudioUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const audioMessage = {
        type: 'audio',
        content: `[音频: ${file.name}]`,
        audioData: e.target.result,
        fileName: file.name
      };
      addFileMessage(audioMessage);
    };
    reader.readAsDataURL(file);
  };

  const handleLocationSelect = (points) => {
    if (points.length > 0) {
      const locationMessage = {
        type: 'location',
        content: `[已选择 ${points.length} 个地图位置]`,
        locationData: points
      };
      addFileMessage(locationMessage);
    }
  };

  return (
    <div className="container">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onNewChat={handleNewChatClick}
        onConversationSelect={loadConversation}
        sidebarCollapsed={sidebarCollapsed}
        onToggleSidebar={toggleSidebar}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      
      <div className="main">
        {showWelcome ? (
          <WelcomeScreen onExampleClick={handleExampleClick} />
        ) : (
          <ChatContainer messages={currentMessages} isTyping={isTyping} />
        )}
        
        <InputContainer
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSendMessage={handleSendMessage}
          isTyping={isTyping}
          onImageUpload={handleImageUpload}
          onAudioUpload={handleAudioUpload}
          onLocationSelect={handleLocationSelect}
        />
      </div>

      <LocationModal
        isOpen={locationModalOpen}
        onClose={() => setLocationModalOpen(false)}
        onLocationSelect={handleLocationSelect}
      />
    </div>
  );
}

export default App;
