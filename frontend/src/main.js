// PlagiSense Frontend Application Logic

const API_BASE_URL = 'http://127.0.0.1:8000';

let sourceFile = null;
let submissionFile = null;

// DOM Elements
const backendStatusEl = document.getElementById('backendStatus');
const sourceFileInput = document.getElementById('sourceFileInput');
const subFileInput = document.getElementById('subFileInput');
const sourceDropArea = document.getElementById('sourceDropArea');
const subDropArea = document.getElementById('subDropArea');
const sourceEmpty = document.getElementById('sourceEmpty');
const subEmpty = document.getElementById('subEmpty');
const sourcePreview = document.getElementById('sourcePreview');
const subPreview = document.getElementById('subPreview');
const sourceFileName = document.getElementById('sourceFileName');
const subFileName = document.getElementById('subFileName');
const sourceFileSize = document.getElementById('sourceFileSize');
const subFileSize = document.getElementById('subFileSize');
const sourceRemoveBtn = document.getElementById('sourceRemoveBtn');
const subRemoveBtn = document.getElementById('subRemoveBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeSpinner = document.getElementById('analyzeSpinner');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const resultsTimestamp = document.getElementById('resultsTimestamp');

// Metric Elements
const riskLevelBadge = document.getElementById('riskLevelBadge');
const overallScoreVal = document.getElementById('overallScoreVal');
const overallScoreFill = document.getElementById('overallScoreFill');
const overallScoreDesc = document.getElementById('overallScoreDesc');
const semanticScoreVal = document.getElementById('semanticScoreVal');
const semanticBarFill = document.getElementById('semanticBarFill');
const lexicalScoreVal = document.getElementById('lexicalScoreVal');
const lexicalBarFill = document.getElementById('lexicalBarFill');
const conceptScoreVal = document.getElementById('conceptScoreVal');
const conceptBarFill = document.getElementById('conceptBarFill');
const matchesCount = document.getElementById('matchesCount');
const matchesList = document.getElementById('matchesList');

// Quick Demo Buttons
const demoParaphraseBtn = document.getElementById('demoParaphraseBtn');
const demoExactBtn = document.getElementById('demoExactBtn');
const demoUnrelatedBtn = document.getElementById('demoUnrelatedBtn');

// Helper: Format file size
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Health check to verify backend connection
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      backendStatusEl.innerHTML = `
        <span class="status-dot online"></span>
        <span class="status-label">${data.service || 'Backend Connected'}</span>
      `;
    } else {
      throw new Error('Health check non-200');
    }
  } catch (err) {
    backendStatusEl.innerHTML = `
      <span class="status-dot offline"></span>
      <span class="status-label">Backend Offline (:8000)</span>
    `;
  }
}

// File state updates
function updateSourceFile(file) {
  sourceFile = file;
  if (file) {
    sourceFileName.textContent = file.name;
    sourceFileSize.textContent = formatBytes(file.size);
    sourceEmpty.classList.add('hidden');
    sourcePreview.classList.remove('hidden');
  } else {
    sourceFileInput.value = '';
    sourceEmpty.classList.remove('hidden');
    sourcePreview.classList.add('hidden');
  }
  updateAnalyzeButtonState();
}

function updateSubFile(file) {
  submissionFile = file;
  if (file) {
    subFileName.textContent = file.name;
    subFileSize.textContent = formatBytes(file.size);
    subEmpty.classList.add('hidden');
    subPreview.classList.remove('hidden');
  } else {
    subFileInput.value = '';
    subEmpty.classList.remove('hidden');
    subPreview.classList.add('hidden');
  }
  updateAnalyzeButtonState();
}

function updateAnalyzeButtonState() {
  analyzeBtn.disabled = !(sourceFile && submissionFile);
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorAlert.classList.remove('hidden');
}

function hideError() {
  errorAlert.classList.add('hidden');
}

// Event Listeners for File Input & Drag and Drop
sourceFileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files[0]) {
    updateSourceFile(e.target.files[0]);
    hideError();
  }
});

subFileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files[0]) {
    updateSubFile(e.target.files[0]);
    hideError();
  }
});

sourceRemoveBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  updateSourceFile(null);
});

subRemoveBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  updateSubFile(null);
});

