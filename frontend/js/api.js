import { mockReviewResponse, mockHealthCheck, mockErrorResponses } from './mock.js';

const API_BASE_URL = 'http://localhost:8000';

// 🔒 安全修复：只在localhost或development环境下启用Mock
const IS_DEV_ENV = window.location.hostname === 'localhost' || 
                   window.location.hostname === '127.0.0.1';
const USE_MOCK_MODE = window.USE_MOCK === true && IS_DEV_ENV;

export async function checkHealth() {
  if (USE_MOCK_MODE) {
    console.log('[API] 使用Mock模式：健康检查');
    return mockHealthCheck;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

export async function submitReview(url) {
  // 🔒 修复1: URL格式验证（防止无效或恶意URL）
  if (!isValidGitHubPRUrl(url)) {
    throw new Error('无效的GitHub PR URL格式');
  }

  if (USE_MOCK_MODE || url.includes('test:')) {
    console.log('[API] 使用Mock模式：提交审查');
    return handleMockReview(url);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pr_url: url }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Request failed');
    }

    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Network error: Unable to connect to server');
    }
    throw error;
  }
}

function handleMockReview(url) {
  return new Promise((resolve, reject) => {
    if (!isValidGitHubPRUrl(url)) {
      setTimeout(() => {
        resolve(mockErrorResponses.invalid_url);
      }, 500);
      return;
    }

    setTimeout(() => {
      if (url.includes('test:rate_limit')) {
        resolve(mockErrorResponses.rate_limit);
      } else if (url.includes('test:not_found')) {
        resolve(mockErrorResponses.pr_not_found);
      } else if (url.includes('test:network_error')) {
        reject(new Error('Network error'));
      } else if (url.includes('test:timeout')) {
        resolve(mockErrorResponses.timeout);
      } else if (url.includes('test:empty')) {
        resolve(mockErrorResponses.empty_result);
      } else {
        resolve(mockReviewResponse);
      }
    }, 1500);
  });
}

// 🔒 URL格式验证（正则表达式）
export function isValidGitHubPRUrl(url) {
  // 安全改进：严格匹配GitHub PR URL格式
  const pattern = /^https?:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/pull\/\d+(\/.*)?$/;
  if (!pattern.test(url)) {
    console.warn('[API] URL验证失败:', url);
    return false;
  }
  return true;
}

// 🔒 修复2: 剪贴板API降级方案
export async function copyToClipboard(text) {
  try {
    // 优先使用现代Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return { success: true, method: 'clipboard-api' };
    }
    
    // 🔒 降级方案1: 使用document.execCommand（兼容性更好）
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    let success = false;
    try {
      success = document.execCommand('copy');
    } catch (err) {
      console.warn('[API] execCommand复制失败:', err);
    }
    
    document.body.removeChild(textArea);
    
    if (success) {
      return { success: true, method: 'execCommand' };
    }
    
    // 🔒 最终降级：显示文本让用户手动复制
    throw new Error('复制功能不可用');
    
  } catch (err) {
    console.error('[API] 复制失败:', err);
    // 最后降级：显示提示让用户手动复制
    if (window.confirm(`复制以下内容到剪贴板：\n\n${text}\n\n（按确定显示内容）`)) {
      alert(text);
    }
    return { success: false, error: err.message };
  }
}

export function getApiConfig() {
  return {
    baseUrl: API_BASE_URL,
    useMock: USE_MOCK_MODE,
    mode: USE_MOCK_MODE ? 'mock' : 'production',
    devEnvironment: IS_DEV_ENV
  };
}
