// ==================== Global Variables ====================
const API_BASE = 'http://localhost:5000/api';
let chatHistory = [];

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    loadApiConfig();
    checkDatabaseStatus();
    setupDragAndDrop();
});

// ==================== API Configuration ====================
async function loadApiConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success) {
            const apiType = data.api_type.toUpperCase();
            document.getElementById('apiType').textContent = `${apiType} API`;
        }
    } catch (error) {
        console.error('Error loading config:', error);
        document.getElementById('apiType').textContent = 'API Error';
    }
}

// ==================== Database Status ====================
async function checkDatabaseStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.success && data.database_exists) {
            showDocumentInfo(data);
            showChatSection();
        } else {
            showUploadSection();
        }
    } catch (error) {
        console.error('Error checking status:', error);
        showNotification('Error checking database status', 'error');
    }
}

// ==================== Drag and Drop ====================
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        }, false);
    });
    
    uploadArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, false);
}

// ==================== File Handling ====================
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

async function handleFile(file) {
    // Validate file type
    if (file.type !== 'application/pdf') {
        showNotification('Please upload a PDF file', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('File size must be less than 16MB', 'error');
        return;
    }
    
    // Show progress
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    uploadProgress.classList.remove('hidden');
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';
    
    // Simulate upload progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
        }
    }, 200);
    
    // Upload file
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        
        if (data.success) {
            progressText.textContent = 'Processing complete!';
            
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
                showDocumentInfo({
                    total_chunks: data.total_chunks,
                    total_pages: data.total_pages
                });
                showChatSection();
                showNotification('PDF processed successfully!', 'success');
            }, 1000);
        } else {
            progressText.textContent = 'Error: ' + data.error;
            showNotification('Error processing PDF: ' + data.error, 'error');
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
            }, 3000);
        }
    } catch (error) {
        clearInterval(progressInterval);
        progressText.textContent = 'Upload failed';
        showNotification('Error uploading file: ' + error.message, 'error');
        setTimeout(() => {
            uploadProgress.classList.add('hidden');
        }, 3000);
    }
}

// ==================== UI Management ====================
function showDocumentInfo(data) {
    const documentInfo = document.getElementById('documentInfo');
    const documentStats = document.getElementById('documentStats');
    
    documentStats.textContent = `${data.total_chunks} chunks • ${data.total_pages} pages`;
    documentInfo.classList.remove('hidden');
}

function showUploadSection() {
    document.getElementById('uploadSection').classList.remove('hidden');
    document.getElementById('chatSection').classList.add('hidden');
    document.getElementById('featuresSection').classList.remove('hidden');
}

function showChatSection() {
    document.getElementById('chatSection').classList.remove('hidden');
    document.getElementById('featuresSection').classList.add('hidden');
}

function toggleUploadSection() {
    const uploadSection = document.getElementById('uploadSection');
    if (uploadSection.classList.contains('hidden')) {
        uploadSection.classList.remove('hidden');
    } else {
        uploadSection.classList.add('hidden');
    }
}

// ==================== Chat Functions ====================
function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
}

async function askQuestion() {
    const input = document.getElementById('questionInput');
    const question = input.value.trim();
    
    if (!question) {
        showNotification('Please enter a question', 'warning');
        return;
    }
    
    // Disable input
    const sendButton = document.getElementById('sendButton');
    input.disabled = true;
    sendButton.disabled = true;
    
    // Add user message to chat
    addMessage(question, 'user');
    input.value = '';
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(`${API_BASE}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        if (data.success) {
            addMessage(data.answer, 'bot', data.relevant_chunks);
        } else {
            addMessage('Sorry, I encountered an error: ' + data.error, 'bot');
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessage('Sorry, I encountered a network error. Please try again.', 'bot');
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        // Re-enable input
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
    }
}

function addMessage(content, type, chunks = null) {
    const messagesContainer = document.getElementById('chatMessages');
    
    // Remove welcome message if exists
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageParagraph = document.createElement('p');
    messageParagraph.textContent = content;
    messageContent.appendChild(messageParagraph);
    
    // Add relevant chunks for bot messages
    if (type === 'bot' && chunks && chunks.length > 0) {
        const chunksDiv = document.createElement('div');
        chunksDiv.className = 'relevant-chunks';
        
        const chunksTitle = document.createElement('h5');
        chunksTitle.textContent = 'Relevant Sections:';
        chunksDiv.appendChild(chunksTitle);
        
        chunks.forEach(chunk => {
            const chunkDiv = document.createElement('div');
            chunkDiv.className = 'chunk';
            chunkDiv.textContent = `📄 Page ${chunk.page} (Score: ${chunk.score.toFixed(2)}): ${chunk.text}`;
            chunksDiv.appendChild(chunkDiv);
        });
        
        messageContent.appendChild(chunksDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Store in history
    chatHistory.push({ type, content, chunks, timestamp: new Date() });
}

function addLoadingMessage() {
    const messagesContainer = document.getElementById('chatMessages');
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.id = 'loading-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = '<p>🤔 Thinking...</p>';
    
    loadingDiv.appendChild(avatar);
    loadingDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return 'loading-message';
}

function removeLoadingMessage(loadingId) {
    const loadingMessage = document.getElementById(loadingId);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// ==================== Database Management ====================
async function clearDatabase() {
    if (!confirm('Are you sure you want to clear the database? This will delete all processed data.')) {
        return;
    }
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.remove('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Database cleared successfully', 'success');
            
            // Reset UI
            document.getElementById('documentInfo').classList.add('hidden');
            document.getElementById('chatMessages').innerHTML = `
                <div class="welcome-message">
                    <i class="fas fa-robot"></i>
                    <p>Hello! I'm ready to answer questions about your document. What would you like to know?</p>
                </div>
            `;
            chatHistory = [];
            showUploadSection();
        } else {
            showNotification('Error clearing database: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        loadingOverlay.classList.add('hidden');
    }
}

// ==================== Notifications ====================
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? 'rgba(16, 185, 129, 0.9)' : 
                     type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 
                     type === 'warning' ? 'rgba(245, 158, 11, 0.9)' : 
                     'rgba(99, 102, 241, 0.9)'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    
    const icon = type === 'success' ? '✓' : 
                 type === 'error' ? '✕' : 
                 type === 'warning' ? '⚠' : 'ℹ';
    
    notification.innerHTML = `<strong>${icon}</strong> ${message}`;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// Add animation styles dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
