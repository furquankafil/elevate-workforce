document.addEventListener('DOMContentLoaded', () => {
    const aiTrigger = document.getElementById('ai-chat-trigger');
    const aiWindow = document.getElementById('ai-chat-window');
    const aiClose = document.getElementById('ai-chat-close');
    const aiChatForm = document.getElementById('ai-chat-form');
    const aiUserInput = document.getElementById('ai-user-input');
    const aiChatLogs = document.getElementById('ai-chat-body-wrap');
    const aiIndicator = document.getElementById('ai-typing-indicator');
    const aiProgressBar = document.getElementById('ai-progress-bar');
    const aiOptionsBar = document.getElementById('ai-dynamic-options-bar');
    const aiSubmitBtn = document.getElementById('ai-submit-btn');
    const aiAttachTrigger = document.getElementById('ai-attach-trigger');
    const aiResumeFile = document.getElementById('ai-resume-file');

    let currentRole = null;
    let currentState = 'START';
    let isSubmitting = false;

    // Helper: Safely Extract CSRF Token
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue || '';
    }

    const capturedData = {
        name: '',
        email: '',
        phone: '',
        location: '',
        company: '',
        skills_needs: '',
        resume_file: null
    };

    const stepsCandidate = ['START', 'CAND_NAME', 'CAND_EMAIL', 'CAND_PHONE', 'CAND_COUNTRY', 'CAND_SKILLS', 'CAND_RESUME', 'FINISHED'];
    const stepsEmployer = ['START', 'EMP_NAME', 'EMP_COMPANY', 'EMP_EMAIL', 'EMP_PHONE', 'EMP_NEEDS', 'FINISHED'];

    function updateProgress() {
        const array = (currentRole === 'candidate') ? stepsCandidate : stepsEmployer;
        const index = array.indexOf(currentState);
        if (index !== -1) {
            const pct = Math.round((index / (array.length - 1)) * 100);
            aiProgressBar.style.width = `${pct}%`;
            aiProgressBar.setAttribute('aria-valuenow', pct);
        } else if (currentState === 'AI_CHAT') {
            aiProgressBar.style.width = '100%';
        }
    }

    // Modern Robotic Assistant Avatar SVG (40px x 40px - 25% Larger)
    function appendMessage(sender, text) {
        const bubbleWrap = document.createElement('div');
        bubbleWrap.className = `d-flex align-items-start gap-2 mb-3 ${sender === 'user' ? 'justify-content-end' : ''}`;
        
        let avatarHTML = '';
        if (sender === 'bot') {
            avatarHTML = `
                <div class="ai-msg-avatar bg-white border p-1 rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="28" height="28">
                        <circle cx="32" cy="32" r="30" fill="#0B3D91"/>
                        <path d="M 20 22 L 44 22 C 48 22 50 26 50 30 L 50 42 C 50 46 48 48 44 48 L 20 48 C 16 48 14 46 14 42 L 14 30 C 14 26 16 22 20 22 Z" fill="#FFFFFF"/>
                        <circle cx="24" cy="32" r="3.5" fill="#00AEEF"/>
                        <circle cx="40" cy="32" r="3.5" fill="#00AEEF"/>
                        <path d="M 28 40 Q 32 43 36 40" stroke="#0B3D91" stroke-width="2" fill="none"/>
                    </svg>
                </div>
            `;
        }

        const formattedText = text.replace(/\n/g, '<br>');

        const cardHtml = `
            <div class="d-flex align-items-start gap-2 max-width-100 ${sender === 'user' ? 'flex-row-reverse' : ''}">
                ${avatarHTML}
                <div class="${sender === 'user' ? 'user-msg-bubble' : 'bot-msg-bubble'} poppins-regular fs-13">
                    ${formattedText}
                </div>
            </div>
        `;
        
        bubbleWrap.innerHTML = cardHtml;
        aiChatLogs.appendChild(bubbleWrap);
        aiChatLogs.scrollTop = aiChatLogs.scrollHeight;
    }

    function showTyping(ms, callback) {
        aiIndicator.classList.remove('d-none');
        aiChatLogs.scrollTop = aiChatLogs.scrollHeight;
        setTimeout(() => {
            aiIndicator.classList.add('d-none');
            if (callback) callback();
        }, ms);
    }

    function configureInput(placeholder, enabled = true) {
        aiUserInput.placeholder = placeholder;
        if (enabled) {
            aiUserInput.removeAttribute('disabled');
            aiSubmitBtn.removeAttribute('disabled');
            aiUserInput.focus();
        } else {
            aiUserInput.setAttribute('disabled', 'true');
            aiSubmitBtn.setAttribute('disabled', 'true');
        }
    }

    function showPills(optionsList, onSelectCallback) {
        aiOptionsBar.innerHTML = '';
        aiOptionsBar.classList.remove('d-none');
        optionsList.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-outline-secondary poppins-semibold px-2 py-1 fs-12';
            btn.textContent = opt;
            btn.type = 'button';
            btn.addEventListener('click', () => {
                aiOptionsBar.classList.add('d-none');
                appendMessage('user', opt);
                onSelectCallback(opt);
            });
            aiOptionsBar.appendChild(btn);
        });
        aiChatLogs.scrollTop = aiChatLogs.scrollHeight;
    }

    function transitionToNextState() {
        updateProgress();

        if (currentRole === 'candidate') {
            switch(currentState) {
                case 'CAND_NAME':
                    configureInput("Enter your full name...");
                    showTyping(600, () => {
                        appendMessage('bot', "Great! Please enter your <strong>Full Name</strong> as shown in your passport.");
                    });
                    break;
                case 'CAND_EMAIL':
                    configureInput("Enter your email address...");
                    showTyping(600, () => {
                        appendMessage('bot', `Perfect. What is your active <strong>Email Address</strong>, <strong>${capturedData.name}</strong>?`);
                    });
                    break;
                case 'CAND_PHONE':
                    configureInput("WhatsApp number: e.g. +91 98979 20091");
                    showTyping(600, () => {
                        appendMessage('bot', "Got it. Please enter your mobile/WhatsApp number with country code.");
                    });
                    break;
                case 'CAND_COUNTRY':
                    configureInput("Choose preferred destination...", false);
                    showTyping(600, () => {
                        appendMessage('bot', "Which region/country are you most interested in?");
                        showPills(['Dubai (UAE)', 'Saudi Arabia', 'Qatar', 'Romania', 'Croatia', 'Other Destination'], (selectedVal) => {
                            capturedData.location = selectedVal;
                            currentState = 'CAND_SKILLS';
                            transitionToNextState();
                        });
                    });
                    break;
                case 'CAND_SKILLS':
                    configureInput("Type trade / skills (e.g. Pipe Welder, Nurse)...");
                    showTyping(600, () => {
                        appendMessage('bot', "What is your trade or primary skills? E.g., Pipe Welder, Nurse, HVAC Technician, Driver.");
                    });
                    break;
                case 'CAND_RESUME':
                    configureInput("Attach CV or type 'Skip'...", true);
                    aiAttachTrigger.removeAttribute('disabled');
                    showTyping(600, () => {
                        appendMessage('bot', "Please upload your CV document by clicking the 📎 clip icon below, or type 'Skip' to proceed.");
                    });
                    break;
                case 'FINISHED':
                    configureInput("Processing candidate profile...", false);
                    aiAttachTrigger.setAttribute('disabled', 'true');
                    showTyping(1000, () => {
                        appendMessage('bot', "Structuring your candidate registration...");
                        submitLeadToBackend();
                    });
                    break;
            }
        } 
        else if (currentRole === 'employer') {
            switch(currentState) {
                case 'EMP_NAME':
                    configureInput("Enter your full name & designation...");
                    showTyping(600, () => {
                        appendMessage('bot', "Welcome! Please enter your <strong>Full Name & Designation</strong>.");
                    });
                    break;
                case 'EMP_COMPANY':
                    configureInput("Enter company name...");
                    showTyping(600, () => {
                        appendMessage('bot', `What is your <strong>Company / Organization Name</strong>, ${capturedData.name}?`);
                    });
                    break;
                case 'EMP_EMAIL':
                    configureInput("Business email address...");
                    showTyping(600, () => {
                        appendMessage('bot', "What is your direct <strong>Business Email Address</strong>?");
                    });
                    break;
                case 'EMP_PHONE':
                    configureInput("Business phone / WhatsApp...");
                    showTyping(600, () => {
                        appendMessage('bot', "What is your contact / WhatsApp number?");
                    });
                    break;
                case 'EMP_NEEDS':
                    configureInput("E.g., Need 50 Welders, 10 Engineers...");
                    showTyping(600, () => {
                        appendMessage('bot', "Briefly list the trades, vacancies, or manpower numbers you need to recruit:");
                    });
                    break;
                case 'FINISHED':
                    configureInput("Logging corporate inquiry...", false);
                    showTyping(1000, () => {
                        appendMessage('bot', "Logging your corporate requirements...");
                        submitEmployerLead();
                    });
                    break;
            }
        }
    }

    function submitLeadToBackend() {
        if (isSubmitting) return;
        isSubmitting = true;

        const formData = new FormData();
        formData.append('action', 'submit_candidate_lead');
        formData.append('name', capturedData.name);
        formData.append('email', capturedData.email);
        formData.append('phone', capturedData.phone);
        formData.append('location', capturedData.location);
        formData.append('skills', capturedData.skills_needs);
        if (capturedData.resume_file) {
            formData.append('resume', capturedData.resume_file);
        }

        fetch('/api/ai-chat/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(res => {
            if (!res.ok) throw new Error("Server error");
            return res.json();
        })
        .then(data => {
            isSubmitting = false;
            currentState = 'AI_CHAT';
            appendMessage('bot', `🎉 <strong>Profile Registered Successfully!</strong><br><br>${data.response || 'Our team will review your profile shortly.'}`);
            configureInput("Ask me anything about overseas jobs, visas, or requirements...", true);
        })
        .catch(() => {
            isSubmitting = false;
            currentState = 'AI_CHAT';
            appendMessage('bot', "Your details have been saved. You can also chat directly on WhatsApp: <a href='https://wa.me/919897920091' target='_blank'><strong>+91 9897920091</strong></a>.");
            configureInput("Ask me any question about Elevate Workforce...", true);
        });
    }

    function submitEmployerLead() {
        if (isSubmitting) return;
        isSubmitting = true;

        const formData = new FormData();
        formData.append('action', 'submit_employer_lead');
        formData.append('name', capturedData.name);
        formData.append('company_name', capturedData.company);
        formData.append('email', capturedData.email);
        formData.append('phone', capturedData.phone);
        formData.append('needs', capturedData.skills_needs);

        fetch('/api/ai-chat/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(res => {
            if (!res.ok) throw new Error("Server error");
            return res.json();
        })
        .then(data => {
            isSubmitting = false;
            currentState = 'AI_CHAT';
            appendMessage('bot', `🤝 <strong>Inquiry Captured!</strong><br><br>${data.response || 'Our executive director will review your requirements.'}`);
            configureInput("Ask me anything about manpower deployment, SLAs, or trades...", true);
        })
        .catch(() => {
            isSubmitting = false;
            currentState = 'AI_CHAT';
            appendMessage('bot', "Your inquiry is captured. For rapid allocation, contact **Mirza Khalique Beg** directly on +91 9897920091.");
            configureInput("Ask me any question...", true);
        });
    }

    function handleLiveAIChat(userQuestion) {
        if (isSubmitting) return;
        isSubmitting = true;

        configureInput("AI is thinking...", false);

        const formData = new FormData();
        formData.append('action', 'chat');
        formData.append('message', userQuestion);
        formData.append('role', currentRole || 'general');

        showTyping(1200, () => {
            fetch('/api/ai-chat/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(res => res.json())
            .then(data => {
                isSubmitting = false;
                appendMessage('bot', data.response || "I am here to assist with international recruitment. How else can I help?");
                configureInput("Type your question here...", true);
            })
            .catch(() => {
                isSubmitting = false;
                appendMessage('bot', "I am currently assisting multiple clients. For immediate response, please contact us on WhatsApp: +91 9897920091.");
                configureInput("Type your question here...", true);
            });
        });
    }

    // Toggle Chat Window
    if (aiTrigger && aiWindow) {
        aiTrigger.addEventListener('click', () => {
            aiWindow.classList.toggle('d-none');
            aiChatLogs.scrollTop = aiChatLogs.scrollHeight;
            
            const initFork = document.getElementById('ai-initial-fork');
            if (initFork) {
                configureInput("Select an option above to begin...", false);
            }
        });
    }

    if (aiClose && aiWindow) {
        aiClose.addEventListener('click', () => {
            aiWindow.classList.add('d-none');
        });
    }

    // Role Selection Click Handler
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.ai-fork-btn')) {
            const btn = e.target.closest('.ai-fork-btn');
            currentRole = btn.getAttribute('data-role');
            const userChoiceText = (currentRole === 'candidate') ? "I am looking for international jobs" : "I am an Employer / Corporate Client";
            
            const initFork = document.getElementById('ai-initial-fork');
            if (initFork) initFork.remove();

            appendMessage('user', userChoiceText);

            if (currentRole === 'candidate') {
                currentState = 'CAND_NAME';
            } else {
                currentState = 'EMP_NAME';
            }
            transitionToNextState();
        }
    });

    // File Attachment Handler
    if (aiAttachTrigger && aiResumeFile) {
        aiAttachTrigger.addEventListener('click', () => {
            aiResumeFile.click();
        });

        aiResumeFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                capturedData.resume_file = file;
                appendMessage('user', `📎 Attached File: ${file.name} (${Math.round(file.size / 1024)} KB)`);
                
                currentState = 'FINISHED';
                transitionToNextState();
            }
        });
    }

    // Form Submission Handler
    if (aiChatForm) {
        aiChatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const rawVal = aiUserInput.value.trim();
            if (!rawVal) return;

            // Handle Active Conversational AI Chat Mode
            if (currentState === 'AI_CHAT') {
                appendMessage('user', rawVal);
                aiUserInput.value = '';
                handleLiveAIChat(rawVal);
                return;
            }

            appendMessage('user', rawVal);
            aiUserInput.value = '';

            if (currentRole === 'candidate') {
                if (currentState === 'CAND_NAME') {
                    capturedData.name = rawVal;
                    currentState = 'CAND_EMAIL';
                } else if (currentState === 'CAND_EMAIL') {
                    if (!rawVal.includes('@')) {
                        appendMessage('bot', "⚠️ Please enter a valid email address containing '@' to continue.");
                        return;
                    }
                    capturedData.email = rawVal;
                    currentState = 'CAND_PHONE';
                } else if (currentState === 'CAND_PHONE') {
                    capturedData.phone = rawVal;
                    currentState = 'CAND_COUNTRY';
                } else if (currentState === 'CAND_SKILLS') {
                    capturedData.skills_needs = rawVal;
                    currentState = 'CAND_RESUME';
                } else if (currentState === 'CAND_RESUME') {
                    currentState = 'FINISHED';
                }
            } 
            else if (currentRole === 'employer') {
                if (currentState === 'EMP_NAME') {
                    capturedData.name = rawVal;
                    currentState = 'EMP_COMPANY';
                } else if (currentState === 'EMP_COMPANY') {
                    capturedData.company = rawVal;
                    currentState = 'EMP_EMAIL';
                } else if (currentState === 'EMP_EMAIL') {
                    if (!rawVal.includes('@')) {
                        appendMessage('bot', "⚠️ Please enter a valid corporate email address.");
                        return;
                    }
                    capturedData.email = rawVal;
                    currentState = 'EMP_PHONE';
                } else if (currentState === 'EMP_PHONE') {
                    capturedData.phone = rawVal;
                    currentState = 'EMP_NEEDS';
                } else if (currentState === 'EMP_NEEDS') {
                    capturedData.skills_needs = rawVal;
                    currentState = 'FINISHED';
                }
            }

            transitionToNextState();
        });
    }
});

