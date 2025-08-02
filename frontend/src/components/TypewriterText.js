import React, { useState, useEffect, useRef } from 'react';

function TypewriterText() {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [textArrayIndex, setTextArrayIndex] = useState(0);
  const timeoutRef = useRef(null);
  
  const textsToType = [
    "PassAgent：一个密码分析智能体，助您评估密码强度并提供改进建议。",
    "了解PassAgent：旨在分析和提高您的密码安全性的智能体。",
    "PassAgent运用先进AI技术，为您检测潜在的密码风险。"
  ];

  useEffect(() => {
    const currentText = textsToType[textArrayIndex];
    const typingSpeed = 50;
    const deletingSpeed = 30; 
    const pauseTime = 1500; 
    
    const tick = () => {
      if (!isDeleting) {
        // 正在输入
        if (currentIndex < currentText.length) {
          setDisplayText(currentText.substring(0, currentIndex + 1));
          setCurrentIndex(prev => prev + 1);
          timeoutRef.current = setTimeout(tick, typingSpeed);
        } else {
          // 输入完成，暂停后开始删除
          timeoutRef.current = setTimeout(() => {
            setIsDeleting(true);
            tick();
          }, pauseTime);
        }
      } else {
        // 正在删除
        if (currentIndex > 0) {
          setDisplayText(currentText.substring(0, currentIndex - 1));
          setCurrentIndex(prev => prev - 1);
          timeoutRef.current = setTimeout(tick, deletingSpeed);
        } else {
          // 删除完成，切换到下一个文本
          setIsDeleting(false);
          setTextArrayIndex(prev => (prev + 1) % textsToType.length);
          timeoutRef.current = setTimeout(tick, 300); // 从500ms减少到300ms
        }
      }
    };

    timeoutRef.current = setTimeout(tick, 300); // 从500ms减少到300ms

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [textArrayIndex, currentIndex, isDeleting]);

  return (
    <p className="welcome-subtitle">
      {displayText}
      <span className="cursor">|</span>
    </p>
  );
}

export default TypewriterText;
