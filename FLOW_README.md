# ✨ Flow - Intelligent Task Management

**A world-class task management application with beautiful UI/UX and smart features**

Flow is designed by top UI/UX principles to make productivity effortless. With intelligent prioritization, energy-based scheduling, and a stunning interface, Flow helps you focus on what matters most.

![Flow](https://img.shields.io/badge/Status-Production%20Ready-success)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)

---

## 🎯 Philosophy

> **"Show what matters, hide what doesn't. Make productivity effortless."**

Flow isn't just another task manager. It's an intelligent productivity companion that:
- **Learns** from your behavior
- **Adapts** to your energy levels
- **Focuses** your attention on high-impact work
- **Celebrates** your progress
- **Delights** with every interaction

---

## ✨ Features

### 🧠 Smart Intelligence

- **Smart Prioritization** - AI-weighted task sorting that considers priority, due dates, and time estimates
- **Energy Matching** - Match tasks to your energy levels (High/Medium/Low)
- **Natural Language Input** - Type "Call mom tomorrow at 3pm" and Flow understands
- **Contextual Sorting** - Smart View automatically shows what needs attention now

### 🎨 Beautiful Design

- **Modern UI** - Clean, minimal interface with smooth animations
- **Color Psychology** - Carefully chosen colors that reduce stress and increase focus
- **Micro-interactions** - Delightful animations and feedback on every action
- **Responsive** - Looks stunning on desktop, tablet, and mobile
- **Dark Mode** - Easy on the eyes (coming soon)

### ⚡ Focus Features

- **Focus Mode** - Distraction-free view of a single task
- **Pomodoro Timer** - Built-in 25-minute focus sessions
- **Quick Capture** - Add tasks in seconds
- **Keyboard Shortcuts** - Never touch your mouse

### 📊 Analytics & Insights

- **Completion Rate** - Track your productivity over time
- **Streak Tracking** - Build consistency with daily streaks
- **Energy Insights** - Learn your peak productivity times
- **Time Estimates** - See how long tasks really take

### 🎯 Task Management

- **Priority Levels** - Critical, High, Medium, Low
- **Categories** - Work, Personal, Health, Learning, Creative, Social
- **Energy Levels** - High, Medium, Low energy tasks
- **Due Dates & Times** - Never miss a deadline
- **Time Estimates** - Plan your day accurately
- **Search & Filter** - Find tasks instantly

### 📱 Mobile First

- **PWA Support** - Install on your phone like a native app
- **Touch Optimized** - Perfect touch targets (44px minimum)
- **Offline Support** - Works without internet
- **Fast & Smooth** - 60fps animations everywhere
- **Responsive Grid** - Adapts to any screen size

---

## 🚀 Quick Start

### Run Locally

```bash
# Option 1: Use the launcher script
./run_flow.sh

# Option 2: Run directly
python flow_app.py
```

The app will be available at:
- **Local:** http://localhost:8052
- **Network:** http://YOUR_IP:8052

### Install on Phone

1. Open the URL on your phone's browser
2. **iPhone (Safari):** Tap Share → "Add to Home Screen"
3. **Android (Chrome):** Tap Menu → "Install app"

---

## 🎨 Design System

### Color Palette

```css
Primary:    #6366f1  /* Indigo - Focus & Trust */
Secondary:  #8b5cf6  /* Purple - Creativity */
Success:    #10b981  /* Green - Achievement */
Warning:    #f59e0b  /* Amber - Attention */
Danger:     #ef4444  /* Red - Urgency */
Info:       #06b6d4  /* Cyan - Information */
```

### Typography

- **Font Family:** Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI'
- **Weights:** 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extrabold)
- **Sizes:** Fluid typography that scales with viewport

### Spacing

- **Scale:** 4px base unit (0.25rem)
- **Rhythm:** Consistent vertical rhythm throughout

---

## 💡 Usage Guide

### Adding Tasks

**Quick Add (Natural Language):**
```
"Call mom tomorrow at 3pm"
"Finish report by Friday urgent"
"Exercise today at 7am"
```

