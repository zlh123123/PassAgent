import React from 'react';
import Message from './Message';
import TypingIndicator from './TypingIndicator';

function ChatContainer({ messages, isTyping }) {
  return (
    <div className="chat-container">
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      {isTyping && <TypingIndicator />}
    </div>
  );
}

export default ChatContainer;
