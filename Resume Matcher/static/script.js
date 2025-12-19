/**
 * Resume Matcher - Frontend JavaScript
 * Handles all UI interactions and API communications
 */

// API Base URL
const API_BASE = '';

// DOM Elements
const elements = {
    // Status
    apiStatus: document.getElementById('apiStatus'),
    
    // Resume Upload
    resumeDropZone: document.getElementById('resumeDropZone'),
    resumeInput: document.getElementById('resumeInput'),
    uploadedResumes: document.getElementById('uploadedResumes'),
    resumeCount: document.getElementById('resumeCount'),
    clearResumesBtn: document.getElementById('clearResumesBtn'),
    
    // Job Description
    jobDropZone: document.getElementById('jobDropZone'),
    jobInput: document.getElementById('jobInput'),
    jobTextInput: document.getElementById('jobTextInput'),
    submitJobTextBtn: document.getElementById('submitJobTextBtn'),
    jobStatus: document.getElementById('jobStatus'),
    clearJobBtn: document.getElementById('clearJobBtn'),
    
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Requirements
    requirementsSection: document.getElementById('requirementsSection'),
    requirementsGrid: document.getElementById('requirementsGrid'),
    
    // Match
    matchBtn: document.getElementById('matchBtn'),
    
    // Results
    resultsSection: document.getElementById('resultsSection'),
    summaryCards: document.getElementById('summaryCards'),
    resultsBody: document.getElementById('resultsBody'),
    exportCsvBtn: document.getElementById('exportCsvBtn'),
    exportJsonBtn: document.getElementById('exportJsonBtn'),
    
    // Modal
    detailModal: document.getElementById('detailModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalBody: document.getElementById('modalBody'),
    modalClose: document.getElementById('modalClose'),
    
    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// State
let state = {
    resumes: [],
    jobLoaded: false,
    jobRequirements: null,
    matchResults: null
};

// ========================================
// Initialization
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await checkApiStatus();
    setupEventListeners();
    await loadStatus();
}

// ========================================
// API Status
// ========================================

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const data = await response.json();
        
        if (data.success) {
            updateStatusIndicator('connected', `${data.api_type.toUpperCase()} Connected`);
        } else {
            updateStatusIndicator('error', 'API Error');
        }
    } catch (error) {
        updateStatusIndicator('error', 'Connection Failed');
        console.error('API check failed:', error);
    }
}

function updateStatusIndicator(status, text) {
    const dot = elements.apiStatus.querySelector('.status-dot');
    const textEl = elements.apiStatus.querySelector('.status-text');
    
    dot.className = 'status-dot ' + status;
    textEl.textContent = text;
}

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success) {
            if (data.resumes_loaded > 0) {
                updateResumeCount(data.resumes_loaded);
            }
            updateMatchButton();
        }
    } catch (error) {
        console.error('Status check failed:', error);
    }
}

// ========================================
// Event Listeners
// ========================================

function setupEventListeners() {
    // Resume Drop Zone
    setupDropZone(elements.resumeDropZone, elements.resumeInput, handleResumeFiles);
    
    // Job Drop Zone
    setupDropZone(elements.jobDropZone, elements.jobInput, handleJobFile);
    
    // Job Text Submit
    elements.submitJobTextBtn.addEventListener('click', submitJobText);
    
    // Tab Switching
    elements.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Clear Buttons
    elements.clearResumesBtn.addEventListener('click', clearResumes);
    elements.clearJobBtn.addEventListener('click', clearJob);
    
    // Match Button
    elements.matchBtn.addEventListener('click', runMatching);
    
    // Export Buttons
    elements.exportCsvBtn.addEventListener('click', () => exportResults('csv'));
    elements.exportJsonBtn.addEventListener('click', () => exportResults('json'));
    
    // Modal
    elements.modalClose.addEventListener('click', closeModal);
    elements.detailModal.querySelector('.modal-backdrop').addEventListener('click', closeModal);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// ========================================
// Drop Zone Setup
// ========================================

function setupDropZone(dropZone, input, handler) {
    // Click to open file dialog
    dropZone.addEventListener('click', () => input.click());
    
    // File input change
    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handler(e.target.files);
        }
    });
    
    // Drag events
    ['dragenter', 'dragover'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });
    
    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });
    
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handler(files);
        }
    });
}