**Structured Add:**
1. Enter task description
2. Set priority (1-4)
3. Choose category
4. Select energy level
5. Estimate time
6. Click "Add Task"

### Smart View

The Smart View automatically sorts tasks by:
1. **Overdue tasks** - Show first
2. **Due today** - High priority
3. **High priority** - Important work
4. **Tomorrow's tasks** - Plan ahead
5. **Everything else** - Backlog

### Focus Mode

1. Click the ⚡ Focus Mode button
2. Your top priority task appears fullscreen
3. Start the Pomodoro timer
4. Work without distractions for 25 minutes
5. Take a break when timer completes

### Energy-Based Scheduling

Match tasks to your energy:
- **⚡ High Energy (Morning):** Deep work, creative tasks, important decisions
- **🔆 Medium Energy (Midday):** Meetings, communication, routine work
- **🌙 Low Energy (Evening):** Planning, organizing, simple tasks

---

## 🎯 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Q` | Quick add task |
| `F` | Focus mode |
| `/` | Search tasks |
| `1-4` | Set priority |
| `Space` | Start/pause Pomodoro |
| `Esc` | Exit focus mode |
| `⌘ + K` | Command palette |

*(Coming in v1.1)*

---

## 📊 Understanding Analytics

### Completion Rate
Shows percentage of tasks completed vs created. Aim for 80%+ for optimal productivity.

### Streak Counter
Consecutive days with at least one completed task. Builds consistency and momentum.

### Active Tasks
Current number of incomplete tasks. Keep under 10 for optimal focus.

### Today's Completed
Tasks completed today. Celebrate small wins!

---

## 🏗️ Architecture

### Tech Stack

- **Framework:** Dash (Python)
- **UI Components:** Dash Bootstrap Components
- **Icons:** Font Awesome 6
- **Styling:** Custom CSS with animations
- **State:** Client-side with dcc.Store
- **PWA:** Service Worker + Manifest

### Data Model

```python
task = {
    "id": "uuid",
    "description": "Task text",
    "priority": 1-4,
    "category": "work|personal|health|learning|creative|social",
    "energy": "high|medium|low",
    "time_estimate": 30,  # minutes
    "due_date": "2025-01-23",
    "due_time": "15:00",
    "created_at": "ISO timestamp",
    "completed": false,
    "completed_at": null,
    "time_spent": 0
}
```

### Smart Scoring Algorithm

```python
score = priority_weight  # Base: 25-100
if overdue: score += 100
if due_today: score += 50
if due_tomorrow: score += 30
if has_time_estimate: score += 10
```

---

## 🎨 Customization

### Adding Custom Categories

Edit `flow_app.py`:

```python
CATEGORIES = {
    "custom": {
        "name": "Custom",
        "icon": "🎯",
        "color": "#ff6b6b"
    }
}
```

### Changing Colors

Edit `assets/flow-style.css`:

```css
:root {
    --primary: #your-color;
}
```

### Custom Energy Levels

Edit `flow_app.py`:

```python
ENERGY_LEVELS = {
    "peak": {
        "name": "Peak Performance",
        "icon": "🚀",
        "color": "#your-color"
    }
}
```

---

## 📱 Mobile Guide

### iOS Installation

1. Open Safari (must use Safari, not Chrome)
2. Navigate to your Flow URL
3. Tap the Share button (bottom center)
4. Scroll and tap "Add to Home Screen"
5. Name it "Flow" and tap Add
6. App appears on home screen like a native app!

### Android Installation

1. Open Chrome
2. Navigate to your Flow URL
3. Tap the menu (three dots)
4. Tap "Install app" or "Add to Home screen"
5. Follow prompts
6. App installed!

### Offline Usage

After first load, Flow caches automatically and works offline. Your tasks are stored locally in your browser.

---

## 🚀 Deployment

### Google Cloud Run

```bash
gcloud run deploy flow \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Render.com

1. Sign up at render.com
2. New Web Service → Connect GitHub
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn flow_app:server -w 1 --threads 8 -b 0.0.0.0:$PORT`

