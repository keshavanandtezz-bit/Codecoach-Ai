import os
from flask import Flask, request, jsonify, render_template_string
from mentor import generate_problem, give_hint, evaluate_solution
from memory import get_learning_profile

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeCoach AI</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0a0a0f;
  --surface: #111118;
  --surface2: #1a1a24;
  --surface3: #22222f;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.12);
  --accent: #7c6dfa;
  --accent2: #a78bfa;
  --accent3: #c4b5fd;
  --green: #10b981;
  --red: #ef4444;
  --amber: #f59e0b;
  --text: #e8e8f0;
  --text2: #9898b0;
  --text3: #5a5a78;
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Syne', sans-serif;
  --radius: 12px;
  --radius2: 16px;
}

html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.6;
  overflow: hidden;
}

/* Layout */
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 0;
  transition: transform 0.3s ease;
  z-index: 10;
}

.sidebar-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.logo-text span {
  color: var(--accent2);
}

.user-input-area {
  display: flex;
  gap: 8px;
  align-items: center;
}

.user-input-area input {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border2);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 8px;
  font-family: var(--sans);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.user-input-area input:focus {
  border-color: var(--accent);
}

.user-input-area input::placeholder { color: var(--text3); }

.btn-icon {
  width: 34px;
  height: 34px;
  background: var(--accent);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: opacity 0.2s, transform 0.1s;
  flex-shrink: 0;
}

.btn-icon:hover { opacity: 0.85; transform: scale(1.05); }

/* Sidebar nav */
.sidebar-nav {
  flex: 1;
  padding: 12px 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-section-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 8px 4px;
  margin-top: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text2);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: var(--surface2);
  color: var(--text);
  border-color: var(--border);
}

.nav-item.active {
  background: rgba(124, 109, 250, 0.15);
  color: var(--accent3);
  border-color: rgba(124, 109, 250, 0.25);
}

.nav-item .nav-icon { font-size: 15px; width: 18px; text-align: center; }

/* Stats bar */
.stats-bar {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 8px;
}

.stat-pill {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 8px;
  text-align: center;
}

.stat-pill .stat-num {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--mono);
  color: var(--accent2);
  display: block;
}

.stat-pill .stat-label {
  font-size: 9px;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Main area */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

/* Top bar */
.topbar {
  height: 56px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
  background: var(--surface);
  flex-shrink: 0;
}

.topbar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  flex: 1;
}

.topbar-title span {
  color: var(--text3);
  font-weight: 400;
}

.btn-sm {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--sans);
  cursor: pointer;
  border: 1px solid var(--border2);
  background: var(--surface2);
  color: var(--text2);
  transition: all 0.15s;
  white-space: nowrap;
}

.btn-sm:hover { background: var(--surface3); color: var(--text); }

.btn-sm.primary {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.btn-sm.primary:hover { opacity: 0.85; }

.btn-sm.success {
  background: var(--green);
  border-color: var(--green);
  color: white;
}

.btn-sm.success:hover { opacity: 0.85; }

/* Tab panels */
.panel {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: none;
  flex-direction: column;
  gap: 16px;
}

.panel.active {
  display: flex;
}

/* Welcome screen */
.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
  gap: 16px;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.welcome h2 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.welcome h2 span { color: var(--accent2); }

.welcome p {
  color: var(--text2);
  max-width: 400px;
  font-size: 14px;
  line-height: 1.7;
}

.welcome-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-lg {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--sans);
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-lg.primary {
  background: var(--accent);
  color: white;
}

.btn-lg.primary:hover { opacity: 0.85; transform: translateY(-1px); }

.btn-lg.secondary {
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border2);
}

.btn-lg.secondary:hover { background: var(--surface3); }

/* Cards */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  padding: 20px;
  transition: border-color 0.2s;
}

.card:hover { border-color: var(--border2); }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.card-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Problem card */
.problem-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.problem-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--mono);
}

.badge-easy { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.badge-medium { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
.badge-hard { background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }

.topic-tag {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  color: var(--text3);
  background: var(--surface2);
  border: 1px solid var(--border);
}

.problem-desc {
  color: var(--text2);
  font-size: 14px;
  line-height: 1.75;
}

/* Code editor */
.editor-wrapper {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border2);
  transition: border-color 0.2s;
}

.editor-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(124,109,250,0.1);
}

.editor-header {
  background: var(--surface2);
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}

.editor-lang {
  font-size: 11px;
  color: var(--text3);
  font-family: var(--mono);
  font-weight: 500;
}

