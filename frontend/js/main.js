import { checkHealth, submitReview, isValidGitHubPRUrl, copyToClipboard } from './api.js';

const healthStatusEl = document.getElementById('health-status');
const reviewForm = document.getElementById('review-form');
const prUrlInput = document.getElementById('pr-url');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingSection = document.getElementById('loading-section');
const resultSection = document.getElementById('result-section');
let toastContainer = null;
let isSubmitting = false;

async function init() {
  initThemeToggle();
  await checkHealthStatus();
  setupEventListeners();
  initToastContainer();
}

function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('dark-mode', isDark);
      console.log('[Main] 主题切换:', isDark ? '深色模式' : '浅色模式');
    });
  }
}

function initToastContainer() {
  toastContainer = document.createElement('div');
  toastContainer.id = 'toast-container';
  toastContainer.className = 'fixed top-6 right-6 z-50 space-y-3';
  document.body.appendChild(toastContainer);
}

async function checkHealthStatus() {
  try {
    const response = await checkHealth();
    console.log('[Main] 健康检查响应:', response);
    
    if (response && response.status === 'ok') {
      healthStatusEl.innerHTML = `
        <div class="health-indicator">
          <div class="health-dot healthy"></div>
          <span class="text-stone-600">Online</span>
        </div>
      `;
      console.log('[Main] ✅ 后端服务正常');
    } else {
      healthStatusEl.innerHTML = `
        <div class="health-indicator">
          <div class="health-dot unhealthy"></div>
          <span class="text-stone-500">Degraded</span>
        </div>
      `;
    }
  } catch (error) {
    console.error('[Main] ❌ 健康检查失败:', error);
    healthStatusEl.innerHTML = `
      <div class="health-indicator">
        <div class="health-dot unhealthy"></div>
        <span class="text-stone-500">Offline</span>
      </div>
    `;
    showToast('无法连接到后端服务', 'error');
  }
}

function setupEventListeners() {
  reviewForm.addEventListener('submit', handleSubmit);
  prUrlInput.addEventListener('input', validateUrlInput);
}

function validateUrlInput() {
  const url = prUrlInput.value.trim();
  
  if (!url) {
    prUrlInput.classList.remove('border-rose-300', 'border-emerald-300');
    prUrlInput.classList.add('border-stone-200');
    return;
  }
  
  if (isValidGitHubPRUrl(url)) {
    prUrlInput.classList.remove('border-stone-200', 'border-rose-300');
    prUrlInput.classList.add('border-emerald-300', 'ring-2', 'ring-emerald-200');
  } else {
    prUrlInput.classList.remove('border-stone-200', 'border-emerald-300');
    prUrlInput.classList.add('border-rose-300', 'ring-2', 'ring-rose-200');
  }
}

