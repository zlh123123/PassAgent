export function formatContent(content) {
  let formattedContent = content;
  
  // 处理代码块
  const codeBlockRegex = /```([\s\S]*?)```/g;
  formattedContent = formattedContent.replace(codeBlockRegex, (match, code) => {
    return `<div class="code-block">
      <button class="copy-btn">复制</button>
      <pre><code>${escapeHtml(code)}</code></pre>
    </div>`;
  });
  
  // 处理内联代码
  const inlineCodeRegex = /`([^`]+)`/g;
  formattedContent = formattedContent.replace(inlineCodeRegex, '<code>$1</code>');
  
  // 处理换行
  formattedContent = formattedContent.replace(/\n/g, '<br>');
  
  return formattedContent;
}

export function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