// Drag & Drop Styling
[sourceDropArea, subDropArea].forEach((area) => {
  ['dragenter', 'dragover'].forEach((eventName) => {
    area.addEventListener(eventName, (e) => {
      e.preventDefault();
      area.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach((eventName) => {
    area.addEventListener(eventName, (e) => {
      e.preventDefault();
      area.classList.remove('dragover');
    });
  });
});

sourceDropArea.addEventListener('drop', (e) => {
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    updateSourceFile(e.dataTransfer.files[0]);
    hideError();
  }
});

subDropArea.addEventListener('drop', (e) => {
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    updateSubFile(e.dataTransfer.files[0]);
    hideError();
  }
});

// Create File Helper for Demo Samples
function createMockFile(filename, text) {
  const blob = new Blob([text], { type: 'text/plain' });
  return new File([blob], filename, { type: 'text/plain' });
}

// Sample Scenario Presets
demoParaphraseBtn.addEventListener('click', () => {
  const src = "Regular exercise improves cardiovascular health. It can reduce the risk of chronic disease. Physical activity may also improve concentration.";
  const sub = "Frequent workouts help maintain a healthy heart. Staying active can lower the chance of long-term illness. Students who remain physically active may concentrate better.";
  updateSourceFile(createMockFile('source_health_study.txt', src));
  updateSubFile(createMockFile('submission_student_essay.txt', sub));
  hideError();
});

demoExactBtn.addEventListener('click', () => {
  const text = "Machine learning algorithms build a mathematical model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed.";
  updateSourceFile(createMockFile('source_textbook.txt', text));
  updateSubFile(createMockFile('submission_homework.txt', text));
  hideError();
});

demoUnrelatedBtn.addEventListener('click', () => {
  const src = "Regular exercise improves cardiovascular health and enhances metabolic longevity.";
  const sub = "The university library opens daily at eight in the morning and closes at ten in the evening.";
  updateSourceFile(createMockFile('source_biology.txt', src));
  updateSubFile(createMockFile('submission_campus_guide.txt', sub));
  hideError();
});

// Run Plagiarism Analysis Action
analyzeBtn.addEventListener('click', async () => {
  if (!sourceFile || !submissionFile) return;

  hideError();
  analyzeBtn.disabled = true;
  analyzeSpinner.classList.remove('hidden');

  const formData = new FormData();
  formData.append('source_file', sourceFile);
  formData.append('submission_file', submissionFile);

  try {
    const res = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Analysis request failed');
    }

    renderAnalysisResults(data);
  } catch (err) {
    showError(err.message || 'An unexpected error occurred while analyzing documents.');
  } finally {
    analyzeBtn.disabled = false;
    analyzeSpinner.classList.add('hidden');
  }
});

// Render Results Function
function renderAnalysisResults(data) {
  // Support both unified top-level and nested structure
  const overall = data.overall || {};
  const score = (typeof data.overall_score === 'number' ? data.overall_score : overall.risk_score) || 0.0;
  const riskLevel = data.overall_risk || overall.risk_level || 'LOW';
  const semantic = (typeof data.semantic_similarity === 'number' ? data.semantic_similarity : overall.semantic_similarity) || 0.0;
  const lexical = (typeof data.lexical_similarity === 'number' ? data.lexical_similarity : overall.lexical_similarity) || 0.0;
  const concept = (typeof data.concept_overlap === 'number' ? data.concept_overlap : overall.concept_overlap) || 0.0;
  const matches = data.matches || [];

  // 1. Overall Risk Card
  const pct = Math.round(score * 100);
  overallScoreVal.textContent = `${pct}%`;
  overallScoreFill.style.width = `${pct}%`;
  riskLevelBadge.textContent = riskLevel;
  riskLevelBadge.className = `risk-badge ${riskLevel}`;

  if (riskLevel === 'HIGH') {
    overallScoreDesc.textContent = 'High probability of significant plagiarism or close paraphrasing.';
  } else if (riskLevel === 'MEDIUM') {
    overallScoreDesc.textContent = 'Moderate similarity detected. Review matches for proper attribution.';
  } else {
    overallScoreDesc.textContent = 'Low overall similarity. Original content detected.';
  }

  // 2. Multi-Signal Score Breakdown
  semanticScoreVal.textContent = semantic.toFixed(3);
  semanticBarFill.style.width = `${Math.round(semantic * 100)}%`;

  lexicalScoreVal.textContent = lexical.toFixed(3);
  lexicalBarFill.style.width = `${Math.round(lexical * 100)}%`;

  conceptScoreVal.textContent = concept.toFixed(3);
  conceptBarFill.style.width = `${Math.round(concept * 100)}%`;

  // 3. Render Passage Matches
  matchesCount.textContent = matches.length;
  matchesList.innerHTML = '';

  if (matches.length === 0) {
    matchesList.innerHTML = `
      <div class="no-matches-box">
        <p class="no-matches-title">No Suspicious Passages Found</p>
        <p>The submission shows high originality with no passages exceeding the semantic threshold.</p>
      </div>
    `;
  } else {
    matches.forEach((m, idx) => {
      const catClass = (m.category || '').replace(/[^a-zA-Z0-9]/g, '_');
      const evidenceTags = (m.evidence || []).map(e => `<span class="evidence-pill">${e}</span>`).join('');
      
      const itemEl = document.createElement('div');
      itemEl.className = 'match-item';
      itemEl.innerHTML = `
        <div class="match-item-header">
          <span class="category-tag ${catClass}">${m.category || 'MATCH'}</span>
          <div class="match-scores-summary">
            <span class="match-score-item">Risk: <span>${Math.round((m.risk_score || 0) * 100)}%</span></span>
            <span class="match-score-item">Semantic: <span>${Math.round((m.semantic_similarity || 0) * 100)}%</span></span>
            <span class="match-score-item">Lexical: <span>${Math.round((m.lexical_similarity || 0) * 100)}%</span></span>
          </div>
        </div>

        <div class="passage-comparison-grid">
          <div class="passage-box">
            <span class="passage-label">Source Passage:</span>
            <p class="passage-text">"${m.source || ''}"</p>
          </div>
          <div class="passage-box">
            <span class="passage-label">Submission Passage:</span>
            <p class="passage-text">"${m.submission || ''}"</p>
          </div>
        </div>

        ${evidenceTags ? `<div class="evidence-row">${evidenceTags}</div>` : ''}

        ${m.explanation ? `
          <div class="explanation-card">
            <strong>Evidence Explanation:</strong> ${m.explanation}
          </div>
        ` : ''}
      `;
      matchesList.appendChild(itemEl);
    });
  }

  // 4. Reveal Results
  resultsTimestamp.textContent = `Analyzed on ${new Date().toLocaleTimeString()}`;
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Initialize on page load
checkBackendHealth();
setInterval(checkBackendHealth, 5000);
