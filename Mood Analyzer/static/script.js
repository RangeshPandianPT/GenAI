/**
 * Mood Analyzer - Frontend JavaScript
 * Handles API communication, UI updates, history, and theme management
 */

// ===== DOM Elements =====
const textInput = document.getElementById('text-input');
const charCounter = document.getElementById('char-counter');
const wordCount = document.getElementById('word-count');
const sentenceCount = document.getElementById('sentence-count');
const analyzeBtn = document.getElementById('analyze-btn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnLoader = analyzeBtn.querySelector('.btn-loader');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');
const themeToggle = document.getElementById('theme-toggle');

// Result elements
const resultCard = document.getElementById('result-card');
const resultEmoji = document.getElementById('result-emoji');
const sentimentText = document.getElementById('sentiment-text');
const confidenceValue = document.getElementById('confidence-value');
const confidenceFill = document.getElementById('confidence-fill');
const scoresContainer = document.getElementById('scores-container');

// New feature elements
const copyResultBtn = document.getElementById('copy-result-btn');
const newAnalysisBtn = document.getElementById('new-analysis-btn');
const statsSection = document.getElementById('stats-section');
const historySection = document.getElementById('history-section');
const historyList = document.getElementById('history-list');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const sampleChips = document.querySelectorAll('.sample-chip');

// Stats elements
const totalAnalyses = document.getElementById('total-analyses');
const positiveCount = document.getElementById('positive-count');
const neutralCount = document.getElementById('neutral-count');
const negativeCount = document.getElementById('negative-count');

// API endpoint
const API_URL = '/analyze';

// Storage keys
const HISTORY_KEY = 'moodAnalyzerHistory';
const THEME_KEY = 'moodAnalyzerTheme';

// Current analysis data
let currentAnalysis = null;

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadHistory();
    updateStats();
    textInput.focus();
});

// ===== Theme Management =====
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeToggle(true);
    }
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
    updateThemeToggle(isDark);
}

function updateThemeToggle(isDark) {
    const icon = themeToggle.querySelector('.icon');
    const label = themeToggle.querySelector('.label');
    icon.textContent = isDark ? '☀️' : '🌙';
    label.textContent = isDark ? 'Light' : 'Dark';
}

themeToggle.addEventListener('click', toggleTheme);

// ===== Text Analytics =====
function updateTextAnalytics() {
    const text = textInput.value;
    
    // Character count
    charCounter.textContent = text.length;
    
    // Word count
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    wordCount.textContent = words.length;
    
    // Sentence count (rough estimate)
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    sentenceCount.textContent = sentences.length;
}

textInput.addEventListener('input', updateTextAnalytics);

// ===== Sample Texts =====
sampleChips.forEach(chip => {
    chip.addEventListener('click', () => {
        const sampleText = chip.dataset.text;
        textInput.value = sampleText;
        updateTextAnalytics();
        textInput.focus();
        
        // Add subtle animation
        chip.style.transform = 'scale(0.95)';
        setTimeout(() => {
            chip.style.transform = '';
        }, 150);
    });
});

// ===== Analyze Button =====
analyzeBtn.addEventListener('click', analyzeMood);

// Retry button
retryBtn.addEventListener('click', () => {
    hideError();
    analyzeMood();
});

// Enter key to submit (with Ctrl/Cmd)
textInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        analyzeMood();
    }
});

/**
 * Main function to analyze mood
 */
