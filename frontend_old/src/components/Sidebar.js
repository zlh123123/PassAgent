import React from 'react';
import logo from '../logo.svg';

function Sidebar({ 
  conversations, 
  currentConversationId, 
  onNewChat, 
  onConversationSelect, 
  sidebarCollapsed, 
  onToggleSidebar, 
  theme, 
  onToggleTheme 
}) {
  return (
    <div className={`sidebar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`} id="sidebar">
      <button className="collapse-btn" onClick={onToggleSidebar} title="收缩/展开侧边栏">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      
      <div className="logo">
        <div className="logo-icon">
          <img src={logo} alt="PassAgent" />
        </div>
        <span>PassAgent</span>
      </div>
      
      <button className="new-chat-btn" onClick={onNewChat}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        新对话
      </button>
      
      <div className="history">
        {conversations.map(conv => (
          <div 
            key={conv.id}
            className={`history-item ${conv.id === currentConversationId ? 'active' : ''}`}
            onClick={() => onConversationSelect(conv)}
          >
            {conv.title}
          </div>
        ))}
      </div>
      
      <button className="theme-toggle-btn" onClick={onToggleTheme}>
        <svg className="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.106a.75.75 0 010 1.06l-1.591 1.59a.75.75 0 11-1.06-1.06l1.59-1.591a.75.75 0 011.06 0zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5h2.25a.75.75 0 01.75.75zM17.894 17.894a.75.75 0 011.06 0l1.591 1.59a.75.75 0 11-1.06 1.06l-1.59-1.591a.75.75 0 010-1.06zM12 17.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V18a.75.75 0 01.75-.75zM5.106 17.894a.75.75 0 010 1.06l-1.591 1.59a.75.75 0 11-1.06-1.06l1.59-1.591a.75.75 0 011.06 0zM4.5 12a.75.75 0 01-.75.75H1.5a.75.75 0 010-1.5h2.25a.75.75 0 01.75.75zM6.106 5.106a.75.75 0 011.06 0l1.591 1.59a.75.75 0 01-1.06 1.06L6.106 6.167a.75.75 0 010-1.06z"></path>
        </svg>
        <svg className="moon-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fillRule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-3.51 1.713-6.622 4.369-8.552a.75.75 0 01.818.162z" clipRule="evenodd"></path>
        </svg>
      </button>
    </div>
  );
}

export default Sidebar;
