let mediaRecorder;
let audioChunks = [];
const recordBtn = document.getElementById('record-btn');
const statusDiv = document.getElementById('status');
const chatBox = document.getElementById('chat-box');
let isRecording = false;

recordBtn.addEventListener('click', async () => {
    if (isRecording) {
        mediaRecorder.stop();
        recordBtn.textContent = 'Start Recording';
        recordBtn.classList.remove('recording');
        statusDiv.textContent = 'Processing...';
        isRecording = false;
    } else {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error("Server error");
                    }
                    
                    const data = await response.json();
                    
                    // Add to chat box
                    chatBox.innerHTML += `<div class="message user-msg"><strong>You</strong> ${data.user_text}</div>`;
                    chatBox.innerHTML += `<div class="message ai-msg"><strong>AI</strong> ${data.ai_text}</div>`;
                    
                    // Auto-scroll to bottom
                    chatBox.scrollTop = chatBox.scrollHeight;
                    
                    // Play audio
                    const audio = new Audio("data:audio/mp3;base64," + data.audio_b64);
                    audio.play();
                    statusDiv.textContent = 'Ready';
                    
                } catch (error) {
                    console.error(error);
                    statusDiv.textContent = 'Error occurred during processing.';
                }
            };
            
            mediaRecorder.start();
            recordBtn.textContent = 'Stop Recording';
            recordBtn.classList.add('recording');
            statusDiv.textContent = 'Recording...';
            isRecording = true;
        } catch (err) {
            console.error("Error accessing microphone:", err);
            statusDiv.textContent = 'Microphone access denied.';
        }
    }
});
