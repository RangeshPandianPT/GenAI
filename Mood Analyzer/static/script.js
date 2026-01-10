/**
 * Mood Analyzer - Frontend JavaScript
 * Handles API communication and dynamic UI updates
 */

// DOM Elements
const textInput = document.getElementById('text-input');
const charCounter = document.getElementById('char-counter');
const analyzeBtn = document.getElementById('analyze-btn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnLoader = analyzeBtn.querySelector('.btn-loader');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');

// Result elements
const resultCard = document.getElementById('result-card');
const resultEmoji = document.getElementById('result-emoji');
const sentimentText = document.getElementById('sentiment-text');
const confidenceValue = document.getElementById('confidence-value');
const confidenceFill = document.getElementById('confidence-fill');
const scoresContainer = document.getElementById('scores-container');

// API endpoint
const API_URL = '/analyze';

// Character counter
textInput.addEventListener('input', () => {
    charCounter.textContent = textInput.value.length;
});

// Analyze button click
analyzeBtn.addEventListener('click', analyzeMood);

// Retry button click
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
        displayResults(data);
        
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
    if (sentiment === 'POSITIVE') {
        resultCard.classList.add('positive');
    } else if (sentiment === 'NEGATIVE') {
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
    
    const labelClass = label.toLowerCase();
    
    item.innerHTML = `
        <span class="score-label">${label.toLowerCase()}</span>
        <div class="score-bar-container">
            <div class="score-bar ${labelClass}" style="width: 0%" data-width="${score}%"></div>
        </div>
        <span class="score-value">${score}%</span>
    `;
    
    return item;
}

/**
 * Set loading state
 */
function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    
    if (isLoading) {
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
}

/**
 * Hide error section
 */
function hideError() {
    errorSection.classList.add('hidden');
}

/**
 * Hide results section
 */
function hideResults() {
    resultsSection.classList.add('hidden');
}

// Initial focus on text input
textInput.focus();
