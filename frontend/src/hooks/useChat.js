import { useState, useCallback } from 'react';
import { generateAIResponse } from '../utils/aiUtils';

export function useChat() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);

  const createNewChat = useCallback(() => {
    const id = Date.now().toString();
    const conversation = {
      id: id,
      title: '新对话',
      messages: []
    };
    
    setConversations(prev => [conversation, ...prev]);
    setCurrentConversationId(id);
    setShowWelcome(false);
    
    return conversation;
  }, []);

  const loadConversation = useCallback((conversation) => {
    setCurrentConversationId(conversation.id);
    setShowWelcome(false);
  }, []);

  const sendMessage = useCallback(async (userMessage) => {
    if (!userMessage.trim() || isTyping) return;
    
    let currentConversation;
    if (!currentConversationId) {
      currentConversation = createNewChat();
    } else {
      currentConversation = conversations.find(c => c.id === currentConversationId);
    }
    
    const newMessage = {
      role: 'user',
      content: userMessage
    };
    
    setConversations(prev => prev.map(conv => 
      conv.id === currentConversation.id 
        ? { ...conv, messages: [...conv.messages, newMessage] }
        : conv
    ));
    
    if (currentConversation.messages.length === 0) {
      const title = userMessage.length > 25 ? userMessage.substring(0, 25) + '...' : userMessage;
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversation.id 
          ? { ...conv, title }
          : conv
      ));
    }
    
    setIsTyping(true);
    
    try {
      const aiResponse = await generateAIResponse(userMessage);
      
      const assistantMessage = {
        role: 'assistant',
        content: aiResponse
      };
      
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversation.id 
          ? { ...conv, messages: [...conv.messages, assistantMessage] }
          : conv
      ));
    } catch (error) {
      console.error('Error generating AI response:', error);
    } finally {
      setIsTyping(false);
    }
  }, [conversations, currentConversationId, isTyping, createNewChat]);

  const addFileMessage = useCallback((fileMessage) => {
    let targetConversationId = currentConversationId;
    
    if (!targetConversationId) {
      const newConv = createNewChat();
      targetConversationId = newConv.id;
    }
    
    setShowWelcome(false);
    
    const userMessage = {
      role: 'user',
      content: fileMessage.content,
      type: fileMessage.type,
      fileData: fileMessage.imageData || fileMessage.audioData,
      locationData: fileMessage.locationData,
      fileName: fileMessage.fileName
    };
    
    setConversations(prev => prev.map(conv => 
      conv.id === targetConversationId
        ? { ...conv, messages: [...conv.messages, userMessage] }
        : conv
    ));
  }, [currentConversationId, createNewChat]);

  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const currentMessages = currentConversation ? currentConversation.messages : [];

  return {
    conversations,
    currentConversationId,
    currentMessages,
    isTyping,
    showWelcome,
    createNewChat,
    loadConversation,
    sendMessage,
    addFileMessage
  };
}