async function analyzeMood() {
    const text = textInput.value.trim();
    
    if (!text) {
        showError('Please enter some text to analyze');
        return;
    }
    
    // Show loading state
    setLoading(true);
    hideResults();
    hideError();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze text');
        }
        
        const data = await response.json();
        
        // Store current analysis
        currentAnalysis = {
            text: text,
            ...data,
            timestamp: new Date().toISOString()
        };
        
        // Save to history
        saveToHistory(currentAnalysis);
        
        // Display results
        displayResults(data);
        
        // Update stats and history display
        updateStats();
        displayHistory();
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Something went wrong. Please try again.');
    } finally {
        setLoading(false);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const { sentiment, confidence, emoji, scores } = data;
    
    // Update emoji
    resultEmoji.textContent = emoji;
    
    // Update sentiment label
    sentimentText.textContent = sentiment;
    
    // Update confidence
    confidenceValue.textContent = `${confidence}%`;
    confidenceFill.style.width = `${confidence}%`;
    
    // Set card theme based on sentiment
    resultCard.className = 'result-card';
    if (sentiment.includes('POSITIVE')) {
        resultCard.classList.add('positive');
    } else if (sentiment.includes('NEGATIVE')) {
        resultCard.classList.add('negative');
    } else {
        resultCard.classList.add('neutral');
    }
    
    // Generate score bars
    scoresContainer.innerHTML = '';
    for (const [label, score] of Object.entries(scores)) {
        const scoreItem = createScoreItem(label, score);
        scoresContainer.appendChild(scoreItem);
    }
    
    // Show results with animation
    resultsSection.classList.remove('hidden');
    
    // Animate score bars after a small delay
    setTimeout(() => {
        document.querySelectorAll('.score-bar').forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 100);
}

/**
 * Create a score item element
 */
function createScoreItem(label, score) {
    const item = document.createElement('div');
    item.className = 'score-item';
    
    const labelClass = label.toLowerCase().includes('positive') ? 'positive' : 
                       label.toLowerCase().includes('negative') ? 'negative' : 'neutral';
    
    item.innerHTML = `
        <span class="score-label">${label.toLowerCase()}</span>
        <div class="score-bar-container">
            <div class="score-bar ${labelClass}" style="width: 0%" data-width="${score}%"></div>
        </div>
        <span class="score-value">${score}%</span>
    `;
    
    return item;
}

// ===== History Management =====
function getHistory() {
    const historyData = localStorage.getItem(HISTORY_KEY);
    return historyData ? JSON.parse(historyData) : [];
}

function saveToHistory(analysis) {
    const history = getHistory();
    
    // Add to beginning of array
    history.unshift(analysis);
    
    // Keep only last 20 items
    if (history.length > 20) {
        history.pop();
    }
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    loadHistory();
    updateStats();
}

function loadHistory() {
    displayHistory();
}

function displayHistory() {
    const history = getHistory();
    
    if (history.length === 0) {
        historySection.classList.add('hidden');
        return;
    }
    
    historySection.classList.remove('hidden');
    historyList.innerHTML = '';
    
    history.slice(0, 10).forEach(item => {
        const historyItem = createHistoryItem(item);
        historyList.appendChild(historyItem);
    });
}

function createHistoryItem(item) {
    const div = document.createElement('div');
    div.className = 'history-item';
    
    const sentimentClass = item.sentiment.toLowerCase().includes('positive') ? 'positive' :
                           item.sentiment.toLowerCase().includes('negative') ? 'negative' : 'neutral';
    
    const timeAgo = getTimeAgo(new Date(item.timestamp));
    
    div.innerHTML = `
        <span class="history-emoji">${item.emoji}</span>
        <div class="history-content">
            <p class="history-text" title="${item.text}">${item.text}</p>
            <div class="history-meta">
                <span class="history-sentiment ${sentimentClass}">${item.sentiment}</span>
                <span class="history-time">${timeAgo}</span>
            </div>
        </div>
    `;
    
    // Click to re-analyze this text
    div.addEventListener('click', () => {
        textInput.value = item.text;
        updateTextAnalytics();
        textInput.focus();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    return div;
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
}

clearHistoryBtn.addEventListener('click', () => {
    if (confirm('Clear all history? This cannot be undone.')) {
        clearHistory();
    }
});

// ===== Statistics =====
function updateStats() {
    const history = getHistory();
    
    if (history.length === 0) {
        statsSection.classList.add('hidden');
        return;
    }
    
    statsSection.classList.remove('hidden');
    
    let positive = 0, neutral = 0, negative = 0;
    
    history.forEach(item => {
        const sentiment = item.sentiment.toLowerCase();
        if (sentiment.includes('positive')) positive++;
        else if (sentiment.includes('negative')) negative++;
        else neutral++;
    });
    
    totalAnalyses.textContent = `${history.length} ${history.length === 1 ? 'analysis' : 'analyses'}`;
    positiveCount.textContent = positive;
    neutralCount.textContent = neutral;
    negativeCount.textContent = negative;
}

// ===== Copy Result =====
copyResultBtn.addEventListener('click', async () => {
    if (!currentAnalysis) return;
    
    const resultText = `🎭 Mood Analysis Result
━━━━━━━━━━━━━━━━━━━━━━
📝 Text: "${currentAnalysis.text.substring(0, 100)}${currentAnalysis.text.length > 100 ? '...' : ''}"
${currentAnalysis.emoji} Sentiment: ${currentAnalysis.sentiment}
📊 Confidence: ${currentAnalysis.confidence}%
━━━━━━━━━━━━━━━━━━━━━━
Analyzed with Mood Analyzer 🎭`;
    
    try {
        await navigator.clipboard.writeText(resultText);
        copyResultBtn.classList.add('copied');
        copyResultBtn.innerHTML = '<span>✓</span> Copied!';
        
        setTimeout(() => {
            copyResultBtn.classList.remove('copied');
            copyResultBtn.innerHTML = '<span>📋</span> Copy Result';
        }, 2000);
    } catch (err) {
        console.error('Copy failed:', err);
    }
});

// ===== New Analysis =====
newAnalysisBtn.addEventListener('click', () => {
    textInput.value = '';
    updateTextAnalytics();
    hideResults();
    textInput.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ===== UI Helper Functions =====
function setLoading(isLoading) {
    if (analyzeBtn) {
        analyzeBtn.disabled = isLoading;
        if (isLoading) {
            btnText.classList.add('hidden');
            btnLoader.classList.remove('hidden');
        } else {
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    // Also hide dashboard loading if it was active
    document.getElementById('dashboard-loading').classList.add('hidden');
}

function hideError() {
    errorSection.classList.add('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
}


// ===== DASHBOARD LOGIC (New) =====

// Tab Switching
const tabs = document.querySelectorAll('.nav-tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all
        tabs.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        
        // Add active to clicked
        tab.classList.add('active');
        document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
    });
});

// Dashboard Elements
const feedSearchInput = document.getElementById('feed-search-input');
const fetchFeedBtn = document.getElementById('fetch-feed-btn');
const dashboardLoading = document.getElementById('dashboard-loading');
const dashboardResults = document.getElementById('dashboard-results');
const globalMoodText = document.getElementById('global-mood-text');
const headlinesList = document.getElementById('headlines-list');
const moodChartCanvas = document.getElementById('moodChart');
let moodChartInstance = null;

fetchFeedBtn.addEventListener('click', fetchFeed);
feedSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') fetchFeed();
});

async function fetchFeed() {
    const query = feedSearchInput.value.trim();
    
    // UI State
    dashboardLoading.classList.remove('hidden');
    dashboardResults.classList.add('hidden');
    hideError();
    
    try {
        const response = await fetch('/analyze-feed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: query })
        });
        
        if (!response.ok) throw new Error("Failed to fetch news feed");
        
        const data = await response.json();
        renderDashboard(data);
        
    } catch (error) {
        console.error(error);
        showError(error.message || "Failed to load dashboard data");
    } finally {
        dashboardLoading.classList.add('hidden');
    }
}

function renderDashboard(data) {
    dashboardResults.classList.remove('hidden');
    
    // 1. Global Stats
    const { stats, headlines, query } = data;
    globalMoodText.textContent = `${stats.overall_mood} ${getMoodEmoji(stats.overall_mood)}`;
    
    document.getElementById('dash-pos-count').textContent = stats.positive;
    document.getElementById('dash-neu-count').textContent = stats.neutral;
    document.getElementById('dash-neg-count').textContent = stats.negative;
    
    // 2. Chart
    renderChart(stats);
    
    // 3. Headlines
    renderHeadlines(headlines);
}

function getMoodEmoji(mood) {
    if (mood === 'POSITIVE') return '😊';
    if (mood === 'NEGATIVE') return '😠';
    return '😐';
}

function renderChart(stats) {
    if (moodChartInstance) {
        moodChartInstance.destroy();
    }
    
    const ctx = moodChartCanvas.getContext('2d');
    moodChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [stats.positive, stats.neutral, stats.negative],
                backgroundColor: [
                    '#10b981', // Green
                    '#9ca3af', // Gray
                    '#ef4444'  // Red
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderHeadlines(headlines) {
    headlinesList.innerHTML = '';
    
    if (headlines.length === 0) {
        headlinesList.innerHTML = '<p class="text-center text-muted">No news found for this topic.</p>';
        return;
    }
    
    headlines.forEach(item => {
        const div = document.createElement('div');
        div.className = `headline-item ${item.sentiment.toLowerCase()}`;
        
        div.innerHTML = `
            <a href="#" target="_blank" class="headline-title">${item.emoji} ${item.title}</a>
            <div class="headline-meta">
                <span>Sentiment: ${item.sentiment} (${item.confidence}%)</span>
            </div>
        `;
        headlinesList.appendChild(div);
    });
}

