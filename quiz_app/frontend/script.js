const API_BASE = '/api';
let currentUser = { id: null, name: '', email: '' };
let currentQuiz = { category: '', questions: [], currentIndex: 0, answers: [], startTime: null };
let timerInterval;

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function goHome() { showScreen('homeScreen'); clearInterval(timerInterval); }
function goToCategories() { showScreen('categoriesScreen'); loadCategories(); }
function goToLeaderboard() { showScreen('leaderboardScreen'); loadLeaderboard(); }

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const data = await response.json();
        const grid = document.getElementById('categoriesGrid');
        grid.innerHTML = '';
        data.categories.forEach(category => {
            const card = document.createElement('div');
            card.className = 'category-card';
            card.textContent = category;
            card.onclick = () => startQuiz(category);
            grid.appendChild(card);
        });
    } catch (error) { console.error('Error loading categories:', error); }
}

async function startQuiz(category) {
    try {
        const response = await fetch(`${API_BASE}/questions?category=${encodeURIComponent(category)}&limit=10`);
        const data = await response.json();
        currentQuiz = { category, questions: data.questions, currentIndex: 0, answers: Array(data.questions.length).fill(null), startTime: Date.now() };
        showScreen('quizScreen');
        loadQuestion(0);
        startTimer();
    } catch (error) { console.error('Error starting quiz:', error); }
}

function loadQuestion(index) {
    const q = currentQuiz.questions[index];
    document.getElementById('questionNumber').textContent = `${index + 1}/${currentQuiz.questions.length}`;
    document.getElementById('questionText').textContent = q.question;
    const badge = document.getElementById('difficultyBadge');
    badge.textContent = q.difficulty.toUpperCase();
    badge.className = `difficulty ${q.difficulty}`;
    const container = document.getElementById('optionsContainer');
    container.innerHTML = '';
    q.options.forEach((option, i) => {
        const div = document.createElement('div');
        div.className = 'option';
        if (currentQuiz.answers[index] === i) div.classList.add('selected');
        div.textContent = option;
        div.onclick = () => selectOption(i);
        container.appendChild(div);
    });
    document.getElementById('prevBtn').disabled = index === 0;
    document.getElementById('nextBtn').textContent = index === currentQuiz.questions.length - 1 ? 'Submit' : 'Next';
    const progress = ((index + 1) / currentQuiz.questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
}

function selectOption(index) { currentQuiz.answers[currentQuiz.currentIndex] = index; loadQuestion(currentQuiz.currentIndex); }
function prevQuestion() { if (currentQuiz.currentIndex > 0) { currentQuiz.currentIndex--; loadQuestion(currentQuiz.currentIndex); } }
function nextQuestion() { if (currentQuiz.currentIndex === currentQuiz.questions.length - 1) { submitQuiz(); } else { currentQuiz.currentIndex++; loadQuestion(currentQuiz.currentIndex); } }

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - currentQuiz.startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('timer').textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

async function submitQuiz() {
    clearInterval(timerInterval);
    const answers = currentQuiz.questions.map((q, i) => ({ question_id: q.id, selected_option: currentQuiz.answers[i] }));
    const timeTaken = Math.floor((Date.now() - currentQuiz.startTime) / 1000);
    try {
        currentUser.name = document.getElementById('userName').value || 'Guest';
        currentUser.email = document.getElementById('userEmail').value || `guest_${Date.now()}@quiz.local`;
        const response = await fetch(`${API_BASE}/quiz/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_name: currentUser.name, user_email: currentUser.email, category: currentQuiz.category, answers, time_taken: timeTaken })
        });
        const data = await response.json();
        currentUser.id = data.user_id;
        showResults(data, timeTaken);
    } catch (error) { console.error('Error submitting quiz:', error); }
}

function showResults(data, timeTaken) {
    document.getElementById('scorePercentage').textContent = Math.round(data.percentage) + '%';
    document.getElementById('scoreDisplay').textContent = data.score;
    document.getElementById('totalDisplay').textContent = data.total;
    document.getElementById('resultCategory').textContent = currentQuiz.category;
    const minutes = Math.floor(timeTaken / 60);
    const seconds = timeTaken % 60;
    document.getElementById('resultTime').textContent = `${minutes}:${String(seconds).padStart(2, '0')}`;
    const detailed = document.getElementById('detailedResults');
    detailed.innerHTML = '';
    data.results.forEach(r => {
        const div = document.createElement('div');
        div.className = `result-item ${r.is_correct ? 'correct' : 'incorrect'}`;
        div.innerHTML = `<div class="result-question">${r.question}</div><div class="result-answer"><span class="${r.is_correct ? 'correct' : 'incorrect'}">${r.selected || 'Not answered'}</span></div><div class="result-answer correct">Correct: ${r.correct_answer}</div><div class="result-answer" style="color:#cbd5e1;margin-top:.5rem">${r.explanation}</div>`;
        detailed.appendChild(div);
    });
    showScreen('resultsScreen');
}

async function loadLeaderboard() {
    try {
        const response = await fetch(`${API_BASE}/leaderboard?limit=15`);
        const data = await response.json();
        const body = document.getElementById('leaderboardBody');
        body.innerHTML = '';
        data.leaderboard.forEach(entry => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>#${entry.rank}</td><td>${entry.name}</td><td>${entry.avg_score.toFixed(1)}%</td><td>${entry.quizzes_taken}</td>`;
            body.appendChild(tr);
        });
    } catch (error) { console.error('Error loading leaderboard:', error); }
}

document.addEventListener('DOMContentLoaded', () => {
    showScreen('homeScreen');
    document.getElementById('userName').addEventListener('keypress', e => { if (e.key === 'Enter') goToCategories(); });
    document.getElementById('userEmail').addEventListener('keypress', e => { if (e.key === 'Enter') goToCategories(); });
});

// Register service worker for offline support
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js').catch(err => console.log('SW registration failed:', err));
}