.editor-actions { display: flex; gap: 6px; }

.editor-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-red { background: #ef4444; }
.dot-amber { background: #f59e0b; }
.dot-green { background: #10b981; }

textarea#code {
  width: 100%;
  height: 200px;
  background: #0d0d14;
  border: none;
  color: #c8d3f5;
  padding: 16px;
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.7;
  resize: vertical;
  outline: none;
  tab-size: 4;
}

textarea#code::placeholder { color: var(--text3); }

.action-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

/* Feedback */
.feedback-card {
  border-radius: var(--radius2);
  padding: 18px 20px;
  border: 1px solid;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.feedback-correct {
  background: rgba(16,185,129,0.08);
  border-color: rgba(16,185,129,0.25);
}

.feedback-wrong {
  background: rgba(239,68,68,0.08);
  border-color: rgba(239,68,68,0.25);
}

.feedback-hint {
  background: rgba(124,109,250,0.08);
  border-color: rgba(124,109,250,0.25);
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  font-size: 14px;
}

.feedback-correct .feedback-header { color: #6ee7b7; }
.feedback-wrong .feedback-header { color: #fca5a5; }
.feedback-hint .feedback-header { color: var(--accent3); }

.feedback-body {
  color: var(--text2);
  font-size: 13px;
  line-height: 1.7;
}

/* Profile panel */
.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
}

.profile-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.profile-sub {
  font-size: 12px;
  color: var(--text3);
  margin-top: 2px;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.memory-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  font-size: 13px;
  color: var(--text2);
  line-height: 1.6;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  transition: border-color 0.15s;
  animation: slideUp 0.3s ease;
}

.memory-item:hover { border-color: var(--border2); }

.memory-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  margin-top: 6px;
}

/* Loading state */
.loading-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  color: var(--text2);
  font-size: 13px;
}

/* Topic chips */
.topic-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.topic-chip {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border2);
  background: var(--surface2);
  color: var(--text2);
  transition: all 0.15s;
  font-family: var(--sans);
}

.topic-chip:hover, .topic-chip.selected {
  background: rgba(124,109,250,0.2);
  border-color: var(--accent);
  color: var(--accent3);
}

/* Difficulty selector */
.diff-btns {
  display: flex;
  gap: 6px;
}

.diff-btn {
  flex: 1;
  padding: 7px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--sans);
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--surface2);
  color: var(--text3);
  transition: all 0.15s;
}

