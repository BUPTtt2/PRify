import { checkHealth, submitReview } from './api.js';

const healthStatusEl = document.getElementById('health-status');
const reviewForm = document.getElementById('review-form');
const prUrlInput = document.getElementById('pr-url');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingSection = document.getElementById('loading-section');
const resultSection = document.getElementById('result-section');

async function init() {
  await checkHealthStatus();
  setupEventListeners();
}

async function checkHealthStatus() {
  try {
    const response = await checkHealth();
    if (response.status === 'ok') {
      healthStatusEl.innerHTML = `
        <div class="health-indicator">
          <div class="health-dot healthy"></div>
          <span class="text-stone-600">Online</span>
        </div>
      `;
    }
  } catch (error) {
    healthStatusEl.innerHTML = `
      <div class="health-indicator">
        <div class="health-dot unhealthy"></div>
        <span class="text-stone-500">Offline</span>
      </div>
    `;
  }
}

function setupEventListeners() {
  reviewForm.addEventListener('submit', handleSubmit);
}

async function handleSubmit(e) {
  e.preventDefault();
  
  const url = prUrlInput.value.trim();
  if (!url) {
    showSimpleAlert('Please provide a GitHub PR URL');
    return;
  }

  showLoading(true);

  try {
    const response = await submitReview(url);
    
    if (response.success) {
      renderResult(response.data);
    } else {
      showSimpleAlert('Analysis failed: ' + (response.error || 'Unknown error'));
    }
  } catch (error) {
    console.error(error);
    showSimpleAlert('Something went wrong. Please try again.');
  } finally {
    showLoading(false);
  }
}

function showLoading(isLoading) {
  if (isLoading) {
    loadingSection.classList.remove('hidden');
    loadingSection.classList.add('fade-in');
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

function showSimpleAlert(message) {
  alert(message);
}

function renderResult(data) {
  const { pr_info, summary, risks, total_files, processing_time } = data;
  
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
              <span>${pr_info.files_count} file${pr_info.files_count !== 1 ? 's' : ''}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 14l4-4 6 6 4-4"/>
              </svg>
              <span>${pr_info.additions}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4 text-rose-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M5 10l4 4 6-6 4 4"/>
              </svg>
              <span>${pr_info.deletions}</span>
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
          
          <div class="space-y-4">
            ${risks.map(risk => `
              <div class="risk-card rounded-lg border p-6 ${
                risk.level === 'high' 
                  ? 'border-rose-200 bg-rose-50/50' 
                  : risk.level === 'medium' 
                    ? 'border-amber-200 bg-amber-50/50' 
                    : 'border-sky-200 bg-sky-50/50'
              }">
                <div class="flex items-start justify-between mb-4">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                    risk.level === 'high' 
                      ? 'bg-rose-100 text-rose-700' 
                      : risk.level === 'medium' 
                        ? 'bg-amber-100 text-amber-700' 
                        : 'bg-sky-100 text-sky-700'
                  }">
                    ${risk.level.charAt(0).toUpperCase() + risk.level.slice(1)}
                  </span>
                  <span class="text-xs text-stone-500 font-mono">${risk.file}:${risk.line}</span>
                </div>
                
                <div class="space-y-3">
                  <div>
                    <p class="text-xs font-medium text-stone-400 uppercase tracking-wider mb-1.5">Type</p>
                    <p class="text-stone-700">${risk.type}</p>
                  </div>
                  <div>
                    <p class="text-xs font-medium text-stone-400 uppercase tracking-wider mb-1.5">Issue</p>
                    <p class="text-stone-700">${risk.description}</p>
                  </div>
                  <div>
                    <p class="text-xs font-medium text-stone-400 uppercase tracking-wider mb-1.5">Suggestion</p>
                    <p class="text-stone-700">${risk.suggestion}</p>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
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
  
  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => handleCopy(data));
  }
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
  
  const success = await navigator.clipboard.writeText(report);
  if (success) {
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
  }
}

init();
