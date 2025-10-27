const API_BASE_URL = 'http://localhost:8080/api/v1';

export const chatAPI = {
  sendMessage: async (message) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          content: message,  // 改为 content
          message_type: "text"  // 添加消息类型
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API调用失败:', error);
      throw error;
    }
  }
};

export const passwordAPI = {
  analyzePassword: async (password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/password/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('密码分析API调用失败:', error);
      throw error;
    }
  }
};

export const checkBackendConnection = async () => {
  try {
    const response = await fetch('http://localhost:8080/health');
    return response.ok;
  } catch (error) {
    console.error('后端连接检查失败:', error);
    return false;
  }
};