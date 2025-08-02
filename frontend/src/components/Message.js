import React from 'react';
import { formatContent } from '../utils/textUtils';

function Message({ message }) {
  return (
    <div className="message">
      <div className={`avatar ${message.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
        {message.role === 'user' ? '用' : 'P'}
      </div>
      <div className="message-content">
        <div dangerouslySetInnerHTML={{ __html: formatContent(message.content) }} />
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
