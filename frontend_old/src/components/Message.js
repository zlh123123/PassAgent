import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

function Message({ message }) {
  return (
    <div className="message">
      <div className={`avatar ${message.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
        {message.role === 'user' ? '用' : 'P'}
      </div>
      <div className="message-content">
        {message.role === 'assistant' ? (
          <MarkdownRenderer content={message.content} />
        ) : (
          <div className="user-message-content">{message.content}</div>
        )}
        {message.role === 'assistant' && (
          <div className="feedback-buttons">
            <button className="feedback-btn thumb-up" title="赞">👍</button>
            <button className="feedback-btn thumb-down" title="踩">👎</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;