.diff-btn:hover { color: var(--text); border-color: var(--border2); }
.diff-btn.active-easy { background: rgba(16,185,129,0.15); color: #6ee7b7; border-color: rgba(16,185,129,0.4); }
.diff-btn.active-medium { background: rgba(245,158,11,0.15); color: #fcd34d; border-color: rgba(245,158,11,0.4); }
.diff-btn.active-hard { background: rgba(239,68,68,0.15); color: #fca5a5; border-color: rgba(239,68,68,0.4); }

/* History panel */
.history-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.15s;
  cursor: pointer;
}

.history-item:hover { border-color: var(--border2); }

.history-status {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.status-correct { background: rgba(16,185,129,0.15); }
.status-wrong { background: rgba(239,68,68,0.15); }

.history-info { flex: 1; }
.history-title { font-size: 13px; font-weight: 600; color: var(--text); }
.history-meta { font-size: 11px; color: var(--text3); margin-top: 2px; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text3);
}

.empty-state .empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-state p { font-size: 13px; line-height: 1.6; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--border2); }

/* Mobile */
@media (max-width: 768px) {
  .sidebar { position: fixed; left: -260px; height: 100%; }
  .sidebar.open { transform: translateX(260px); }
  .main { width: 100%; }
}
</style>
</head>
<body>

<div class="layout">

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">Code<span>Coach</span></div>
      </div>
      <div class="user-input-area">
        <input type="text" id="user-id" placeholder="Your name..." autocomplete="off">
        <button class="btn-icon" onclick="setUser()" title="Set user">→</button>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-section-title">Practice</div>
      <div class="nav-item active" onclick="showPanel('practice')">
        <span class="nav-icon">🎯</span> New Problem
      </div>
      <div class="nav-item" onclick="showPanel('history')">
        <span class="nav-icon">📋</span> My History
      </div>

      <div class="nav-section-title">Insights</div>
      <div class="nav-item" onclick="showPanel('profile')">
        <span class="nav-icon">🧠</span> Learning Profile
      </div>
      <div class="nav-item" onclick="showPanel('stats')">
        <span class="nav-icon">📊</span> My Stats
      </div>

      <div class="nav-section-title">Settings</div>
      <div class="nav-item" onclick="showPanel('settings')">
        <span class="nav-icon">⚙️</span> Preferences
      </div>
    </nav>

    <div class="stats-bar">
      <div class="stat-pill">
        <span class="stat-num" id="stat-solved">0</span>
        <span class="stat-label">Solved</span>
      </div>
      <div class="stat-pill">
        <span class="stat-num" id="stat-streak">0</span>
        <span class="stat-label">Streak</span>
      </div>
      <div class="stat-pill">
        <span class="stat-num" id="stat-topics">0</span>
        <span class="stat-label">Topics</span>
      </div>
    </div>
  </aside>

  <!-- Main content -->
  <main class="main">

    <!-- Top bar -->
    <div class="topbar">
      <div class="topbar-title" id="topbar-title">
        Welcome to CodeCoach <span>— Enter your name to begin</span>
      </div>
      <button class="btn-sm" onclick="showPanel('profile')">🧠 My Profile</button>
      <button class="btn-sm primary" onclick="getProblem()">⚡ New Problem</button>
    </div>

    <!-- PRACTICE PANEL -->
    <div class="panel active" id="panel-practice">

      <!-- Welcome state (shown before user starts) -->
      <div class="welcome" id="welcome-state">
        <div class="welcome-icon">⚡</div>
        <h2>Ready to level up your <span>coding?</span></h2>
        <p>CodeCoach remembers every mistake you make and gets smarter with every session. Enter your name on the left to get started.</p>
        <div class="welcome-actions">
          <button class="btn-lg primary" onclick="getProblem()">Get My First Problem</button>
          <button class="btn-lg secondary" onclick="showPanel('profile')">View Profile</button>
        </div>
      </div>

      <!-- Active practice (shown after problem loads) -->
      <div id="practice-state" style="display:none; flex-direction:column; gap:16px;">

        <!-- Controls row -->
        <div class="card" style="padding:16px;">
          <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
              <div style="font-size:11px; color:var(--text3); margin-bottom:6px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Topic</div>
              <div class="topic-chips" id="topic-chips">
                <div class="topic-chip selected" onclick="selectTopic(this, 'any')">Any</div>
                <div class="topic-chip" onclick="selectTopic(this, 'arrays')">Arrays</div>
                <div class="topic-chip" onclick="selectTopic(this, 'loops')">Loops</div>
                <div class="topic-chip" onclick="selectTopic(this, 'recursion')">Recursion</div>
                <div class="topic-chip" onclick="selectTopic(this, 'strings')">Strings</div>
                <div class="topic-chip" onclick="selectTopic(this, 'functions')">Functions</div>
                <div class="topic-chip" onclick="selectTopic(this, 'dictionaries')">Dicts</div>
              </div>
            </div>
            <div style="min-width:160px;">
              <div style="font-size:11px; color:var(--text3); margin-bottom:6px; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Difficulty</div>
              <div class="diff-btns">
                <button class="diff-btn active-easy" onclick="selectDiff(this, 'easy')" id="diff-easy">Easy</button>
                <button class="diff-btn" onclick="selectDiff(this, 'medium')" id="diff-medium">Med</button>
                <button class="diff-btn" onclick="selectDiff(this, 'hard')" id="diff-hard">Hard</button>
              </div>
            </div>
            <button class="btn-sm primary" onclick="getProblem()" style="margin-top:18px;">⚡ New Problem</button>
          </div>
        </div>

        <!-- Loading state -->
        <div class="loading-card" id="loading-problem" style="display:none;">
          <div class="spinner"></div>
          <div class="loading-text">Generating your personalized problem based on your history...</div>
        </div>

        <!-- Problem card -->
        <div class="card" id="problem-card" style="display:none;">
          <div class="card-header">
            <span class="card-title">Your Problem</span>
            <div style="display:flex; gap:6px;">
              <button class="btn-sm" onclick="getProblem()">↻ New</button>
            </div>
          </div>
          <div class="problem-title" id="problem-title"></div>
          <div class="problem-meta" id="problem-meta"></div>
          <div class="problem-desc" id="problem-desc"></div>
        </div>

        <!-- Code editor -->
        <div class="card" id="editor-card" style="display:none;">
          <div class="card-header">
            <span class="card-title">Your Solution</span>
          </div>
          <div class="editor-wrapper">
            <div class="editor-header">
              <div style="display:flex; gap:5px;">
                <div class="editor-dot dot-red"></div>
                <div class="editor-dot dot-amber"></div>
                <div class="editor-dot dot-green"></div>
              </div>
              <span class="editor-lang">python</span>
              <button class="btn-sm" onclick="clearCode()" style="padding:3px 8px; font-size:11px;">Clear</button>
            </div>
            <textarea id="code" spellcheck="false" placeholder="# Write your Python solution here...&#10;&#10;def solution():&#10;    pass"></textarea>
          </div>
          <div class="action-row">
            <button class="btn-sm" onclick="getHint()" style="gap:5px; display:flex; align-items:center;">
              💡 Get Hint
            </button>
            <button class="btn-sm success" onclick="submitSolution()" style="gap:5px; display:flex; align-items:center;">
              ✓ Submit Solution
            </button>
          </div>
        </div>

        <!-- Feedback area -->
        <div id="feedback-area"></div>

      </div>
    </div>

    <!-- PROFILE PANEL -->
    <div class="panel" id="panel-profile">
      <div id="profile-content">
        <div class="empty-state">
          <div class="empty-icon">🧠</div>
          <p>Enter your name and click "Load Profile" to see your learning history.</p>
          <button class="btn-lg primary" style="margin-top:16px;" onclick="loadProfile()">Load My Profile</button>
        </div>
      </div>
    </div>

    <!-- HISTORY PANEL -->
    <div class="panel" id="panel-history">
      <div id="history-content">
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <p>Your solved problems will appear here. Start practicing to build your history!</p>
        </div>
      </div>
    </div>

    <!-- STATS PANEL -->
    <div class="panel" id="panel-stats">
      <div class="card">
        <div class="card-header"><span class="card-title">Your Progress</span></div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin-top:4px;">
          <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center;">
            <div style="font-size:28px; font-weight:800; font-family:var(--mono); color:var(--accent2);" id="big-solved">0</div>
            <div style="font-size:11px; color:var(--text3); margin-top:4px; text-transform:uppercase; letter-spacing:1px;">Problems Solved</div>
          </div>
          <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center;">
            <div style="font-size:28px; font-weight:800; font-family:var(--mono); color:var(--green);" id="big-streak">0</div>
            <div style="font-size:11px; color:var(--text3); margin-top:4px; text-transform:uppercase; letter-spacing:1px;">Current Streak</div>
          </div>
          <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center;">
            <div style="font-size:28px; font-weight:800; font-family:var(--mono); color:var(--amber);" id="big-topics">0</div>
            <div style="font-size:11px; color:var(--text3); margin-top:4px; text-transform:uppercase; letter-spacing:1px;">Topics Practiced</div>
          </div>
          <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center;">
            <div style="font-size:28px; font-weight:800; font-family:var(--mono); color:var(--red);" id="big-wrong">0</div>
            <div style="font-size:11px; color:var(--text3); margin-top:4px; text-transform:uppercase; letter-spacing:1px;">Need Review</div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><span class="card-title">Topics Practiced</span></div>
        <div id="topics-practiced" style="display:flex; flex-wrap:wrap; gap:6px; padding-top:4px;">
          <div style="color:var(--text3); font-size:13px;">Solve problems to see your topic breakdown.</div>
        </div>
      </div>
    </div>

    <!-- SETTINGS PANEL -->
    <div class="panel" id="panel-settings">
      <div class="card">
        <div class="card-header"><span class="card-title">Preferences</span></div>
        <div style="display:flex; flex-direction:column; gap:16px; padding-top:4px;">
          <div>
            <div style="font-size:13px; font-weight:600; color:var(--text); margin-bottom:6px;">Default Difficulty</div>
            <div class="diff-btns" style="max-width:240px;">
              <button class="diff-btn active-easy" onclick="selectDiff(this,'easy')" id="pref-easy">Easy</button>
              <button class="diff-btn" onclick="selectDiff(this,'medium')" id="pref-med">Medium</button>
              <button class="diff-btn" onclick="selectDiff(this,'hard')" id="pref-hard">Hard</button>
            </div>
          </div>
          <div>
            <div style="font-size:13px; font-weight:600; color:var(--text); margin-bottom:4px;">Hindsight Memory</div>
            <div style="font-size:12px; color:var(--text3); line-height:1.6;">
              CodeCoach uses Hindsight memory to remember your mistakes and personalize every problem.
              Your memory bank: <span style="color:var(--accent2); font-family:var(--mono);">codecoach</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </main>
</div>

<script>
// State
let currentProblem = "";
let currentTopic = "";
let currentDiff = "easy";
let selectedTopicFilter = "any";
let sessionSolved = 0;
let sessionStreak = 0;
let sessionTopics = new Set();
let sessionWrong = 0;
let history = [];

function getUserId() {
  const uid = document.getElementById('user-id').value.trim();
  if (!uid) {
    alert("Please enter your name on the left sidebar first!");
    return null;
  }
  return uid;
}

function setUser() {
  const uid = document.getElementById('user-id').value.trim();
  if (!uid) { alert("Please type your name first!"); return; }
  document.getElementById('topbar-title').innerHTML =
    'Logged in as <span style="color:var(--accent2)">' + uid + '</span>';
  document.getElementById('welcome-state').style.display = 'none';
  document.getElementById('practice-state').style.display = 'flex';
  showPanel('practice');
}

function showPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    if (item.textContent.toLowerCase().includes(name) ||
        (name === 'practice' && item.textContent.includes('New Problem')) ||
        (name === 'history' && item.textContent.includes('History')) ||
        (name === 'profile' && item.textContent.includes('Learning')) ||
        (name === 'stats' && item.textContent.includes('Stats')) ||
        (name === 'settings' && item.textContent.includes('Settings'))) {
      item.classList.add('active');
    }
  });
}