// ========================================
// Resume Upload
// ========================================

async function handleResumeFiles(files) {
    const formData = new FormData();
    
    for (let file of files) {
        if (file.type === 'application/pdf') {
            formData.append('files', file);
        } else {
            showToast(`${file.name} is not a PDF file`, 'error');
        }
    }
    
    if (!formData.has('files')) {
        return;
    }
    
    try {
        showToast('Uploading resumes...', 'info');
        
        const response = await fetch(`${API_BASE}/api/upload/resume`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Uploaded ${data.results.length} resume(s)`, 'success');
            updateResumeList(data.results);
            updateResumeCount(data.total_resumes);
            updateMatchButton();
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
        console.error('Resume upload error:', error);
    }
}

function updateResumeList(results) {
    results.forEach(result => {
        if (result.success) {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span class="filename">${result.filename}</span>
                <span class="file-status">Ready</span>
            `;
            elements.uploadedResumes.appendChild(item);
            state.resumes.push(result.filename);
        }
    });
}

function updateResumeCount(count) {
    elements.resumeCount.textContent = `${count} resume${count !== 1 ? 's' : ''}`;
    elements.clearResumesBtn.disabled = count === 0;
}

async function clearResumes() {
    try {
        const response = await fetch(`${API_BASE}/api/resumes/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            elements.uploadedResumes.innerHTML = '';
            state.resumes = [];
            updateResumeCount(0);
            updateMatchButton();
            hideResults();
            showToast('Resumes cleared', 'success');
        }
    } catch (error) {
        showToast('Failed to clear resumes', 'error');
    }
}

// ========================================
// Job Description
// ========================================

function switchTab(tab) {
    elements.tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    
    document.getElementById('textTab').classList.toggle('active', tab === 'text');
    document.getElementById('fileTab').classList.toggle('active', tab === 'file');
}

async function handleJobFile(files) {
    const file = files[0];
    
    if (file.type !== 'application/pdf') {
        showToast('Please upload a PDF file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showToast('Processing job description...', 'info');
        
        const response = await fetch(`${API_BASE}/api/upload/job`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job description processed', 'success');
            handleJobSuccess(data);
        } else {
            showToast(data.error || 'Processing failed', 'error');
        }
    } catch (error) {
        showToast('Processing failed: ' + error.message, 'error');
        console.error('Job upload error:', error);
    }
}

async function submitJobText() {
    const text = elements.jobTextInput.value.trim();
    
    if (!text) {
        showToast('Please enter a job description', 'error');
        return;
    }
    
    try {
        showToast('Processing job description...', 'info');
        
        const response = await fetch(`${API_BASE}/api/job/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Job description processed', 'success');
            handleJobSuccess(data);
        } else {
            showToast(data.error || 'Processing failed', 'error');
        }
    } catch (error) {
        showToast('Processing failed: ' + error.message, 'error');
        console.error('Job text error:', error);
    }
}

function handleJobSuccess(data) {
    state.jobLoaded = true;
    state.jobRequirements = data.requirements;
    
    // Update job status
    elements.jobStatus.innerHTML = `
        <div class="job-status-card">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            <div class="status-info">
                <div class="status-title">Job Description Loaded</div>
                <div class="status-meta">${data.char_count.toLocaleString()} characters analyzed</div>
            </div>
        </div>
    `;
    
    // Show requirements
    displayRequirements(data.requirements);
    updateMatchButton();
}

