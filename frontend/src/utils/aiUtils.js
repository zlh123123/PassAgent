import { chatAPI } from './api';

export async function generateAIResponse(userMessage) {
  try {
    // 调用后端API
    const response = await chatAPI.sendMessage(userMessage);
    return response.message || response.content || '抱歉，我无法处理您的请求。';
  } catch (error) {
    console.error('AI响应生成失败:', error);
    
    // 如果API调用失败，返回模拟响应
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    let fallbackResponse = '';
    
    if (userMessage.toLowerCase().includes('你好') || userMessage.toLowerCase().includes('hello')) {
      fallbackResponse = '你好！我是PassAgent，一个密码分析AI助手。我能帮助您评估密码强度并提供改进建议。您有什么需要帮助的吗？（注意：当前为离线模式）';
    } else if (userMessage.toLowerCase().includes('密码') || userMessage.toLowerCase().includes('password')) {
      fallbackResponse = '我可以帮助您分析密码强度。一个强密码应该包含：\n\n• 至少8个字符\n• 大小写字母混合\n• 数字和特殊字符\n• 避免常见词汇和个人信息\n\n请告诉我您想要分析的密码，我会为您提供详细的安全评估。（注意：当前为离线模式）';
    } else {
      fallbackResponse = '感谢您使用PassAgent！我是专门用于密码安全分析的AI助手。请告诉我您需要什么帮助？（注意：当前为离线模式）';
    }
    
    return fallbackResponse;
  }
}