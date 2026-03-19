document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    const liveLogs = document.getElementById('live-logs');
    const languageSelect = document.getElementById('language-select');

    // Agent Node UI Elements
    const nodes = {
        'coordinator': document.getElementById('node-coordinator'),
        'query': document.getElementById('node-query'),
        'recommendation': document.getElementById('node-recommendation'),
        quiz: document.getElementById('node-quiz'),
        pdf: document.getElementById('node-pdf')
    };

    // Session ID representing current user session
    const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

    function addLog(message, isHighlight = false) {
        const p = document.createElement('p');
        p.className = 'log-entry' + (isHighlight ? ' highlight' : '');
        
        const time = new Date().toLocaleTimeString([], {hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit'});
        p.innerHTML = `<span class="timestamp">${time}:</span> ${message}`;
        
        liveLogs.appendChild(p);
        liveLogs.scrollTop = liveLogs.scrollHeight;
    }

    function appendMessage(role, text, agentName = null, isFile = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role === 'user' ? 'user-msg' : 'agent-msg'}`;

        let avatar = role === 'user' ? '👤' : '🤖';
        let author = role === 'user' ? 'You' : (agentName || 'System');

        // Choose avatar based on agent type
        if (role === 'agent' && agentName) {
            if (agentName.includes('Coordinator')) avatar = '🧠';
            else if (agentName.includes('Query')) avatar = '📚';
            else if (agentName.includes('Recommendation')) avatar = '🎯';
            else if (agentName.includes('Quiz')) avatar = '✏️';
            else if (agentName.includes('PDF') || agentName.includes('Summarizer')) avatar = '📑';
        }

        let htmlContent;
        if (isFile) {
            htmlContent = `
                <div class="file-card">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <div class="file-name">${text}</div>
                        <div class="file-type">PDF</div>
                    </div>
                </div>`;
        } else {
            htmlContent = role === 'user' ? `<p>${text}</p>` : marked.parse(text);
        }

        msgDiv.innerHTML = `<div class="msg-avatar">${avatar}</div><div class="msg-content"><strong>${author}</strong>${htmlContent}</div>`;
        
        chatHistory.appendChild(msgDiv);
        msgDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function showThinking(role, agentName = 'AI') {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}-msg thinking-bubble`;
        msgDiv.id = 'thinking-msg';
        
        let avatar = '🧠';
        if (agentName.includes('Query')) avatar = '📚';
        else if (agentName.includes('Quiz')) avatar = '✏️';

        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatar}</div>
            <div class="msg-content shimmer" style="height: 60px; width: 250px; border-radius: 20px;"></div>
        `;
        chatHistory.appendChild(msgDiv);
        msgDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return msgDiv;
    }

    function removeThinking() {
        const thinking = document.getElementById('thinking-msg');
        if (thinking) thinking.remove();
    }

    function setActiveNode(nodeKey) {
        // Reset all active states
        Object.values(nodes).forEach(node => {
            if (node) {
                node.classList.remove('active-coordinator', 'active-query', 'active-recommendation', 'active-quiz', 'active-pdf');
            }
        });

        if (nodeKey && nodes[nodeKey]) {
            // Coordinator is always active while routing...
            const activeClass = `active-${nodeKey}`;
            nodes[nodeKey].classList.add(activeClass);
        }
    }

    const attachBtn = document.getElementById('attach-btn');
    const pdfUpload = document.getElementById('pdf-upload');

    // Handle File Attachment Click
    attachBtn.addEventListener('click', () => pdfUpload.click());

    // Handle PDF File Selection
    pdfUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            appendMessage('agent', 'Please select a valid PDF file.', 'System');
            return;
        }

        // Show loading state
        setActiveNode('pdf');
        appendMessage('user', file.name, null, true);
        
        // Progressive feedback
        const loadingMsgId = Date.now();
        showThinking('agent', 'PDF Summarizer');
        addLog('pdf', 'File received: ' + file.name);
        
        setTimeout(() => addLog('pdf', 'Extracting text and metadata...'), 1000);
        setTimeout(() => addLog('pdf', 'Consulting Precision Analyst AI...'), 2500);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', 'default-session');

        try {
            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                removeThinking();
                appendMessage('agent', data.response, data.decision);
                setActiveNode(null); 
            } else {
                removeThinking();
                appendMessage('agent', `Error: ${data.detail}`, 'System Error');
            }
        } catch (error) {
            removeThinking();
            appendMessage('agent', 'Could not upload file.', 'System Error');
        } finally {
            pdfUpload.value = ''; // Reset input
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;

        // Add user msg to UI
        appendMessage('user', text);
        userInput.value = '';
        sendBtn.disabled = true;

        // UI Effects - Step 1: Coordinator Start
        setActiveNode('coordinator');
        showThinking('agent', 'Coordinator');
        addLog('Coordinator received request.', false);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: text,
                    session_id: sessionId
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            
            // UI Effects - Step 2: Show Intent
            addLog(`Intent classified as ${data.decision}.`, true);
            
            // Sub-Agent Activation
            let subNodeKey = data.decision.toLowerCase();
            if (subNodeKey.includes('quiz')) subNodeKey = 'quiz';
            else if (subNodeKey.includes('recommend')) subNodeKey = 'recommendation';
            else if (subNodeKey.includes('query')) subNodeKey = 'query';
            else if (subNodeKey.includes('pdf')) subNodeKey = 'pdf';
            
            if(nodes[subNodeKey]) {
                setActiveNode(subNodeKey);
                addLog(`Delegated to ${data.agent || subNodeKey}.`, false);
            }

            // Final delivery
            setTimeout(() => {
                removeThinking();
                appendMessage('agent', data.response, data.agent);
                addLog('Response delivered.', true);
                
                setTimeout(() => setActiveNode(null), 2000);
                sendBtn.disabled = false;
                userInput.focus();
            }, 600);

        } catch (error) {
            console.error('Error:', error);
            removeThinking();
            appendMessage('agent', 'Sorry, I encountered an error. Please check your connection.', 'System Error');
            addLog('API Connection failed.', true);
            setActiveNode(null);
            sendBtn.disabled = false;
        }
    });
});