function displayRequirements(requirements) {
    elements.requirementsSection.classList.remove('hidden');
    
    let html = '';
    
    // Required Skills
    if (requirements.required_skills && requirements.required_skills.length > 0) {
        html += `
            <div class="requirement-card">
                <h4>Required Skills</h4>
                <div class="skill-tags">
                    ${requirements.required_skills.map(s => 
                        `<span class="skill-tag required">${s}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    // Preferred Skills
    if (requirements.preferred_skills && requirements.preferred_skills.length > 0) {
        html += `
            <div class="requirement-card">
                <h4>Preferred Skills</h4>
                <div class="skill-tags">
                    ${requirements.preferred_skills.map(s => 
                        `<span class="skill-tag preferred">${s}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    // Experience & Education
    html += `
        <div class="requirement-card">
            <h4>Other Requirements</h4>
            <div class="skill-tags">
                <span class="skill-tag">📅 ${requirements.experience_years || 'Not specified'}</span>
                <span class="skill-tag">🎓 ${requirements.education || 'Not specified'}</span>
            </div>
        </div>
    `;
    
    elements.requirementsGrid.innerHTML = html;
}

async function clearJob() {
    try {
        const response = await fetch(`${API_BASE}/api/job/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.jobLoaded = false;
            state.jobRequirements = null;
            elements.jobStatus.innerHTML = '';
            elements.jobTextInput.value = '';
            elements.requirementsSection.classList.add('hidden');
            updateMatchButton();
            hideResults();
            showToast('Job description cleared', 'success');
        }
    } catch (error) {
        showToast('Failed to clear job', 'error');
    }
}

// ========================================
// Matching
// ========================================

function updateMatchButton() {
    const hasResumes = state.resumes.length > 0;
    const hasJob = state.jobLoaded;
    
    elements.matchBtn.disabled = !(hasResumes && hasJob);
}

async function runMatching() {
    const btnContent = elements.matchBtn.querySelector('.btn-content');
    const btnLoader = elements.matchBtn.querySelector('.btn-loader');
    
    // Show loading state
    btnContent.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    elements.matchBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/match`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.matchResults = data.results;
            displayResults(data.results, data.summary);
            showToast('Matching complete!', 'success');
        } else {
            showToast(data.error || 'Matching failed', 'error');
        }
    } catch (error) {
        showToast('Matching failed: ' + error.message, 'error');
        console.error('Matching error:', error);
    } finally {
        // Hide loading state
        btnContent.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        elements.matchBtn.disabled = false;
    }
}

// ========================================
// Results Display
// ========================================

function displayResults(results, summary) {
    elements.resultsSection.classList.remove('hidden');
    
    // Display summary
    displaySummary(summary);
    
    // Display results table
    displayResultsTable(results);
    
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displaySummary(summary) {
    elements.summaryCards.innerHTML = `
        <div class="summary-card">
            <div class="value">${summary.total}</div>
            <div class="label">Total Candidates</div>
        </div>
        <div class="summary-card">
            <div class="value">${summary.average_score}%</div>
            <div class="label">Average Score</div>
        </div>
        <div class="summary-card">
            <div class="value">${summary.highest_score}%</div>
            <div class="label">Highest Score</div>
        </div>
        <div class="summary-card">
            <div class="value">${summary.above_80}</div>
            <div class="label">Strong Matches (80%+)</div>
        </div>
    `;
}

function displayResultsTable(results) {
    elements.resultsBody.innerHTML = results.map(result => {
        if (result.error) {
            return `
                <tr>
                    <td><span class="rank-badge rank-other">-</span></td>
                    <td class="candidate-name">${result.resume_filename}</td>
                    <td colspan="4" style="color: var(--error);">Error: ${result.error}</td>
                </tr>
            `;
        }
        
        const rankClass = result.rank <= 3 ? `rank-${result.rank}` : 'rank-other';
        const finalScoreClass = getScoreClass(result.final_score);
        const semanticScoreClass = getScoreClass(result.semantic_score);
        const skillScoreClass = getScoreClass(result.skill_score);
        
        return `
            <tr>
                <td><span class="rank-badge ${rankClass}">${result.rank}</span></td>
                <td class="candidate-name">
                    ${result.resume_filename}
                </td>
                <td>
                    <div class="score-display">
                        <span class="score-value">${result.final_score}%</span>
                        <div class="score-bar">
                            <div class="score-bar-fill ${finalScoreClass}" style="width: ${result.final_score}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="score-display">
                        <span class="score-value" style="font-size: 0.9rem;">${result.semantic_score}%</span>
                        <div class="score-bar">
                            <div class="score-bar-fill ${semanticScoreClass}" style="width: ${result.semantic_score}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="score-display">
                        <span class="score-value" style="font-size: 0.9rem;">${result.skill_score}%</span>
                        <div class="score-bar">
                            <div class="score-bar-fill ${skillScoreClass}" style="width: ${result.skill_score}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <button class="btn-details" onclick="showDetails(${results.indexOf(result)})">
                        View Details
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function getScoreClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function hideResults() {
    elements.resultsSection.classList.add('hidden');
    state.matchResults = null;
}

// ========================================
// Details Modal
// ========================================

function showDetails(index) {
    const result = state.matchResults[index];
    
    if (!result) return;
    
    elements.modalTitle.textContent = result.resume_filename;
    
    const skillDetails = result.skill_details || {};
    
    elements.modalBody.innerHTML = `
        <div class="detail-section">
            <h4>Score Breakdown</h4>
            <div class="score-breakdown">
                <div class="score-item">
                    <div class="value">${result.final_score}%</div>
                    <div class="label">Final Score</div>
                </div>
                <div class="score-item">
                    <div class="value">${result.semantic_score}%</div>
                    <div class="label">Semantic Match</div>
                </div>
                <div class="score-item">
                    <div class="value">${result.skill_score}%</div>
                    <div class="label">Skill Match</div>
                </div>
            </div>
        </div>
        
        ${skillDetails.required_matches && skillDetails.required_matches.length > 0 ? `
            <div class="detail-section">
                <h4>✅ Matched Required Skills (${skillDetails.required_matches.length}/${skillDetails.total_required || 0})</h4>
                <div class="skills-list">
                    ${skillDetails.required_matches.map(s => 
                        `<span class="skill-tag skill-matched">${s}</span>`
                    ).join('')}
                </div>
            </div>
        ` : ''}
        
        ${skillDetails.required_missing && skillDetails.required_missing.length > 0 ? `
            <div class="detail-section">
                <h4>❌ Missing Required Skills</h4>
                <div class="skills-list">
                    ${skillDetails.required_missing.map(s => 
                        `<span class="skill-tag skill-missing">${s}</span>`
                    ).join('')}
                </div>
            </div>
        ` : ''}
        
        ${skillDetails.preferred_matches && skillDetails.preferred_matches.length > 0 ? `
            <div class="detail-section">
                <h4>⭐ Matched Preferred Skills</h4>
                <div class="skills-list">
                    ${skillDetails.preferred_matches.map(s => 
                        `<span class="skill-tag skill-matched">${s}</span>`
                    ).join('')}
                </div>
            </div>
        ` : ''}
        
        ${skillDetails.extracted_skills ? `
            <div class="detail-section">
                <h4>📋 All Extracted Skills</h4>
                <div class="skills-list">
                    ${getAllSkillTags(skillDetails.extracted_skills)}
                </div>
            </div>
        ` : ''}
    `;
    
    elements.detailModal.classList.remove('hidden');
}

function getAllSkillTags(skills) {
    const allSkills = [];
    
    ['technical_skills', 'soft_skills', 'tools', 'languages', 'frameworks', 'certifications'].forEach(category => {
        if (skills[category]) {
            skills[category].forEach(skill => {
                allSkills.push(`<span class="skill-tag">${skill}</span>`);
            });
        }
    });
    
    return allSkills.join('');
}

function closeModal() {
    elements.detailModal.classList.add('hidden');
}

// ========================================
// Export
// ========================================

function exportResults(format) {
    window.location.href = `${API_BASE}/api/results/export?format=${format}`;
    showToast(`Downloading ${format.toUpperCase()} file...`, 'success');
}

// ========================================
// Toast Notifications
// ========================================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' 
        ? '<polyline points="20 6 9 17 4 12"/>'
        : type === 'error'
        ? '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
        : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>';
    
    toast.innerHTML = `
        <svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${icon}
        </svg>
        <span class="toast-message">${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Make showDetails globally accessible
window.showDetails = showDetails;
