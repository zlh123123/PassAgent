import React from 'react';
import TypewriterText from './TypewriterText';

function WelcomeScreen({ onExampleClick }) {
  const examples = [
    "分析密码'Password123!'的安全性",
    "我喜欢猫咪和咖啡，请帮我生成一个密码",
    "检测我的密码'100200abc'是否被泄露",
    "帮我的密码'Password123!'进行合规性检查",
  ];

  return (
    <div className="welcome-container">
      <h1 className="welcome-title">欢迎使用 PassAgent🤗</h1>
      <TypewriterText />
      <div className="examples">
        {examples.map((example, index) => (
          <div 
            key={index}
            className="example" 
            onClick={() => onExampleClick(example)}
          >
            <p>{example}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WelcomeScreen;
