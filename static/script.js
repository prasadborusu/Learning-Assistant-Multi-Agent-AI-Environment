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
        'quiz': document.getElementById('node-quiz')
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

    function appendMessage(role, text, agentName = null) {
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
        }

        const htmlContent = role === 'user' ? `<p>${text}</p>` : marked.parse(text);

        msgDiv.innerHTML = `<div class="msg-avatar">${avatar}</div><div class="msg-content"><strong>${author}</strong>${htmlContent}</div>`;

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function setActiveNode(nodeKey) {
        // Reset all active states
        Object.values(nodes).forEach(node => {
            node.classList.remove('active-coordinator', 'active-query', 'active-recommendation', 'active-quiz');
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
            addMessage('System', 'Please select a valid PDF file.', 'agent');
            return;
        }

        // Show loading state
        addMessage('You', `[Uploading PDF: ${file.name}]`, 'user');
        const loadingMsgId = Date.now();
        addMessage('Coordinator', 'Analyzing document...', 'agent');

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
                // Remove loading msg if possible or just append
                addMessage('PDF Summarizer Agent', data.response, 'agent');
                updateAgentActivity('active-quiz', false); // Clean up state
                updateAgentActivity('active-recommendation', false);
                updateAgentActivity('active-query', false);
                updateAgentActivity('active-quiz', true); // Visual highlight for result
            } else {
                addMessage('System', `Error: ${data.detail}`, 'agent');
            }
        } catch (error) {
            addMessage('System', 'Could not upload file.', 'agent');
        } finally {
            pdfUpload.value = ''; // Reset input
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;

        // Apply localization prompt modifier (advanced feature requirement)
        const lang = languageSelect.value;
        let modifiedPrompt = text;
        if(lang !== 'en') {
            modifiedPrompt = `[Reply in ${lang.toUpperCase()}] ` + text;
        }

        // Add user msg to UI
        appendMessage('user', text);
        userInput.value = '';
        sendBtn.disabled = true;

        // UI Effects - Step 1: Coordinator takes the request
        setActiveNode('coordinator');
        nodes['coordinator'].classList.add('active-coordinator'); // Force coordinator visually active
        addLog('Coordinator received request.', false);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: modifiedPrompt,
                    session_id: sessionId
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();

            // UI Effects - Step 2: Show Routing intent
            addLog(`Intent classified: [${data.decision}]`, true);
            
            // UI Effects - Step 3: Activate specific Sub-Agent visually
            setTimeout(() => {
                const subNodeKey = data.agent_used.replace('Agent', '').toLowerCase();
                if(nodes[subNodeKey]) {
                    setActiveNode(subNodeKey);
                    addLog(`Delegated task to ${data.agent_used}.`, false);
                }

                // Show response after a tiny delay for visual effect
                setTimeout(() => {
                    appendMessage('agent', data.response, data.agent_used);
                    addLog('Response delivered to user.', true);
                    
                    // Reset glowing nodes after delivery
                    setTimeout(() => setActiveNode(null), 1500);
                    sendBtn.disabled = false;
                    userInput.focus();
                }, 800);
            }, 800);

        } catch (error) {
            console.error('Error:', error);
            appendMessage('agent', 'Sorry, I encountered an error connecting to the backend system. Please ensure the server is running and the API key is configured.', 'System Error');
            addLog('API Error: Connection failed.', true);
            setActiveNode(null);
            sendBtn.disabled = false;
        }
    });
});