### Railway.app

1. Sign up at railway.app
2. New Project → Deploy from GitHub
3. Auto-detects and deploys!

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "flow_app:server", "-w", "1", "--threads", "8", "-b", "0.0.0.0:8052"]
```

---

## 🎯 Best Practices

### Daily Workflow

**Morning (High Energy):**
1. Review Smart View
2. Start with highest-priority task
3. Use Pomodoro timer for deep work
4. Take breaks between sessions

**Midday (Medium Energy):**
1. Handle meetings and communication
2. Complete medium-priority tasks
3. Process quick wins

**Evening (Low Energy):**
1. Plan tomorrow's tasks
2. Clean up completed tasks
3. Review analytics
4. Celebrate progress

### Task Writing Tips

**Good Tasks:**
- "Draft Q1 report outline - 45min"
- "Call dentist to schedule appointment - 10min"
- "Review and merge PR #123 - 30min"

**Avoid:**
- "Work on project" (too vague)
- "Do stuff" (no context)
- "Everything" (not actionable)

### Priority Guidelines

- **Critical (1):** Will cause problems if not done today
- **High (2):** Important, due soon, or blocks others
- **Medium (3):** Should be done this week
- **Low (4):** Nice to have, no urgency

---

## 🐛 Troubleshooting

### App Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Try running directly
python flow_app.py
```

### Tasks Not Saving

Tasks are stored in browser localStorage. Check:
- Cookies enabled
- Not in Incognito/Private mode
- Browser storage not full
- JavaScript enabled

### PWA Won't Install

- Must use HTTPS (or localhost)
- Safari on iOS only (not Chrome)
- Chrome on Android (any version)
- Clear browser cache and try again

### Slow Performance

- Close other browser tabs
- Clear browser cache
- Check for browser extensions blocking scripts
- Update browser to latest version

---

## 🔮 Roadmap

### v1.1 - Smart Features
- [ ] Task dependencies ("Do X before Y")
- [ ] Recurring tasks
- [ ] Task templates
- [ ] Batch operations
- [ ] Keyboard shortcuts

### v1.2 - Collaboration
- [ ] Share tasks with others
- [ ] Team workspaces
- [ ] Comments on tasks
- [ ] Activity feed

### v1.3 - Intelligence
- [ ] AI task suggestions
- [ ] Automatic categorization
- [ ] Smart due date predictions
- [ ] Productivity insights with ML

### v1.4 - Integrations
- [ ] Calendar sync (Google, Apple)
- [ ] Email integration
- [ ] Slack notifications
- [ ] GitHub issues sync
- [ ] API for developers

### v2.0 - Platform
- [ ] Native iOS app
- [ ] Native Android app
- [ ] Desktop apps (Mac, Windows, Linux)
- [ ] Browser extensions
- [ ] Apple Watch & Android Wear

---

## 🤝 Contributing

Flow is open source and welcomes contributions!

### Development Setup

```bash
git clone https://github.com/yourusername/flow
cd flow
pip install -r requirements.txt
python flow_app.py
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

---

## 📄 License

MIT License - feel free to use Flow for personal or commercial projects!

---

## 💬 Support

Need help? Have suggestions?

- 📧 Email: support@flowapp.io
- 🐛 Issues: GitHub Issues
- 💬 Discord: Coming soon
- 🐦 Twitter: @flowapp

---

## 🙏 Acknowledgments

Flow is built with love using:
- Dash by Plotly
- Bootstrap
- Font Awesome
- Inter font family

Inspired by the best task managers:
- Todoist
- Things 3
- TickTick
- Any.do

---

## ⭐ Show Your Support

If you love Flow, please:
- ⭐ Star this repo
- 🐦 Share on social media
- 📝 Write a review
- 🤝 Contribute code
- ☕ Buy me a coffee

---

**Made with ✨ and ❤️ for productive people everywhere**

Flow - Where productivity meets beauty.
