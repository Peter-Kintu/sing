// Base URL for API calls
const BASE_API_URL = '/api';

// DOM Elements
const form = document.getElementById('lyrics-form');
const lyricsInput = document.getElementById('lyrics-input');
const genreSelect = document.getElementById('genre-select');
const moodSelect = document.getElementById('mood-select');
const titleInput = document.getElementById('title-input');
const languageSelect = document.getElementById('language-select');
const voiceTypeSelect = document.getElementById('voice-type-select');
const publicCheckbox = document.getElementById('is-public-checkbox');

const generateButton = document.getElementById('generate-button');

const inputStage = document.getElementById('input-form-stage');
const processingStage = document.getElementById('processing-stage');
const resultStage = document.getElementById('result-stage');

const progressBar = document.getElementById('progress-bar');
const progressMessage = document.getElementById('progress-message');

const audioPlayer = document.getElementById('audio-player');
const downloadLink = document.getElementById('download-link');
const remixButton = document.getElementById('remix-button');
const currentStatusSpan = document.getElementById('current-status');
const remixOrigin = document.getElementById('remix-origin');
const remixSourceTitle = document.getElementById('remix-source-title');

let pollingInterval;
let remixSourceId = null; // Optional: set this if remixing

// --- Utility Functions ---

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Form Submission ---

async function handleSubmit(e) {
    e.preventDefault();

    const lyrics = lyricsInput.value.trim();
    if (!lyrics || lyrics.length < 10) {
        alert("Lyrics must be at least 10 characters.");
        return;
    }

    inputStage.style.display = 'none';
    processingStage.style.display = 'block';

    const csrfToken = getCookie('csrftoken');

    const data = {
        title: titleInput?.value || null,
        lyrics: lyrics,
        genre: genreSelect.value.toLowerCase(),
        mood: moodSelect.value.toLowerCase(),
        language: languageSelect?.value.charAt(0).toUpperCase() + languageSelect.value.slice(1),
        voice_type: voiceTypeSelect?.value?.toLowerCase() || null,
        is_public: publicCheckbox?.checked || false,
        remix_of: remixSourceId || null
    };

    console.log("📦 Submitting payload:", data);

    try {
        const response = await fetch(`${BASE_API_URL}/generate-song/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorDetails = await response.json();
            console.error("❌ Backend validation errors:", errorDetails);
            progressMessage.textContent = `Error: ${JSON.stringify(errorDetails)}.`;
            progressBar.style.backgroundColor = 'red';
            setTimeout(() => {
                processingStage.style.display = 'none';
                inputStage.style.display = 'block';
            }, 5000);
            return;
        }

        const songRequest = await response.json();
        console.log("✅ Song request submitted. ID:", songRequest.id);

        startPolling(songRequest.id);

    } catch (error) {
        console.error("Submission Error:", error);
        progressMessage.textContent = `Error: ${error.message}. Please check console.`;
        progressBar.style.backgroundColor = 'red';
        setTimeout(() => {
            processingStage.style.display = 'none';
            inputStage.style.display = 'block';
        }, 5000);
    }
}

// --- Polling Logic ---

function startPolling(requestId) {
    const steps = [
        { status: 'PENDING', progress: 10, message: 'Received request. Starting generation...' },
        { status: 'AUDIO_READY', progress: 100, message: '✅ Audio generated! Your anthem is ready!' },
        { status: 'FAILED', progress: 100, message: 'Generation failed. Please try again.' }
    ];

    const pollStatus = async () => {
        try {
            const response = await fetch(`${BASE_API_URL}/status/${requestId}/`);
            if (!response.ok) {
                throw new Error(`Status check failed with status ${response.status}`);
            }

            const data = await response.json();
            const status = data.status;
            const step = steps.find(s => s.status === status);

            if (step) {
                progressBar.style.width = `${step.progress}%`;
                progressMessage.textContent = step.message;
                currentStatusSpan.textContent = status;
            }

            if (status === 'AUDIO_READY' && data.audio_url) {
                clearInterval(pollingInterval);
                displayResults(data);
            } else if (status === 'FAILED') {
                clearInterval(pollingInterval);
                displayFailure();
            }

        } catch (error) {
            clearInterval(pollingInterval);
            console.error("Polling Error:", error);
            progressMessage.textContent = `Polling failed. Check API connectivity.`;
            displayFailure();
        }
    };

    pollingInterval = setInterval(pollStatus, 3000);
}

// --- Result Display ---

function displayResults(data) {
    processingStage.style.display = 'none';
    resultStage.style.display = 'block';

    audioPlayer.src = data.audio_url;
    audioPlayer.style.display = 'block';

    downloadLink.href = data.audio_url;
    remixButton.style.display = 'inline-block';
    currentStatusSpan.textContent = "Completed";
    progressBar.style.backgroundColor = 'green';

    if (data.remix_of && data.original_title) {
        remixOrigin.style.display = 'block';
        remixSourceTitle.textContent = data.original_title;
    }
}

function displayFailure() {
    processingStage.style.display = 'none';
    resultStage.style.display = 'block';
    document.getElementById('result-heading').textContent = "💔 Generation Failed";
    document.getElementById('result-heading').classList.remove('text-success');
    document.getElementById('result-heading').classList.add('text-danger');
    currentStatusSpan.textContent = "Failed";
}

// --- Event Listeners ---
form.addEventListener('submit', handleSubmit);