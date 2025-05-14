document.addEventListener('DOMContentLoaded', function() {
    const audioForm = document.getElementById('audioForm');
    const processButton = document.getElementById('processButton');
    const statusContainer = document.getElementById('statusContainer');
    const progressContainer = document.getElementById('progressContainer');
    const conversationContainer = document.getElementById('conversationContainer');
    const audioResponseContainer = document.getElementById('audioResponseContainer');
    const responseAudio = document.getElementById('responseAudio');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    
    // Error modal elements
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    const errorModalBody = document.getElementById('errorModalBody');

    // Handle form submission
    audioForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(audioForm);
        const audioFile = document.getElementById('audioFile').files[0];
        
        if (!audioFile) {
            showError('Please select an audio file.');
            return;
        }
        
        // Update UI to show processing
        processButton.disabled = true;
        processButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        statusContainer.innerHTML = '<p class="mb-1 processing">Processing audio file...</p>';
        progressContainer.style.display = 'block';
        
        // Send request to backend
        fetch('/process_audio', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Unknown error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            // Update conversation container
            updateConversation(data.conversation_history);
            
            // Set up audio response
            if (data.audio_path) {
                responseAudio.src = `/get_audio/${data.audio_path.split('/').pop()}`;
                audioResponseContainer.style.display = 'block';
                responseAudio.play();
            }
            
            // Reset UI
            resetUI();
        })
        .catch(error => {
            showError(error.message);
            resetUI();
        });
    });
    
    // Clear conversation history
    clearHistoryBtn.addEventListener('click', function() {
        fetch('/clear_history', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                conversationContainer.innerHTML = `
                    <div class="text-center text-muted py-5">
                        <i class="fas fa-comment-dots fa-3x mb-3"></i>
                        <p>No conversation yet. Upload an audio file to begin.</p>
                    </div>
                `;
                audioResponseContainer.style.display = 'none';
            }
        })
        .catch(error => {
            showError('Failed to clear history: ' + error.message);
        });
    });
    
    // Helper functions
    function updateConversation(history) {
        if (!history || history.length === 0) {
            return;
        }
        
        let html = '';
        history.forEach(message => {
            html += `
                <div class="message-container ${message.role === 'user' ? 'user-message' : 'assistant-message'}">
                    <div class="message-header">
                        <span class="message-role">${message.role.charAt(0).toUpperCase() + message.role.slice(1)}</span>
                        <span class="message-time">${message.timestamp || new Date().toTimeString().split(' ')[0]}</span>
                    </div>
                    <div class="message-content">${message.content}</div>
                </div>
            `;
        });
        
        conversationContainer.innerHTML = html;
        
        // Scroll to bottom of conversation
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
    
    function resetUI() {
        processButton.disabled = false;
        processButton.innerHTML = '<i class="fas fa-upload me-2"></i>Upload & Process';
        statusContainer.innerHTML = '<p class="mb-1">Ready for next input</p>';
        progressContainer.style.display = 'none';
        document.getElementById('audioFile').value = '';
    }
    
    function showError(message) {
        errorModalBody.textContent = message;
        errorModal.show();
    }
});
