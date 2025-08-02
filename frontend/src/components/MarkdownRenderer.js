import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

function MarkdownRenderer({ content, className = '' }) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          // 代码块渲染
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            if (!inline && language) {
              return (
                <div className="code-block-container">
                  <div className="code-block-header">
                    <span className="code-language">{language}</span>
                    <button 
                      className="copy-code-btn"
                      onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                    >
                      复制
                    </button>
                  </div>
                  <SyntaxHighlighter
                    style={tomorrow}
                    language={language}
                    PreTag="div"
                    customStyle={{
                      margin: 0,
                      borderRadius: '0 0 6px 6px',
                      backgroundColor: 'var(--code-bg)',
                    }}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                </div>
              );
            }
            
            // 内联代码
            return (
              <code className="inline-code" {...props}>
                {children}
              </code>
            );
          },
          
          // 表格渲染
          table({ children }) {
            return (
              <div className="table-container">
                <table className="markdown-table">{children}</table>
              </div>
            );
          },
          
          // 链接渲染
          a({ href, children }) {
            return (
              <a 
                href={href} 
                target="_blank" 
                rel="noopener noreferrer"
                className="markdown-link"
              >
                {children}
              </a>
            );
          },
          
          // 引用块渲染
          blockquote({ children }) {
            return <blockquote className="markdown-blockquote">{children}</blockquote>;
          },
          
          // 列表渲染
          ul({ children }) {
            return <ul className="markdown-list">{children}</ul>;
          },
          
          ol({ children }) {
            return <ol className="markdown-list ordered">{children}</ol>;
          },
          
          // 标题渲染
          h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
          h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
          h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
          h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,
          h5: ({ children }) => <h5 className="markdown-h5">{children}</h5>,
          h6: ({ children }) => <h6 className="markdown-h6">{children}</h6>,
          
          // 段落渲染
          p({ children }) {
            return <p className="markdown-paragraph">{children}</p>;
          },
          
          // 水平线渲染
          hr() {
            return <hr className="markdown-hr" />;
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