function selectTopic(el, topic) {
  document.querySelectorAll('.topic-chip').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  selectedTopicFilter = topic;
}

function selectDiff(el, diff) {
  const parent = el.parentElement;
  parent.querySelectorAll('.diff-btn').forEach(b => {
    b.classList.remove('active-easy', 'active-medium', 'active-hard');
  });
  el.classList.add('active-' + diff);
  currentDiff = diff;
}

function clearCode() {
  document.getElementById('code').value = '';
  document.getElementById('feedback-area').innerHTML = '';
}

function setFeedback(html) {
  document.getElementById('feedback-area').innerHTML = html;
  document.getElementById('feedback-area').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function updateStats() {
  document.getElementById('stat-solved').textContent = sessionSolved;
  document.getElementById('stat-streak').textContent = sessionStreak;
  document.getElementById('stat-topics').textContent = sessionTopics.size;
  document.getElementById('big-solved').textContent = sessionSolved;
  document.getElementById('big-streak').textContent = sessionStreak;
  document.getElementById('big-topics').textContent = sessionTopics.size;
  document.getElementById('big-wrong').textContent = sessionWrong;

  if (sessionTopics.size > 0) {
    const chips = Array.from(sessionTopics).map(t =>
      `<span class="topic-chip selected" style="cursor:default;">${t}</span>`
    ).join('');
    document.getElementById('topics-practiced').innerHTML = chips;
  }
}

async function getProblem() {
  const uid = getUserId();
  if (!uid) return;

  document.getElementById('welcome-state').style.display = 'none';
  document.getElementById('practice-state').style.display = 'flex';
  document.getElementById('loading-problem').style.display = 'flex';
  document.getElementById('problem-card').style.display = 'none';
  document.getElementById('editor-card').style.display = 'none';
  document.getElementById('feedback-area').innerHTML = '';
  showPanel('practice');

  const topicHint = selectedTopicFilter !== 'any' ? selectedTopicFilter : null;

  const r = await fetch('/api/problem', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: uid, topic: topicHint, difficulty: currentDiff })
  });
  const data = await r.json();

  currentProblem = data.description;
  currentTopic = data.topic;

  if (data.topic) sessionTopics.add(data.topic);
  updateStats();

  const diff = (data.difficulty || 'easy').toLowerCase();
  document.getElementById('problem-title').textContent = data.title;
  document.getElementById('problem-meta').innerHTML =
    `<span class="badge badge-${diff}">${diff}</span>
     <span class="topic-tag">${data.topic}</span>`;
  document.getElementById('problem-desc').textContent = data.description;

  document.getElementById('loading-problem').style.display = 'none';
  document.getElementById('problem-card').style.display = 'block';
  document.getElementById('editor-card').style.display = 'block';
  document.getElementById('code').value = '';
}

