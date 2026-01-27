"""
Flow - Intelligent Task Management Application
Production-ready version optimized for Render deployment
Beautiful UI/UX with smart features and mobile-first design
WITH CLOUD SYNC via Supabase
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import uuid
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase setup (optional - falls back to localStorage if not configured)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USE_CLOUD_SYNC = bool(SUPABASE_URL and SUPABASE_KEY)

print("\n" + "="*60)
print("🔍 CLOUD SYNC DIAGNOSTIC")
print("="*60)
print(f"SUPABASE_URL exists: {bool(SUPABASE_URL)}")
print(f"SUPABASE_KEY exists: {bool(SUPABASE_KEY)}")
print(f"USE_CLOUD_SYNC: {USE_CLOUD_SYNC}")
if SUPABASE_URL:
    print(f"SUPABASE_URL value: {SUPABASE_URL[:30]}...")
if SUPABASE_KEY:
    print(f"SUPABASE_KEY value: {SUPABASE_KEY[:20]}...")
print("="*60 + "\n")

if USE_CLOUD_SYNC:
    try:
        from supabase import create_client, Client
        import supabase_db
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cloud sync enabled with Supabase")
        print(f"✅ Supabase client created successfully")
        # Test connection
        try:
            test_result = supabase.table('tasks').select('count', count='exact').limit(0).execute()
            print(f"✅ Successfully connected to Supabase database!")
        except Exception as test_e:
            print(f"⚠️  Supabase connection test failed: {test_e}")
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e}")
        print("📦 Falling back to localStorage")
        USE_CLOUD_SYNC = False
else:
    print("📦 Using localStorage (set SUPABASE_URL and SUPABASE_KEY for cloud sync)")

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "theme-color", "content": "#6366f1"}
    ]
)

app.title = "Flow - Task Management"
server = app.server

# Categories with beautiful colors
CATEGORIES = {
    "work": {"name": "Work", "icon": "💼", "color": "#6366f1"},
    "personal": {"name": "Personal", "icon": "🏠", "color": "#8b5cf6"},
    "health": {"name": "Health", "icon": "❤️", "color": "#ec4899"},
    "learning": {"name": "Learning", "icon": "📚", "color": "#14b8a6"},
    "creative": {"name": "Creative", "icon": "🎨", "color": "#f59e0b"},
    "social": {"name": "Social", "icon": "👥", "color": "#06b6d4"}
}

# Priority levels
PRIORITIES = {
    1: {"name": "Critical", "color": "#ef4444"},
    2: {"name": "High", "color": "#f59e0b"},
    3: {"name": "Medium", "color": "#3b82f6"},
    4: {"name": "Low", "color": "#10b981"}
}

# Inspirational quotes by category
QUOTES = {
    "work": [
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "avatar": "SJ", "color": "#007aff"},
        {"text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs", "avatar": "SJ", "color": "#007aff"},
        {"text": "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work.", "author": "Steve Jobs", "avatar": "SJ", "color": "#007aff"},
        {"text": "Success is a lousy teacher. It seduces smart people into thinking they can't lose.", "author": "Bill Gates", "avatar": "BG", "color": "#00a4ef"},
        {"text": "When something is important enough, you do it even if the odds are not in your favor.", "author": "Elon Musk", "avatar": "EM", "color": "#e62117"},
        {"text": "I think it's very important to have a feedback loop, where you're constantly thinking about what you've done and how you could be doing it better.", "author": "Elon Musk", "avatar": "EM", "color": "#e62117"},
        {"text": "The best way to predict the future is to invent it.", "author": "Alan Kay", "avatar": "AK", "color": "#8b5cf6"},
        {"text": "Code is like humor. When you have to explain it, it's bad.", "author": "Cory House", "avatar": "CH", "color": "#10b981"},
    ],
    "personal": [
        {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins", "avatar": "TR", "color": "#f59e0b"},
        {"text": "Your time is limited, don't waste it living someone else's life.", "author": "Steve Jobs", "avatar": "SJ", "color": "#007aff"},
        {"text": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde", "avatar": "OW", "color": "#8b5cf6"},
        {"text": "The unexamined life is not worth living.", "author": "Socrates", "avatar": "SO", "color": "#3b82f6"},
        {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "avatar": "JL", "color": "#ef4444"},
    ],
    "health": [
        {"text": "Take care of your body. It's the only place you have to live.", "author": "Jim Rohn", "avatar": "JR", "color": "#ec4899"},
        {"text": "The greatest wealth is health.", "author": "Virgil", "avatar": "VI", "color": "#ec4899"},
        {"text": "To keep the body in good health is a duty... otherwise we shall not be able to keep our mind strong and clear.", "author": "Buddha", "avatar": "BU", "color": "#f59e0b"},
        {"text": "Health is not valued till sickness comes.", "author": "Thomas Fuller", "avatar": "TF", "color": "#ec4899"},
        {"text": "The first wealth is health.", "author": "Ralph Waldo Emerson", "avatar": "RWE", "color": "#10b981"},
    ],
    "learning": [
        {"text": "The important thing is not to stop questioning. Curiosity has its own reason for existing.", "author": "Albert Einstein", "avatar": "AE", "color": "#6366f1"},
        {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Mahatma Gandhi", "avatar": "MG", "color": "#f59e0b"},
        {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela", "avatar": "NM", "color": "#14b8a6"},
        {"text": "The beautiful thing about learning is that no one can take it away from you.", "author": "B.B. King", "avatar": "BBK", "color": "#8b5cf6"},
        {"text": "Study hard what interests you the most in the most undisciplined, irreverent and original manner possible.", "author": "Richard Feynman", "avatar": "RF", "color": "#3b82f6"},
        {"text": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin", "avatar": "BF", "color": "#10b981"},
    ],
    "creative": [
        {"text": "Creativity is intelligence having fun.", "author": "Albert Einstein", "avatar": "AE", "color": "#6366f1"},
        {"text": "The desire to create is one of the deepest yearnings of the human soul.", "author": "Dieter F. Uchtdorf", "avatar": "DU", "color": "#f59e0b"},
        {"text": "Creativity takes courage.", "author": "Henri Matisse", "avatar": "HM", "color": "#ef4444"},
        {"text": "Don't think. Thinking is the enemy of creativity.", "author": "Ray Bradbury", "avatar": "RB", "color": "#8b5cf6"},
        {"text": "Every artist was first an amateur.", "author": "Ralph Waldo Emerson", "avatar": "RWE", "color": "#10b981"},
        {"text": "Imagination is more important than knowledge.", "author": "Albert Einstein", "avatar": "AE", "color": "#6366f1"},
    ],
    "social": [
        {"text": "Alone we can do so little; together we can do so much.", "author": "Helen Keller", "avatar": "HK", "color": "#06b6d4"},
        {"text": "Coming together is a beginning; keeping together is progress; working together is success.", "author": "Henry Ford", "avatar": "HF", "color": "#3b82f6"},
        {"text": "Be the change you wish to see in the world.", "author": "Mahatma Gandhi", "avatar": "MG", "color": "#f59e0b"},
        {"text": "In the end, we will remember not the words of our enemies, but the silence of our friends.", "author": "Martin Luther King Jr.", "avatar": "MLK", "color": "#8b5cf6"},
        {"text": "The function of leadership is to produce more leaders, not more followers.", "author": "Ralph Nader", "avatar": "RN", "color": "#10b981"},
    ]
}

import random

def get_random_quote(category):
    """Get a random quote based on task category"""
    if category in QUOTES:
        return random.choice(QUOTES[category])
    # Default quote if category not found
    return {"text": "Great job! Keep up the excellent work!", "author": "Flow Team", "avatar": "✨", "color": "#6366f1"}

def parse_natural_language(text):
    """Parse natural language task input"""
    data = {"description": text, "due_date": None, "priority": 3}

    # Check for dates
    today = datetime.now()
    if "tomorrow" in text.lower():
        data["due_date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text.lower():
        data["due_date"] = today.strftime("%Y-%m-%d")

    # Check for priority keywords
    if any(word in text.lower() for word in ['urgent', 'critical', 'asap']):
        data["priority"] = 1
    elif "high" in text.lower():
        data["priority"] = 2

    return data

def calculate_task_score(task):
    """Calculate priority score for smart sorting"""
    score = PRIORITIES[task.get("priority", 3)].get("color") == "#ef4444" and 100 or 50

    if task.get("due_date"):
        try:
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            today = datetime.now().date()
            days_until = (due_date - today).days
            if days_until < 0:
                score += 100  # Overdue
            elif days_until == 0:
                score += 50   # Due today
            elif days_until == 1:
                score += 30   # Tomorrow
        except:
            pass

    return score

def create_task_card(task, in_trash=False):
    """Create a beautiful task card"""
    category = CATEGORIES.get(task.get("category", "personal"))
    priority = PRIORITIES[task.get("priority", 3)]

    # Due date badge
    due_badge = None
    if task.get("due_date"):
        try:
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            today = datetime.now().date()
            days_until = (due_date - today).days

            if days_until < 0:
                due_text, due_color = f"Overdue {abs(days_until)}d", "danger"
            elif days_until == 0:
                due_text, due_color = "Due today", "warning"
            elif days_until == 1:
                due_text, due_color = "Tomorrow", "info"
            else:
                due_text, due_color = due_date.strftime("%b %d"), "secondary"

            due_badge = dbc.Badge(due_text, color=due_color, className="me-2")
        except:
            pass

    # Recurring badge
    recurring_badge = None
    if task.get("recurring"):
        freq_icons = {
            "daily": "📅",
            "weekly": "📆",
            "monthly": "🗓️",
            "yearly": "📊"
        }
        freq = task.get("recurring_freq", "daily")
        recurring_badge = dbc.Badge(
            [html.I(className="fas fa-redo me-1"), f"{freq_icons.get(freq, '🔄')} {freq.title()}"],
            color="info",
            className="me-2"
        )

    # Build badges list
    badges = [
        dbc.Badge(
            [html.I(className="fas fa-flag me-1"), priority["name"]],
            color="light",
            text_color="dark",
            className="me-2"
        ),
        dbc.Badge(
            [category["icon"], " ", category["name"]],
            color="light",
            text_color="dark",
            className="me-2"
        )
    ]

    if recurring_badge:
        badges.append(recurring_badge)
    if due_badge:
        badges.append(due_badge)

    # Action buttons for trash vs active tasks
    if in_trash:
        action_buttons = html.Div([
            dbc.Button(
                [html.I(className="fas fa-undo me-1"), "Restore"],
                id={"type": "restore-task", "index": task["id"]},
                color="success",
                size="sm",
                className="me-2"
            ),
            dbc.Button(
                [html.I(className="fas fa-times me-1"), "Delete Forever"],
                id={"type": "permanent-delete-task", "index": task["id"]},
                color="danger",
                size="sm"
            )
        ], className="d-flex")
    else:
        action_buttons = html.Div([
            dbc.Button(
                html.I(className="fas fa-edit"),
                id={"type": "edit-task", "index": task["id"]},
                color="light",
                size="sm",
                className="me-2"
            ),
            dbc.Button(
                html.I(className="fas fa-trash"),
                id={"type": "delete-task", "index": task["id"]},
                color="light",
                size="sm"
            )
        ], className="d-flex")

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                dbc.Checkbox(
                    id={"type": "complete-task", "index": task["id"]},
                    className="me-3",
                    style={"transform": "scale(1.4)"},
                    disabled=in_trash
                ) if not in_trash else html.Div(style={"width": "20px"}),
                html.Div([
                    html.H6(task["description"], className="mb-2", style={"fontWeight": "600", "opacity": "0.6" if in_trash else "1"}),
                    html.Div(badges)
                ], style={"flex": "1"}),
                action_buttons
            ], className="d-flex align-items-center")
        ])
    ], className="mb-3 task-card", style={
        "borderLeft": f"4px solid {category['color']}",
        "transition": "all 0.3s ease",
        "opacity": "0.8" if in_trash else "1"
    })

# Login Layout
login_layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div(className="custom-halo"),
                                    html.Div(className="halo-particle"),
                                    html.Div(className="halo-particle"),
                                    html.Div(className="halo-particle"),
                                    html.H2([
                                        html.Span("😇", className="angel-halo", style={"fontSize": "3rem", "marginRight": "10px"}),
                                        "Angel's Flow"
                                    ], className="mb-1", style={
                                        "fontWeight": "800",
                                        "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                                        "WebkitBackgroundClip": "text",
                                        "WebkitTextFillColor": "transparent",
                                        "backgroundClip": "text"
                                    })
                                ], className="halo-container", style={"display": "inline-block", "position": "relative"})
                            ], className="text-center"),
                            html.P("Intelligent Task Management", className="text-center text-muted mb-4"),
                            dbc.Label("Username", className="fw-bold"),
                            dbc.Input(
                                id="login-username",
                                type="text",
                                placeholder="Enter your name",
                                className="mb-3"
                            ),
                            dbc.Label("Password", className="fw-bold"),
                            dbc.Input(
                                id="login-password",
                                type="password",
                                placeholder="Enter password",
                                className="mb-3"
                            ),
                            html.Div(id="login-error", className="mb-3"),
                            dbc.Button(
                                [html.I(className="fas fa-sign-in-alt me-2"), "Login"],
                                id="login-btn",
                                color="primary",
                                className="w-100",
                                size="lg"
                            ),
                            html.Small("v2.0 - Cloud Sync Required", className="text-muted mt-3", style={"display": "block", "textAlign": "center"})
                        ])
                    ])
                ], className="login-card")
            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100", align="center")
    ], fluid=True, className="login-container")
], id="login-container-main")

# Main App Layout
def create_main_layout():
    return dbc.Container([
    # Data stores - use memory storage for cloud sync, local for theme
    dcc.Store(id="tasks-store", data=[], storage_type="memory" if USE_CLOUD_SYNC else "local"),
    dcc.Store(id="trash-store", data=[], storage_type="memory" if USE_CLOUD_SYNC else "local"),
    dcc.Store(id="filter-state", data={"category": "all", "search": ""}),
    dcc.Store(id="edit-task-store", data=None),
    dcc.Store(id="theme-store", data="light", storage_type="local"),
    dcc.Store(id="streak-store", data=0, storage_type="memory" if USE_CLOUD_SYNC else "local"),

    # Quote Toast Container
    html.Div(id="quote-toast-container", style={"position": "fixed", "top": "20px", "right": "20px", "zIndex": "9999"}),

    # Edit Task Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Edit Task")),
        dbc.ModalBody([
            dbc.Label("Task Description"),
            dbc.Textarea(
                id="edit-task-description",
                rows=3,
                className="mb-3"
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Priority", size="sm"),
                    dbc.Select(
                        id="edit-task-priority",
                        options=[{"label": v["name"], "value": k} for k, v in PRIORITIES.items()],
                        size="sm"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Category", size="sm"),
                    dbc.Select(
                        id="edit-task-category",
                        options=[{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in CATEGORIES.items()],
                        size="sm"
                    )
                ], width=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Due Date", size="sm"),
                    dbc.Input(
                        id="edit-task-due-date",
                        type="date",
                        size="sm"
                    )
                ], width=12)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-edit-btn", color="secondary", className="me-2"),
            dbc.Button("Save Changes", id="save-edit-btn", color="primary")
        ])
    ], id="edit-modal", is_open=False, size="lg"),

    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Div(className="custom-halo"),
                    html.Div(className="halo-particle"),
                    html.Div(className="halo-particle"),
                    html.Div(className="halo-particle"),
                    html.H1([
                        html.Span("😇", className="angel-halo", style={"fontSize": "2.5rem", "marginRight": "10px"}),
                        "Angel's Flow"
                    ], className="mb-1", style={
                        "fontWeight": "800",
                        "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "backgroundClip": "text"
                    })
                ], className="halo-container", style={"display": "inline-block", "position": "relative"}),
                html.P("Intelligent Task Management", className="text-muted mb-0"),
                html.Div([
                    dbc.Badge([
                        html.I(className="fas fa-cloud" + ("-check" if USE_CLOUD_SYNC else "-slash") + " me-1"),
                        "Cloud Sync " + ("ON" if USE_CLOUD_SYNC else "OFF")
                    ], color="success" if USE_CLOUD_SYNC else "warning", className="mt-2")
                ], className="text-center")
            ], className="text-center mb-0")
        ], width=True),
        dbc.Col([
            html.Div([
                dbc.Button(
                    html.I(id="theme-icon", className="fas fa-moon"),
                    id="theme-toggle",
                    color="light",
                    size="lg",
                    className="rounded-circle me-2",
                    style={"width": "50px", "height": "50px"}
                ),
                dbc.Button(
                    [html.I(className="fas fa-sign-out-alt me-1"), html.Span(id="username-display", children="Logout")],
                    id="logout-btn",
                    color="light",
                    size="sm"
                )
            ], className="text-end")
        ], width="auto")
    ], className="mb-4", align="center"),

    # Stats
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-tasks fa-2x mb-2", style={"color": "#6366f1"}),
                        html.H3(id="stat-active", children="0", className="mb-0"),
                        html.Small("Active Tasks", className="text-muted")
                    ], className="text-center")
                ])
            ], className="stat-card")
        ], width=6, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        dbc.Button(
                            html.I(className="fas fa-times", style={"fontSize": "12px"}),
                            id="reset-completed-btn",
                            color="light",
                            size="sm",
                            className="reset-tile-btn",
                            title="Clear completed tasks"
                        ),
                        html.I(className="fas fa-check-circle fa-2x mb-2", style={"color": "#10b981"}),
                        html.H3(id="stat-completed", children="0", className="mb-0"),
                        html.Small("Completed", className="text-muted")
                    ], className="text-center", style={"position": "relative"})
                ])
            ], className="stat-card")
        ], width=6, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        dbc.Button(
                            html.I(className="fas fa-times", style={"fontSize": "12px"}),
                            id="reset-streak-btn",
                            color="light",
                            size="sm",
                            className="reset-tile-btn",
                            title="Reset streak"
                        ),
                        html.I(className="fas fa-fire fa-2x mb-2", style={"color": "#ef4444"}),
                        html.H3(id="stat-streak", children="0", className="mb-0"),
                        html.Small("Day Streak", className="text-muted")
                    ], className="text-center", style={"position": "relative"})
                ])
            ], className="stat-card")
        ], width=6, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-2x mb-2", style={"color": "#8b5cf6"}),
                        html.H3(id="stat-rate", children="0%", className="mb-0"),
                        html.Small("Completion Rate", className="text-muted")
                    ], className="text-center")
                ])
            ], className="stat-card")
        ], width=6, md=3)
    ], className="mb-4 g-3"),

    # Main content
    dbc.Row([
        # Left sidebar - Add task
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5([html.I(className="fas fa-plus-circle me-2"), "Add Task"], className="mb-3"),
                    dbc.Textarea(
                        id="task-input",
                        placeholder="What needs to be done? Try 'Call mom tomorrow urgent'",
                        rows=3,
                        className="mb-3"
                    ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Priority", size="sm"),
                            dbc.Select(
                                id="task-priority",
                                options=[{"label": v["name"], "value": k} for k, v in PRIORITIES.items()],
                                value=3,
                                size="sm"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Category", size="sm"),
                            dbc.Select(
                                id="task-category",
                                options=[{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in CATEGORIES.items()],
                                value="personal",
                                size="sm"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Due Date", size="sm"),
                            dbc.Input(
                                id="task-due-date",
                                type="date",
                                size="sm"
                            )
                        ], width=12)
                    ], className="mb-3"),

                    # Recurring task options
                    dbc.Row([
                        dbc.Col([
                            dbc.Checkbox(
                                id="task-recurring-toggle",
                                label="🔄 Make this recurring",
                                value=False,
                                className="mb-2"
                            ),
                            dbc.Collapse([
                                dbc.Label("Repeat every:", size="sm", className="mb-1"),
                                dbc.Select(
                                    id="task-recurring-freq",
                                    options=[
                                        {"label": "📅 Daily", "value": "daily"},
                                        {"label": "📆 Weekly", "value": "weekly"},
                                        {"label": "🗓️ Monthly", "value": "monthly"},
                                        {"label": "📊 Yearly", "value": "yearly"}
                                    ],
                                    value="daily",
                                    size="sm",
                                    className="mb-2"
                                ),
                                html.Small("Next occurrence will be created when completed", className="text-muted")
                            ], id="recurring-options", is_open=False)
                        ], width=12)
                    ], className="mb-3"),

                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "Add Task"],
                        id="add-task-btn",
                        color="primary",
                        className="w-100"
                    ),
                    html.Div(id="add-feedback", className="mt-2")
                ])
            ], className="mb-3"),

            # Quick filters
            dbc.Card([
                dbc.CardBody([
                    html.H6("Quick Filters", className="mb-3"),
                    dbc.RadioItems(
                        id="view-filter",
                        options=[
                            {"label": "📋 All Tasks", "value": "all"},
                            {"label": "⚡ Smart View", "value": "smart"},
                            {"label": "📅 Due Today", "value": "today"},
                            {"label": "🔄 Recurring", "value": "recurring"}
                        ],
                        value="smart",
                        className="mb-2"
                    ),
                    html.Hr(className="my-2"),
                    dbc.Button(
                        [html.I(className="fas fa-trash me-2"), "Trash", html.Span(id="trash-count", className="badge bg-secondary ms-2", children="0")],
                        id="view-trash-btn",
                        color="light",
                        className="w-100",
                        size="sm"
                    )
                ])
            ])
        ], width=12, lg=4),

        # Right - Task list
        dbc.Col([
            # Search and category filter
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText(html.I(className="fas fa-search")),
                        dbc.Input(id="search-input", placeholder="Search tasks...")
                    ])
                ], width=12, md=8),
                dbc.Col([
                    dbc.Select(
                        id="category-filter",
                        options=[{"label": "All Categories", "value": "all"}] +
                                [{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in CATEGORIES.items()],
                        value="all"
                    )
                ], width=12, md=4)
            ], className="mb-3 g-2"),

            # Task list
            html.Div(id="task-list")
        ], width=12, lg=8)
    ])
    ], fluid=True, className="p-3 p-md-4", style={"backgroundColor": "#f8fafc", "minHeight": "100vh"})

# Actual app layout with conditional rendering
app.layout = html.Div([
    # Always use localStorage for login - it's reliable and we need it to persist
    dcc.Store(id="login-store", data={"logged_in": False, "username": ""}, storage_type="local"),
    dcc.Store(id="theme-store", data="light", storage_type="local"),
    # Start with login screen when cloud sync is enabled, otherwise empty div that gets filled by callback
    html.Div(id="page-content", children=login_layout if USE_CLOUD_SYNC else None),
    # Clear ONLY task-related localStorage on first load (NOT login data)
    html.Script("""
        if (""" + str(USE_CLOUD_SYNC).lower() + """) {
            // Check if we need to clear storage (only do once per session)
            const clearFlag = sessionStorage.getItem('storage_cleared_v2');

            if (!clearFlag) {
                console.log('🧹 First load - clearing task localStorage (keeping login)');
                // Clear task data but KEEP login data
                const keysToRemove = [];
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    // Clear tasks/trash/streak but NOT login-store
                    if (key && (key.includes('tasks-store') || key.includes('trash-store') || key.includes('streak-store')) && !key.includes('login-store')) {
                        keysToRemove.push(key);
                    }
                }
                keysToRemove.forEach(key => {
                    console.log('Clearing localStorage key:', key);
                    localStorage.removeItem(key);
                });

                // Set flag so we don't clear again this session
                sessionStorage.setItem('storage_cleared_v2', 'true');
                console.log('✅ Cleared task localStorage - login preserved');
            }
        }
    """) if USE_CLOUD_SYNC else html.Div()
], id="app-container", className="theme-light")

# Callbacks

@app.callback(
    Output("recurring-options", "is_open"),
    Input("task-recurring-toggle", "value")
)
def toggle_recurring_options(is_recurring):
    """Toggle recurring options visibility"""
    return is_recurring

@app.callback(
    Output("tasks-store", "data"),
    Output("add-feedback", "children"),
    Output("task-input", "value"),
    Output("task-priority", "value"),
    Output("task-category", "value"),
    Output("task-due-date", "value"),
    Output("task-recurring-toggle", "value"),
    Input("add-task-btn", "n_clicks"),
    State("task-input", "value"),
    State("task-priority", "value"),
    State("task-category", "value"),
    State("task-due-date", "value"),
    State("task-recurring-toggle", "value"),
    State("task-recurring-freq", "value"),
    State("tasks-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def add_task(n, description, priority, category, due_date, is_recurring, recurring_freq, tasks, login_data):
    """Add a new task"""
    if not description or not description.strip():
        return tasks, dbc.Alert("Please enter a task!", color="warning", duration=3000), description, priority, category, due_date, is_recurring

    # Parse natural language
    parsed = parse_natural_language(description)

    new_task = {
        "id": str(uuid.uuid4()),
        "description": description.strip(),
        "priority": int(priority),
        "category": category,
        "due_date": due_date or parsed.get("due_date"),
        "created_at": datetime.now().isoformat(),
        "completed": False,
        "recurring": is_recurring,
        "recurring_freq": recurring_freq if is_recurring else None
    }

    tasks.append(new_task)

    # Save to cloud if logged in
    print(f"\n🔍 ADD TASK DEBUG:")
    print(f"   USE_CLOUD_SYNC: {USE_CLOUD_SYNC}")
    print(f"   login_data: {login_data}")
    print(f"   Task ID: {new_task.get('id')}")
    print(f"   Task description: {new_task.get('description')}")

    if USE_CLOUD_SYNC and login_data.get("logged_in"):
        username = login_data.get("username")
        if username:
            print(f"   ✅ Attempting cloud save for user: {username}")
            save_result = supabase_db.save_task(username, new_task)
            print(f"   ☁️  Cloud save result: {save_result}")
        else:
            print(f"   ⚠️  No username in login_data")
    else:
        print(f"   ❌ Cloud save skipped - USE_CLOUD_SYNC:{USE_CLOUD_SYNC}, logged_in:{login_data.get('logged_in')}")

    return tasks, dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Task added!" + (" (Recurring)" if is_recurring else "")],
        color="success",
        duration=3000
    ), "", 3, "personal", "", False

@app.callback(
    Output("task-list", "children"),
    Output("stat-active", "children"),
    Output("stat-completed", "children"),
    Output("stat-rate", "children"),
    Output("stat-streak", "children"),
    Output("trash-count", "children"),
    Input("tasks-store", "data"),
    Input("trash-store", "data"),
    Input("view-filter", "value"),
    Input("search-input", "value"),
    Input("category-filter", "value"),
    Input("streak-store", "data"),
    Input("view-trash-btn", "n_clicks")
)
def update_tasks(tasks, trash, view, search, category, streak, trash_clicks):
    """Update task list and stats"""
    trash_count = len(trash) if trash else 0

    # Check if we're in trash view (based on button clicks)
    in_trash_view = trash_clicks and trash_clicks % 2 == 1

    if in_trash_view:
        # Show trash items
        if not trash:
            empty = html.Div([
                html.I(className="fas fa-trash fa-4x mb-3", style={"color": "#cbd5e1"}),
                html.H5("Trash is empty", className="text-muted"),
                html.P("Deleted tasks will appear here", className="text-muted")
            ], className="text-center py-5")
            return empty, "0", "0", "0%", str(streak), str(trash_count)

        task_cards = [create_task_card(task, in_trash=True) for task in trash]
        return task_cards, "0", "0", "0%", str(streak), str(trash_count)

    # Regular task view
    if not tasks:
        empty = html.Div([
            html.I(className="fas fa-inbox fa-4x mb-3", style={"color": "#cbd5e1"}),
            html.H5("No tasks yet", className="text-muted"),
            html.P("Add your first task to get started!", className="text-muted")
        ], className="text-center py-5")
        return empty, "0", "0", "0%", str(streak), str(trash_count)

    # Filter tasks
    active_tasks = [t for t in tasks if not t.get("completed")]
    completed_tasks = [t for t in tasks if t.get("completed")]

    # Apply filters
    filtered = active_tasks.copy()

    if search:
        filtered = [t for t in filtered if search.lower() in t["description"].lower()]

    if category != "all":
        filtered = [t for t in filtered if t.get("category") == category]

    if view == "today":
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        filtered = [t for t in filtered if t.get("due_date") == today_str]
    elif view == "smart":
        filtered.sort(key=calculate_task_score, reverse=True)
    elif view == "recurring":
        filtered = [t for t in filtered if t.get("recurring")]

    # Create task cards
    if not filtered:
        task_cards = html.Div([
            html.I(className="fas fa-filter fa-3x mb-3", style={"color": "#cbd5e1"}),
            html.H6("No tasks match your filters", className="text-muted")
        ], className="text-center py-5")
    else:
        task_cards = [create_task_card(task) for task in filtered]

    # Calculate stats
    active_count = len(active_tasks)
    completed_count = len(completed_tasks)
    total = len(tasks)
    completion_rate = f"{int((completed_count / total * 100))}%" if total > 0 else "0%"

    return task_cards, str(active_count), str(completed_count), completion_rate, str(streak), str(trash_count)

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Output("quote-toast-container", "children"),
    Output("streak-store", "data", allow_duplicate=True),
    Input({"type": "complete-task", "index": ALL}, "value"),
    State("tasks-store", "data"),
    State("streak-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def complete_task(values, tasks, current_streak, login_data):
    """Mark task as completed and show inspirational quote"""
    if not ctx.triggered:
        return tasks, None, current_streak

    trigger = ctx.triggered[0]["prop_id"]
    if not trigger or ".value" not in trigger:
        return tasks, None, current_streak

    # Get the actual checkbox value - only proceed if it's True (checked)
    checkbox_value = ctx.triggered[0].get("value")
    if not checkbox_value:
        # Checkbox was unchecked or not set - don't show quote
        return tasks, None, current_streak

    task_id = json.loads(trigger.split(".")[0])["index"]

    completed_category = None
    is_recurring = False
    recurring_task_data = None

    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            completed_category = task.get("category", "work")

            # Check if this is a recurring task
            if task.get("recurring"):
                is_recurring = True
                recurring_task_data = task.copy()
            break

    # If recurring, create next occurrence
    if is_recurring and recurring_task_data:
        next_task = recurring_task_data.copy()
        next_task["id"] = str(uuid.uuid4())
        next_task["completed"] = False
        next_task["completed_at"] = None
        next_task["created_at"] = datetime.now().isoformat()

        # Calculate next due date
        if next_task.get("due_date"):
            try:
                current_due = datetime.strptime(next_task["due_date"], "%Y-%m-%d")
                freq = next_task.get("recurring_freq", "daily")

                if freq == "daily":
                    next_due = current_due + timedelta(days=1)
                elif freq == "weekly":
                    next_due = current_due + timedelta(weeks=1)
                elif freq == "monthly":
                    next_due = current_due + timedelta(days=30)
                elif freq == "yearly":
                    next_due = current_due + timedelta(days=365)
                else:
                    next_due = current_due + timedelta(days=1)

                next_task["due_date"] = next_due.strftime("%Y-%m-%d")
            except:
                pass

        tasks.append(next_task)

        # Save next occurrence to cloud
        if USE_CLOUD_SYNC and login_data.get("logged_in"):
            username = login_data.get("username")
            if username:
                supabase_db.save_task(username, next_task)

    # Save completed task to cloud
    if USE_CLOUD_SYNC and login_data.get("logged_in"):
        username = login_data.get("username")
        if username:
            completed_task = next((t for t in tasks if t["id"] == task_id), None)
            if completed_task:
                supabase_db.save_task(username, completed_task)
                print(f"☁️  Updated completed task in cloud for {username}")

    # Update streak in cloud
    new_streak = current_streak + 1
    if USE_CLOUD_SYNC and login_data.get("logged_in"):
        username = login_data.get("username")
        if username:
            supabase_db.update_user_stats(username, streak=new_streak)

    # Get a random quote based on the task category
    if completed_category:
        quote = get_random_quote(completed_category)

        # Create a beautiful quote toast
        quote_toast = dbc.Toast(
            [
                html.Div([
                    html.Div([
                        html.Div(
                            quote["avatar"],
                            style={
                                "width": "60px",
                                "height": "60px",
                                "borderRadius": "50%",
                                "backgroundColor": quote["color"],
                                "color": "white",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontSize": "20px",
                                "fontWeight": "bold",
                                "marginRight": "15px",
                                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)"
                            }
                        ),
                        html.Div([
                            html.P(f'"{quote["text"]}"', style={
                                "fontSize": "15px",
                                "fontStyle": "italic",
                                "marginBottom": "8px",
                                "lineHeight": "1.5"
                            }),
                            html.P(f"— {quote['author']}", style={
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "color": quote["color"],
                                "marginBottom": "0"
                            })
                        ], style={"flex": "1"})
                    ], style={"display": "flex", "alignItems": "start"}),
                    html.Div("🎉 Task Completed!", style={
                        "marginTop": "10px",
                        "padding": "8px",
                        "backgroundColor": "#10b98133",
                        "borderRadius": "8px",
                        "textAlign": "center",
                        "fontWeight": "600",
                        "color": "#10b981"
                    })
                ])
            ],
            header="✨ Inspiration",
            is_open=True,
            duration=8000,
            icon="success",
            style={
                "minWidth": "400px",
                "maxWidth": "500px",
                "boxShadow": "0 10px 40px rgba(0,0,0,0.2)"
            }
        )

        return tasks, quote_toast, new_streak

    return tasks, None, new_streak

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Output("trash-store", "data", allow_duplicate=True),
    Input({"type": "delete-task", "index": ALL}, "n_clicks"),
    State("tasks-store", "data"),
    State("trash-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def delete_task(n_clicks, tasks, trash, login_data):
    """Move task to trash"""
    if not ctx.triggered or not any(n_clicks):
        return tasks, trash

    trigger = ctx.triggered[0]["prop_id"]
    task_id = json.loads(trigger.split(".")[0])["index"]

    # Find the task and move it to trash
    task_to_delete = None
    for task in tasks:
        if task["id"] == task_id:
            task_to_delete = task.copy()
            task_to_delete["deleted_at"] = datetime.now().isoformat()
            break

    if task_to_delete:
        if not trash:
            trash = []
        trash.append(task_to_delete)
        tasks = [t for t in tasks if t["id"] != task_id]

        # Save to cloud trash and delete from cloud tasks
        if USE_CLOUD_SYNC and login_data.get("logged_in"):
            username = login_data.get("username")
            if username:
                supabase_db.save_to_trash(username, task_to_delete)
                supabase_db.delete_task_from_cloud(username, task_id)
                print(f"☁️  Moved task to cloud trash for {username}")

    return tasks, trash

@app.callback(
    Output("edit-modal", "is_open"),
    Output("edit-task-store", "data"),
    Input({"type": "edit-task", "index": ALL}, "n_clicks"),
    Input("cancel-edit-btn", "n_clicks"),
    Input("save-edit-btn", "n_clicks"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def toggle_edit_modal(edit_clicks, cancel_clicks, save_clicks, tasks):
    """Open/close edit modal and store task being edited"""
    if not ctx.triggered:
        return False, None

    trigger_id = ctx.triggered[0]["prop_id"]

    # If edit button clicked, open modal and store task ID
    if "edit-task" in trigger_id and any(edit_clicks):
        task_id = json.loads(trigger_id.split(".")[0])["index"]
        return True, task_id

    # If cancel or save clicked, close modal
    return False, None

@app.callback(
    Output("edit-task-description", "value"),
    Output("edit-task-priority", "value"),
    Output("edit-task-category", "value"),
    Output("edit-task-due-date", "value"),
    Input("edit-task-store", "data"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def populate_edit_modal(task_id, tasks):
    """Populate edit modal with task data"""
    if not task_id:
        return "", 3, "personal", ""

    # Find the task
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return "", 3, "personal", ""

    return (
        task.get("description", ""),
        task.get("priority", 3),
        task.get("category", "personal"),
        task.get("due_date", "")
    )

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Input("save-edit-btn", "n_clicks"),
    State("edit-task-store", "data"),
    State("edit-task-description", "value"),
    State("edit-task-priority", "value"),
    State("edit-task-category", "value"),
    State("edit-task-due-date", "value"),
    State("tasks-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def save_edited_task(n_clicks, task_id, description, priority, category, due_date, tasks, login_data):
    """Save edited task"""
    if not n_clicks or not task_id:
        return tasks

    # Find and update the task
    updated_task = None
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = description.strip() if description else task["description"]
            task["priority"] = int(priority)
            task["category"] = category
            task["due_date"] = due_date if due_date else None
            updated_task = task
            break

    # Save to cloud
    if updated_task and USE_CLOUD_SYNC and login_data.get("logged_in"):
        username = login_data.get("username")
        if username:
            supabase_db.save_task(username, updated_task)
            print(f"☁️  Updated task in cloud for {username}")

    return tasks

@app.callback(
    Output("theme-store", "data"),
    Output("theme-icon", "className"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    """Toggle between light and dark mode"""
    new_theme = "dark" if current_theme == "light" else "light"
    icon_class = "fas fa-sun" if new_theme == "dark" else "fas fa-moon"
    return new_theme, icon_class

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Output("trash-store", "data", allow_duplicate=True),
    Input({"type": "restore-task", "index": ALL}, "n_clicks"),
    State("tasks-store", "data"),
    State("trash-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def restore_task(n_clicks, tasks, trash, login_data):
    """Restore task from trash"""
    if not ctx.triggered or not any(n_clicks):
        return tasks, trash

    trigger = ctx.triggered[0]["prop_id"]
    task_id = json.loads(trigger.split(".")[0])["index"]

    # Find the task in trash and restore it
    task_to_restore = None
    trash_item_id = None
    for task in trash:
        if task["id"] == task_id or task.get("task_id") == task_id:
            task_to_restore = task.copy()
            trash_item_id = task.get("id")  # Cloud trash ID
            if "deleted_at" in task_to_restore:
                del task_to_restore["deleted_at"]
            break

    if task_to_restore:
        tasks.append(task_to_restore)
        trash = [t for t in trash if t["id"] != task_id and t.get("task_id") != task_id]

        # Restore in cloud
        if USE_CLOUD_SYNC and login_data.get("logged_in"):
            username = login_data.get("username")
            if username:
                supabase_db.save_task(username, task_to_restore)
                if trash_item_id:
                    supabase_db.delete_from_trash(username, trash_item_id)
                print(f"☁️  Restored task from cloud trash for {username}")

    return tasks, trash

@app.callback(
    Output("trash-store", "data", allow_duplicate=True),
    Input({"type": "permanent-delete-task", "index": ALL}, "n_clicks"),
    State("trash-store", "data"),
    State("login-store", "data"),
    prevent_initial_call=True
)
def permanent_delete_task(n_clicks, trash, login_data):
    """Permanently delete task from trash"""
    if not ctx.triggered or not any(n_clicks):
        return trash

    trigger = ctx.triggered[0]["prop_id"]
    task_id = json.loads(trigger.split(".")[0])["index"]

    # Delete from cloud trash
    if USE_CLOUD_SYNC and login_data.get("logged_in"):
        username = login_data.get("username")
        if username:
            # Find the cloud trash ID
            for item in trash:
                if item["id"] == task_id or item.get("task_id") == task_id:
                    cloud_id = item.get("id")
                    if cloud_id:
                        supabase_db.delete_from_trash(username, cloud_id)
                        print(f"☁️  Permanently deleted from cloud trash for {username}")
                    break

    trash = [t for t in trash if t["id"] != task_id and t.get("task_id") != task_id]
    return trash

@app.callback(
    Output("app-container", "className"),
    Input("theme-store", "data")
)
def apply_theme(theme):
    """Apply theme class to container"""
    return f"theme-{theme}"

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Input("reset-completed-btn", "n_clicks"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def reset_completed(n_clicks, tasks):
    """Clear all completed tasks"""
    if not n_clicks:
        return tasks
    # Remove all completed tasks
    return [t for t in tasks if not t.get("completed")]

@app.callback(
    Output("streak-store", "data", allow_duplicate=True),
    Input("reset-streak-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_streak(n_clicks):
    """Reset streak counter"""
    if not n_clicks:
        return 0
    return 0

@app.callback(
    Output("page-content", "children"),
    Input("login-store", "data")
)
def display_page(login_data):
    """Display login page or main app based on login status"""
    print(f"\n📄 DISPLAY PAGE CALLBACK:")
    print(f"   login_data: {login_data}")
    print(f"   logged_in: {login_data.get('logged_in') if login_data else None}")
    print(f"   username: {login_data.get('username') if login_data else None}")

    # When cloud sync is enabled, require login
    if USE_CLOUD_SYNC:
        if login_data and login_data.get("logged_in") and login_data.get("username"):
            print(f"   ✅ Showing main app for user: {login_data.get('username')}")
            return create_main_layout()
        else:
            print(f"   ❌ Showing login page (not logged in)")
            return login_layout

    # Without cloud sync, allow access without login
    if login_data and login_data.get("logged_in"):
        print(f"   ✅ Showing main app (no cloud sync)")
        return create_main_layout()

    print(f"   ❌ Showing login page (default)")
    return login_layout

@app.callback(
    Output("login-store", "data", allow_duplicate=True),
    Output("login-error", "children"),
    Input("login-btn", "n_clicks"),
    State("login-username", "value"),
    State("login-password", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Handle login authentication"""
    print(f"\n🔐 LOGIN ATTEMPT:")
    print(f"   n_clicks: {n_clicks}")
    print(f"   username received: '{username}'")
    print(f"   password received: '{password}'")

    if not n_clicks:
        print(f"   ❌ No clicks, returning not logged in")
        return {"logged_in": False, "username": ""}, None

    if not username or not username.strip():
        print(f"   ❌ Empty username")
        return {"logged_in": False, "username": ""}, dbc.Alert("Please enter your username", color="warning", duration=3000)

    # Authenticate with specific credentials
    print(f"   Checking: '{username.strip()}' == 'jangel1906': {username.strip() == 'jangel1906'}")
    print(f"   Checking: '{password}' == 'Tokyo1913@': {password == 'Tokyo1913@'}")

    if username.strip() == "jangel1906" and password == "Tokyo1913@":
        print(f"   ✅ LOGIN SUCCESS! Setting logged_in=True, username=jangel1906")
        return {"logged_in": True, "username": "jangel1906"}, None

    print(f"   ❌ LOGIN FAILED! Invalid credentials")
    return {"logged_in": False, "username": ""}, dbc.Alert("Invalid username or password", color="danger", duration=3000)

