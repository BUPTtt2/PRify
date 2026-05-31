import { mockReviewResponse, mockHealthCheck, mockErrorResponses } from './mock.js';

const API_BASE_URL = 'http://localhost:8000';
const USE_MOCK_MODE = window.USE_MOCK === true;

export async function checkHealth() {
  if (USE_MOCK_MODE) {
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
  if (USE_MOCK_MODE || url.includes('test:')) {
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

export function isValidGitHubPRUrl(url) {
  const pattern = /^https?:\/\/github\.com\/[\w-]+\/[\w-]+\/pull\/\d+(\/.*)?$/;
  return pattern.test(url);
}

export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('复制失败:', err);
    return false;
  }
}

export function getApiConfig() {
  return {
    baseUrl: API_BASE_URL,
    useMock: USE_MOCK_MODE,
    mode: USE_MOCK_MODE ? 'mock' : 'production'
  };
}