async function getHint() {
  const uid = getUserId();
  if (!uid) return;
  if (!currentProblem) { alert("Get a problem first!"); return; }

  const code = document.getElementById('code').value;
  setFeedback(`<div class="loading-card"><div class="spinner"></div>
    <div class="loading-text">Finding a hint based on your past mistakes...</div></div>`);

  const r = await fetch('/api/hint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: uid, problem: currentProblem, code })
  });
  const data = await r.json();

  setFeedback(`<div class="feedback-card feedback-hint">
    <div class="feedback-header">💡 Hint</div>
    <div class="feedback-body">${data.hint}</div>
  </div>`);
}

async function submitSolution() {
  const uid = getUserId();
  if (!uid) return;
  if (!currentProblem) { alert("Get a problem first!"); return; }

  const code = document.getElementById('code').value;
  if (!code.trim()) { alert("Write some code first!"); return; }

  setFeedback(`<div class="loading-card"><div class="spinner"></div>
    <div class="loading-text">Evaluating your solution and saving to memory...</div></div>`);

  const r = await fetch('/api/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: uid, topic: currentTopic, problem: currentProblem, code })
  });
  const data = await r.json();

  if (data.correct) {
    sessionSolved++;
    sessionStreak++;
  } else {
    sessionStreak = 0;
    sessionWrong++;
  }
  updateStats();

  // Add to history
  history.unshift({
    title: document.getElementById('problem-title').textContent,
    topic: currentTopic,
    correct: data.correct,
    time: new Date().toLocaleTimeString()
  });
  renderHistory();

  const cls = data.correct ? 'feedback-correct' : 'feedback-wrong';
  const icon = data.correct ? '✓ Correct!' : '✗ Not quite right';
  const iconEmoji = data.correct ? '✅' : '❌';

  setFeedback(`<div class="feedback-card ${cls}">
    <div class="feedback-header">${iconEmoji} ${icon}</div>
    <div class="feedback-body">${data.feedback}</div>
    ${data.correct ? `<button class="btn-sm primary" onclick="getProblem()" style="margin-top:12px;">Next Problem →</button>` : ''}
  </div>`);
}