function appendMessage(sender, text) {
        const bubbleWrap = document.createElement('div');
        bubbleWrap.className = `d-flex align-items-start gap-2 mb-3 ${sender === 'user' ? 'justify-content-end' : ''}`;
        
        let avatarHTML = '';
        if (sender === 'bot') {
            avatarHTML = `
                <div class="ai-msg-avatar bg-white border p-1 rounded-circle d-flex align-items-center justify-content-center" style="width: 36px; height: 36px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="26" height="26">
                        <circle cx="32" cy="32" r="30" fill="#0B3D91"/>
                        <path d="M 20 22 L 44 22 C 48 22 50 26 50 30 L 50 42 C 50 46 48 48 44 48 L 20 48 C 16 48 14 46 14 42 L 14 30 C 14 26 16 22 20 22 Z" fill="#FFFFFF"/>
                        <circle cx="24" cy="32" r="3.5" fill="#00AEEF"/>
                        <circle cx="40" cy="32" r="3.5" fill="#00AEEF"/>
                        <path d="M 28 40 Q 32 43 36 40" stroke="#0B3D91" stroke-width="2" fill="none"/>
                    </svg>
                </div>
            `;
        }

        const formattedText = text.replace(/\n/g, '<br>');

        const cardHtml = `
            <div class="d-flex align-items-start gap-2 max-width-100 ${sender === 'user' ? 'flex-row-reverse' : ''}">
                ${avatarHTML}
                <div class="${sender === 'user' ? 'user-msg-bubble' : 'bot-msg-bubble'} poppins-regular fs-13">
                    ${formattedText}
                </div>
            </div>
        `;
        
        bubbleWrap.innerHTML = cardHtml;
        aiChatLogs.appendChild(bubbleWrap);
        
        // Smooth scroll to bottom after appending message
        setTimeout(() => {
            aiChatLogs.scrollTop = aiChatLogs.scrollHeight;
        }, 50);
    }