async function handleSubmit(e) {
  e.preventDefault();
  
  if (isSubmitting) {
    console.log('[Main] 正在提交中，忽略重复点击');
    return;
  }
  
  const url = prUrlInput.value.trim();
  if (!url) {
    showToast('请输入 GitHub PR URL', 'warning');
    return;
  }

  if (!isValidGitHubPRUrl(url)) {
    showToast('无效的 GitHub PR URL 格式', 'error');
    return;
  }

  isSubmitting = true;
  showLoading(true);

  try {
    console.log('[Main] 提交审查请求:', url);
    const response = await submitReview(url);
    console.log('[Main] 收到响应:', response);
    
    if (response.success) {
      console.log('[Main] ✅ 分析成功');
      renderResult(response.data);
    } else {
      console.error('[Main] ❌ 分析失败:', response.error);
      showToast(response.error || '分析失败', 'error');
    }
  } catch (error) {
    console.error('[Main] ❌ 请求异常:', error);
    showToast('网络错误，请检查网络连接', 'error');
  } finally {
    isSubmitting = false;
    showLoading(false);
  }
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type} px-4 py-3 rounded-lg shadow-lg flex items-center space-x-3 fade-in max-w-sm`;
  
  const icons = {
    success: '<svg class="w-5 h-5 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7"/></svg>',
    error: '<svg class="w-5 h-5 text-rose-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 18L18 6M6 6l12 12"/></svg>',
    warning: '<svg class="w-5 h-5 text-amber-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    info: '<svg class="w-5 h-5 text-sky-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
  };
  
  toast.innerHTML = `
    ${icons[type]}
    <span class="text-sm font-medium">${message}</span>
    <button class="toast-close ml-auto text-stone-400 hover:text-stone-600">
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 18L18 6M6 6l12 12"/></svg>
    </button>
  `;
  
  toastContainer.appendChild(toast);
  
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.remove();
  });
  
  setTimeout(() => {
    if (toast.parentNode) {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

function showLoading(isLoading) {
  if (isLoading) {
    loadingSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    analyzeBtn.disabled = true;
    prUrlInput.disabled = true;
    analyzeBtn.classList.add('opacity-50', 'cursor-not-allowed');
  } else {
    loadingSection.classList.add('hidden');
    analyzeBtn.disabled = false;
    prUrlInput.disabled = false;
    analyzeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
  }
}

function renderResult(data) {
  const { pr_info, summary, risks, total_files, processing_time } = data;
  
  const groupedRisks = {
    high: risks.filter(r => r.level === 'high'),
    medium: risks.filter(r => r.level === 'medium'),
    low: risks.filter(r => r.level === 'low')
  };
  
  const riskLevels = [
    { key: 'high', label: 'High Risk', color: 'rose', bgClass: 'bg-rose-50/50', borderClass: 'border-rose-200', badgeClass: 'bg-rose-100 text-rose-700' },
    { key: 'medium', label: 'Medium Risk', color: 'amber', bgClass: 'bg-amber-50/50', borderClass: 'border-amber-200', badgeClass: 'bg-amber-100 text-amber-700' },
    { key: 'low', label: 'Low Risk', color: 'sky', bgClass: 'bg-sky-50/50', borderClass: 'border-sky-200', badgeClass: 'bg-sky-100 text-sky-700' }
  ];
  
  resultSection.innerHTML = `
    <div class="bg-white rounded-lg border border-stone-200 fade-in">
      <div class="p-8 md:p-10 border-b border-stone-200">
        <div class="mb-8">
          <h2 class="text-xl md:text-2xl font-light text-stone-800 mb-4 leading-relaxed">${pr_info.title}</h2>
          <div class="flex flex-wrap gap-x-6 gap-y-3 text-sm text-stone-500">
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="7" r="4"/>
                <path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2"/>
              </svg>
              <span>${pr_info.author}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <span>Files: ${pr_info.files_count}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 14l4-4 6 6 4-4"/>
              </svg>
              <span>+${pr_info.additions}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-rose-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 10l4 4 6-6 4 4"/>
              </svg>
              <span>-${pr_info.deletions}</span>
            </div>
          </div>
        </div>

        <div class="mb-10">
          <h3 class="text-sm font-medium text-stone-400 uppercase tracking-wider mb-4">Summary</h3>
          <p class="text-stone-600 font-light leading-relaxed">${summary}</p>
        </div>

        <div>
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-sm font-medium text-stone-400 uppercase tracking-wider">Risk Assessment</h3>
            <span class="text-sm text-stone-500 font-light">${risks.length} item${risks.length !== 1 ? 's' : ''}</span>
          </div>

          ${riskLevels.map(level => groupedRisks[level.key].length > 0 ? `
          <div class="risk-group mb-6 last:mb-0">
            <button class="risk-group-header w-full flex items-center justify-between p-4 rounded-lg border ${level.borderClass} ${level.bgClass} hover:opacity-80 transition-opacity duration-200" data-risk-level="${level.key}">
              <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${level.badgeClass}">
                  ${level.label}
                </span>
                <span class="text-sm text-stone-500">${groupedRisks[level.key].length} item${groupedRisks[level.key].length !== 1 ? 's' : ''}</span>
              </div>
              <svg class="risk-chevron w-5 h-5 text-stone-400 transition-transform duration-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </button>
            <div class="risk-group-content hidden mt-3 pl-2 space-y-3" data-risk-level="${level.key}">
              ${groupedRisks[level.key].map((risk, index) => `
                <div class="risk-card rounded-lg border ${level.borderClass} ${level.bgClass} p-5">
                  <div class="flex items-start justify-between mb-3">
                    <span class="text-xs text-stone-500 font-mono">${risk.file}:${risk.line}</span>
                    <button class="copy-suggestion-btn text-stone-400 hover:text-stone-600 transition-colors duration-200 p-1" data-suggestion="${escapeHtml(risk.suggestion)}" title="Copy suggestion">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="9" y="9" width="13" height="13" rx="2"/>
                        <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                      </svg>
                    </button>
                  </div>

                  <div class="space-y-2.5">
                    <div class="flex items-start space-x-2">
                      <span class="text-xs font-medium text-stone-400 uppercase tracking-wider mt-0.5">Type</span>
                      <span class="text-sm text-stone-700">${risk.type}</span>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="text-xs font-medium text-stone-400 uppercase tracking-wider mt-0.5">Issue</span>
                      <span class="text-sm text-stone-700">${risk.description}</span>
                    </div>
                    <div class="flex items-start space-x-2">
                      <span class="text-xs font-medium text-stone-400 uppercase tracking-wider mt-0.5">Suggestion</span>
                      <span class="text-sm text-stone-700">${risk.suggestion}</span>
                    </div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
          ` : '').join('')}
        </div>
      </div>

      <div class="px-8 md:px-10 py-6 border-t border-stone-200">
        <div class="flex items-center justify-between text-sm text-stone-500">
          <div class="flex items-center space-x-2">
            <svg class="w-4 h-4 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>Processed in ${processing_time}s</span>
          </div>
          <button id="copy-btn" class="flex items-center space-x-2 text-stone-600 hover:text-stone-800 transition-colors duration-200">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="9" y="9" width="13" height="13" rx="2"/>
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
            </svg>
            <span>Copy report</span>
          </button>
        </div>
      </div>
    </div>
  `;

  resultSection.classList.remove('hidden');
  
  setupRiskGroupListeners();
  setupCopySuggestionListeners();
  
  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => handleCopy(data));
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function setupRiskGroupListeners() {
  document.querySelectorAll('.risk-group-header').forEach(header => {
    header.addEventListener('click', () => {
      const level = header.getAttribute('data-risk-level');
      const content = document.querySelector(`.risk-group-content[data-risk-level="${level}"]`);
      const chevron = header.querySelector('.risk-chevron');

      content.classList.toggle('hidden');
      chevron.classList.toggle('rotate-180');
    });
  });
}

function setupCopySuggestionListeners() {
  document.querySelectorAll('.copy-suggestion-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const suggestion = btn.getAttribute('data-suggestion');
      
      const result = await copyToClipboard(suggestion);

      if (result.success) {
        btn.innerHTML = `
          <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M5 13l4 4L19 7"/>
          </svg>
        `;
        setTimeout(() => {
          btn.innerHTML = `
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="9" y="9" width="13" height="13" rx="2"/>
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
            </svg>
          `;
        }, 2000);
      } else {
        showToast('复制失败，请手动复制', 'warning');
      }
    });
  });
}

async function handleCopy(data) {
  const { pr_info, summary, risks, processing_time } = data;
  const report = `# ${pr_info.title}
By ${pr_info.author}
${pr_info.files_count} file${pr_info.files_count !== 1 ? 's' : ''} • +${pr_info.additions} • -${pr_info.deletions}

## Summary
${summary}

## Risk Assessment (${risks.length})
${risks.map(risk => `- ${risk.level.toUpperCase()}: [${risk.type}] ${risk.file}:${risk.line}
  ${risk.description}
  Suggestion: ${risk.suggestion}`).join('\n\n')}

---
Processed in ${processing_time}s
`;
  
  const result = await copyToClipboard(report);
  
  if (result.success) {
    const copyBtn = document.getElementById('copy-btn');
    copyBtn.innerHTML = `
      <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M5 13l4 4L19 7"/>
      </svg>
      <span class="text-emerald-600">Copied</span>
    `;
    setTimeout(() => {
      copyBtn.innerHTML = `
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="9" y="9" width="13" height="13" rx="2"/>
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
        </svg>
        <span>Copy report</span>
      `;
    }, 2000);
  } else {
    showToast('复制失败，请手动复制', 'warning');
  }
}

init();
