import { mockReviewResponse, mockHealthCheck, mockErrorResponses } from './mock.js';

export async function checkHealth() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockHealthCheck);
    }, 500);
  });
}

export async function submitReview(url) {
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
