import { mockReviewResponse, mockHealthCheck } from './mock.js';

export async function checkHealth() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockHealthCheck);
    }, 500);
  });
}

export async function submitReview(url) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockReviewResponse);
    }, 2000);
  });
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