function renderHistory() {
  const container = document.getElementById('history-content');
  if (history.length === 0) {
    container.innerHTML = `<div class="empty-state">
      <div class="empty-icon">📋</div>
      <p>Your solved problems will appear here.</p>
    </div>`;
    return;
  }
  container.innerHTML = `<div style="display:flex; flex-direction:column; gap:8px;">` +
    history.map(h => `
      <div class="history-item">
        <div class="history-status ${h.correct ? 'status-correct' : 'status-wrong'}">
          ${h.correct ? '✓' : '✗'}
        </div>
        <div class="history-info">
          <div class="history-title">${h.title}</div>
          <div class="history-meta">${h.topic} · ${h.time}</div>
        </div>
        <span class="badge ${h.correct ? 'badge-easy' : 'badge-hard'}">${h.correct ? 'Solved' : 'Attempted'}</span>
      </div>
    `).join('') + `</div>`;
}

async function loadProfile() {
  const uid = getUserId();
  if (!uid) return;

  document.getElementById('profile-content').innerHTML = `
    <div class="loading-card">
      <div class="spinner"></div>
      <div class="loading-text">Loading ${uid}'s learning profile from Hindsight memory...</div>
    </div>`;

  const r = await fetch('/api/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: uid })
  });
  const data = await r.json();

  const initials = uid.charAt(0).toUpperCase();
  const memories = data.profile.split('\\n').filter(m => m.trim());

  let memoriesHTML = '';
  if (memories.length === 0 || data.profile.includes('No learning history')) {
    memoriesHTML = `<div class="empty-state">
      <div class="empty-icon">🌱</div>
      <p>No history yet for <strong>${uid}</strong>. Solve some problems to build your profile!</p>
    </div>`;
  } else {
    memoriesHTML = `<div class="memory-list">` +
      memories.map(m => `
        <div class="memory-item">
          <div class="memory-dot"></div>
          <div>${m.replace('•', '').trim()}</div>
        </div>
      `).join('') + `</div>`;
  }

  document.getElementById('profile-content').innerHTML = `
    <div class="profile-header">
      <div class="profile-avatar">${initials}</div>
      <div>
        <div class="profile-name">${uid}</div>
        <div class="profile-sub">Learning profile powered by Hindsight memory</div>
      </div>
      <button class="btn-sm primary" onclick="loadProfile()" style="margin-left:auto;">↻ Refresh</button>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Memory Bank — ${memories.length} memories</span>
      </div>
      ${memoriesHTML}
    </div>`;
}

// Auto-load profile when switching to profile panel
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
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'easy')
    result = generate_problem(data['user_id'], topic=topic, difficulty=difficulty)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)