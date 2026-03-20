import os
from flask import Flask, request, jsonify, render_template_string
from mentor import generate_problem, give_hint, evaluate_solution
from memory import get_learning_profile

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CodeCoach AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .header { background: #1e293b; padding: 16px 32px; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 12px; }
        .header h1 { font-size: 22px; color: #60a5fa; }
        .header p { font-size: 13px; color: #94a3b8; }
        .container { max-width: 900px; margin: 32px auto; padding: 0 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
        .card h2 { font-size: 16px; color: #94a3b8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }
        input[type=text] { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 10px 14px; border-radius: 8px; font-size: 14px; width: 220px; }
        input[type=text]:focus { outline: none; border-color: #60a5fa; }
        textarea { width: 100%; height: 160px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 14px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 14px; resize: vertical; }
        textarea:focus { outline: none; border-color: #60a5fa; }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 500; transition: opacity 0.2s; }
        .btn:hover { opacity: 0.85; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-secondary { background: #334155; color: #e2e8f0; }
        .btn-success { background: #10b981; color: white; }
        .btn-row { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
        .problem-box { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 20px; }
        .problem-title { font-size: 18px; font-weight: 600; color: #60a5fa; margin-bottom: 8px; }
        .problem-meta { font-size: 12px; color: #64748b; margin-bottom: 12px; }
        .problem-desc { color: #cbd5e1; line-height: 1.6; }
        .feedback-box { padding: 16px; border-radius: 8px; margin-top: 16px; line-height: 1.6; }
        .feedback-correct { background: #064e3b; border: 1px solid #10b981; color: #6ee7b7; }
        .feedback-wrong { background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; }
        .feedback-hint { background: #1e3a5f; border: 1px solid #3b82f6; color: #93c5fd; }
        .feedback-profile { background: #0f172a; border: 1px solid #334155; color: #cbd5e1; white-space: pre-line; }
        .loading { color: #64748b; font-style: italic; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 6px; }
        .badge-easy { background: #064e3b; color: #6ee7b7; }
        .badge-medium { background: #451a03; color: #fbbf24; }
        .badge-hard { background: #450a0a; color: #fca5a5; }
        #feedback { min-height: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>CodeCoach AI</h1>
            <p>Your personal coding mentor that remembers everything</p>
        </div>
    </div>

    <div class="container">
        <!-- User setup -->
        <div class="card">
            <h2>Who are you?</h2>
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap">
                <input type="text" id="user-id" placeholder="Enter your name e.g. keshav">
                <button class="btn btn-primary" onclick="getNewProblem()">Get My Problem</button>
                <button class="btn btn-secondary" onclick="getProfile()">My Learning Profile</button>
            </div>
        </div>

        <!-- Problem display -->
        <div class="card" id="problem-card" style="display:none">
            <h2>Your Problem</h2>
            <div class="problem-box">
                <div class="problem-title" id="problem-title"></div>
                <div class="problem-meta" id="problem-meta"></div>
                <div class="problem-desc" id="problem-desc"></div>
            </div>
        </div>

        <!-- Code editor -->
        <div class="card" id="editor-card" style="display:none">
            <h2>Your Solution</h2>
            <textarea id="code" placeholder="Write your Python code here..."></textarea>
            <div class="btn-row">
                <button class="btn btn-secondary" onclick="getHint()">Get Hint</button>
                <button class="btn btn-success" onclick="submitSolution()">Submit Solution</button>
            </div>
        </div>

        <!-- Feedback -->
        <div id="feedback"></div>
    </div>

<script>
let currentProblem = "";
let currentTopic = "";

function getUserId() {
    const uid = document.getElementById('user-id').value.trim();
    if (!uid) { alert("Please enter your name first!"); return null; }
    return uid;
}

function setFeedback(html) {
    document.getElementById('feedback').innerHTML = html;
}

async function getNewProblem() {
    const uid = getUserId();
    if (!uid) return;
    
    setFeedback('<div class="card"><p class="loading">Generating your personalized problem based on your history...</p></div>');
    
    const r = await fetch('/api/problem', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: uid})
    });
    const data = await r.json();
    
    currentProblem = data.description;
    currentTopic = data.topic;
    
    const badgeClass = 'badge-' + (data.difficulty || 'easy').toLowerCase();
    
    document.getElementById('problem-title').textContent = data.title;
    document.getElementById('problem-meta').innerHTML = 
        '<span class="badge ' + badgeClass + '">' + data.difficulty + '</span>' +
        '<span style="color:#64748b">Topic: ' + data.topic + '</span>';
    document.getElementById('problem-desc').textContent = data.description;
    
    document.getElementById('problem-card').style.display = 'block';
    document.getElementById('editor-card').style.display = 'block';
    document.getElementById('code').value = '';
    setFeedback('');
}

async function getHint() {
    const uid = getUserId();
    if (!uid) return;
    if (!currentProblem) { alert("Get a problem first!"); return; }
    
    const code = document.getElementById('code').value;
    setFeedback('<div class="card"><p class="loading">Thinking of a hint based on your past mistakes...</p></div>');
    
    const r = await fetch('/api/hint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: uid, problem: currentProblem, code: code})
    });
    const data = await r.json();
    setFeedback('<div class="card feedback-box feedback-hint"><strong>Hint:</strong> ' + data.hint + '</div>');
}

async function submitSolution() {
    const uid = getUserId();
    if (!uid) return;
    if (!currentProblem) { alert("Get a problem first!"); return; }
    
    const code = document.getElementById('code').value;
    if (!code.trim()) { alert("Write some code first!"); return; }
    
    setFeedback('<div class="card"><p class="loading">Evaluating your solution and saving to memory...</p></div>');
    
    const r = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: uid, topic: currentTopic, problem: currentProblem, code: code})
    });
    const data = await r.json();
    
    const cls = data.correct ? 'feedback-correct' : 'feedback-wrong';
    const icon = data.correct ? '✓ Correct!' : '✗ Not quite right';
    setFeedback('<div class="feedback-box ' + cls + '"><strong>' + icon + '</strong><br><br>' + data.feedback + '</div>');
}

async function getProfile() {
    const uid = getUserId();
    if (!uid) return;
    
    setFeedback('<div class="card"><p class="loading">Loading your learning profile from memory...</p></div>');
    
    const r = await fetch('/api/profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: uid})
    });
    const data = await r.json();
    setFeedback('<div class="card"><h2 style="margin-bottom:12px">Your Learning Profile</h2><div class="feedback-box feedback-profile">' + data.profile + '</div></div>');
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/problem', methods=['POST'])
def problem():
    data = request.json
    result = generate_problem(data['user_id'])
    return jsonify(result)

@app.route('/api/hint', methods=['POST'])
def hint():
    data = request.json
    h = give_hint(data['user_id'], data['problem'], data['code'])
    return jsonify({"hint": h})

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    result = evaluate_solution(data['user_id'], data['topic'], data['problem'], data['code'])
    return jsonify(result)

@app.route('/api/profile', methods=['POST'])
def profile():
    data = request.json
    p = get_learning_profile(data['user_id'])
    return jsonify({"profile": p})

if __name__ == '__main__':
    app.run(debug=True, port=5000)