@app.callback(
    Output("login-store", "data", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if not n_clicks:
        return {"logged_in": False, "username": ""}
    return {"logged_in": False, "username": ""}

@app.callback(
    Output("username-display", "children"),
    Input("login-store", "data")
)
def update_username_display(login_data):
    """Update username in header"""
    print(f"\n👤 UPDATE USERNAME DISPLAY:")
    print(f"   login_data: {login_data}")
    print(f"   logged_in: {login_data.get('logged_in') if login_data else None}")
    print(f"   username: {login_data.get('username') if login_data else None}")

    if login_data and login_data.get("logged_in") and login_data.get("username"):
        result = f"{login_data['username']} - Logout"
        print(f"   ✅ Returning: '{result}'")
        return result
    print(f"   ❌ Returning: 'Logout'")
    return "Logout"

# Cloud Sync Callbacks
@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Output("trash-store", "data", allow_duplicate=True),
    Output("streak-store", "data", allow_duplicate=True),
    Input("login-store", "data"),
    State("tasks-store", "data"),
    State("trash-store", "data"),
    State("streak-store", "data"),
    prevent_initial_call=True
)
def load_cloud_data(login_data, local_tasks, local_trash, local_streak):
    """Load user data from cloud when logged in"""
    print(f"\n🔍 LOAD CLOUD DATA DEBUG:")
    print(f"   login_data: {login_data}")
    print(f"   USE_CLOUD_SYNC: {USE_CLOUD_SYNC}")
    print(f"   local_tasks count: {len(local_tasks) if local_tasks else 0}")

    if not login_data.get("logged_in") or not USE_CLOUD_SYNC:
        print(f"   ❌ Skipping cloud load - logged_in:{login_data.get('logged_in')}, USE_CLOUD_SYNC:{USE_CLOUD_SYNC}")
        return local_tasks, local_trash, local_streak

    username = login_data.get("username")
    if not username:
        print(f"   ❌ No username found")
        return local_tasks, local_trash, local_streak

    try:
        # Load tasks from cloud
        print(f"   📡 Fetching tasks from Supabase for user: {username}")
        cloud_tasks = supabase_db.get_user_tasks(username)
        print(f"   📦 Retrieved {len(cloud_tasks)} tasks from cloud")

        # Load trash from cloud
        cloud_trash = supabase_db.get_user_trash(username)

        # Load stats from cloud
        stats = supabase_db.get_user_stats(username)
        cloud_streak = stats.get('streak', 0)

        # If cloud is empty but we have local data, sync local to cloud (first login)
        if not cloud_tasks and local_tasks:
            print(f"   📤 Migrating {len(local_tasks)} local tasks to cloud...")
            supabase_db.sync_local_to_cloud(username, local_tasks)
            cloud_tasks = local_tasks

        print(f"   ✅ Loaded {len(cloud_tasks)} tasks from cloud for {username}")
        if cloud_tasks:
            for task in cloud_tasks:
                print(f"      - {task.get('description')} (ID: {task.get('id')[:8]}...)")

        return cloud_tasks, cloud_trash, cloud_streak

    except Exception as e:
        print(f"   ⚠️  Error loading cloud data: {e}")
        import traceback
        traceback.print_exc()
        return local_tasks, local_trash, local_streak

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8052))
    app.run(debug=False, host="0.0.0.0", port=port)
