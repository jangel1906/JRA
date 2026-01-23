"""
Flow - Intelligent Task Management
A world-class task management application with modern UI/UX
Built with Dash, featuring smart prioritization, focus modes, and beautiful analytics
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import uuid
import re
from collections import defaultdict
import os

# Initialize the Dash app with modern theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "apple-mobile-web-app-title", "content": "Flow"},
        {"name": "theme-color", "content": "#6366f1"},
        {"name": "description", "content": "Intelligent task management for focused productivity"}
    ]
)

app.title = "Flow - Task Management"
server = app.server

# Energy levels for task scheduling
ENERGY_LEVELS = {
    "high": {"name": "High Energy", "icon": "⚡", "color": "#ef4444", "time": "Morning"},
    "medium": {"name": "Medium Energy", "icon": "🔆", "color": "#f59e0b", "time": "Midday"},
    "low": {"name": "Low Energy", "icon": "🌙", "color": "#3b82f6", "time": "Evening"}
}

# Task categories with beautiful colors
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
    1: {"name": "Critical", "color": "#ef4444", "weight": 100},
    2: {"name": "High", "color": "#f59e0b", "weight": 75},
    3: {"name": "Medium", "color": "#3b82f6", "weight": 50},
    4: {"name": "Low", "color": "#10b981", "weight": 25}
}

def parse_natural_language_task(text):
    """Parse natural language task input like 'Call mom tomorrow at 3pm'"""
    task_data = {
        "description": text,
        "due_date": None,
        "due_time": None,
        "priority": 3
    }

    # Parse dates
    today = datetime.now()
    if "tomorrow" in text.lower():
        task_data["due_date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text.lower():
        task_data["due_date"] = today.strftime("%Y-%m-%d")

    # Parse times (3pm, 15:00, etc.)
    time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', text.lower())
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = time_match.group(3)

        if meridiem == 'pm' and hour < 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0

        task_data["due_time"] = f"{hour:02d}:{minute:02d}"

    # Parse priority keywords
    if any(word in text.lower() for word in ['urgent', 'important', 'critical', 'asap']):
        task_data["priority"] = 1
    elif any(word in text.lower() for word in ['high', 'soon']):
        task_data["priority"] = 2

    return task_data

def calculate_task_score(task):
    """Calculate smart priority score for task sorting"""
    score = PRIORITIES[task.get("priority", 3)]["weight"]

    # Boost score if due soon
    if task.get("due_date"):
        try:
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_until = (due - datetime.now()).days
            if days_until == 0:
                score += 50  # Due today
            elif days_until == 1:
                score += 30  # Due tomorrow
            elif days_until < 0:
                score += 100  # Overdue!
        except:
            pass

    # Boost if has time estimate (shows commitment)
    if task.get("time_estimate"):
        score += 10

    return score

def create_task_card(task, index):
    """Create a beautiful card for a task"""
    category = CATEGORIES.get(task.get("category", "personal"), CATEGORIES["personal"])
    priority = PRIORITIES[task.get("priority", 3)]
    energy = ENERGY_LEVELS.get(task.get("energy", "medium"), ENERGY_LEVELS["medium"])

    # Due date badge
    due_badge = None
    if task.get("due_date"):
        try:
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_until = (due - datetime.now()).days

            if days_until < 0:
                due_text = f"Overdue {abs(days_until)}d"
                due_color = "danger"
            elif days_until == 0:
                due_text = "Due today"
                due_color = "warning"
            elif days_until == 1:
                due_text = "Tomorrow"
                due_color = "info"
            else:
                due_text = due.strftime("%b %d")
                due_color = "secondary"

            due_badge = dbc.Badge(due_text, color=due_color, className="me-2")
        except:
            pass

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                # Left: Checkbox and content
                html.Div([
                    dbc.Checkbox(
                        id={"type": "task-checkbox", "index": task["id"]},
                        className="task-checkbox",
                        style={"transform": "scale(1.3)"}
                    ),
                    html.Div([
                        html.H6(
                            task["description"],
                            className="mb-1",
                            style={"fontWeight": "500"}
                        ),
                        html.Div([
                            dbc.Badge(
                                [html.I(className=f"fas fa-flag me-1"), priority["name"]],
                                color="light",
                                text_color="dark",
                                className="me-2",
                                style={"borderLeft": f"3px solid {priority['color']}"}
                            ),
                            dbc.Badge(
                                [category["icon"], " ", category["name"]],
                                color="light",
                                text_color="dark",
                                className="me-2"
                            ),
                            dbc.Badge(
                                [energy["icon"], " ", energy["name"]],
                                color="light",
                                text_color="dark",
                                className="me-2"
                            ),
                            due_badge if due_badge else None,
                            dbc.Badge(
                                f"{task.get('time_estimate', 30)}m",
                                color="light",
                                text_color="dark"
                            ) if task.get("time_estimate") else None
                        ], className="d-flex flex-wrap gap-1")
                    ], className="ms-3", style={"flex": "1"})
                ], className="d-flex align-items-start"),

                # Right: Actions
                html.Div([
                    dbc.Button(
                        html.I(className="fas fa-play"),
                        id={"type": "start-task", "index": task["id"]},
                        color="primary",
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
            ], className="d-flex justify-content-between align-items-start")
        ], className="p-3")
    ], className="task-card mb-3", style={
        "borderLeft": f"4px solid {category['color']}",
        "transition": "all 0.3s ease",
        "cursor": "pointer"
    })

def create_stats_card(title, value, subtitle, icon, color):
    """Create a stat card for the dashboard"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"fas {icon}", style={
                        "fontSize": "2rem",
                        "color": color,
                        "opacity": "0.8"
                    })
                ]),
                html.Div([
                    html.H3(value, className="mb-0", style={"fontWeight": "700"}),
                    html.P(title, className="text-muted mb-0", style={"fontSize": "0.875rem"}),
                    html.Small(subtitle, className="text-muted", style={"fontSize": "0.75rem"})
                ], className="ms-3")
            ], className="d-flex align-items-center")
        ])
    ], className="stat-card h-100")

# App Layout
app.layout = dbc.Container([
    # PWA Links
    html.Link(rel='manifest', href='/assets/flow-manifest.json'),
    html.Link(rel='icon', type='image/png', sizes='192x192', href='/assets/icons/icon-192x192.png'),
    html.Link(rel='apple-touch-icon', sizes='180x180', href='/assets/icons/icon-192x192.png'),

    # Data stores
    dcc.Store(id='tasks-store', data=[]),
    dcc.Store(id='completed-tasks-store', data=[]),
    dcc.Store(id='focus-task-store', data=None),
    dcc.Store(id='pomodoro-state', data={"running": False, "time_left": 1500}),
    dcc.Store(id='theme-store', data="light"),

    # Intervals
    dcc.Interval(id='pomodoro-interval', interval=1000, n_intervals=0, disabled=True),
    dcc.Interval(id='stats-interval', interval=60000, n_intervals=0),  # Update stats every minute

    # Header
    dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H2([
                            html.Span("✨ ", style={"fontSize": "1.5rem"}),
                            "Flow"
                        ], className="mb-0", style={
                            "fontWeight": "700",
                            "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent"
                        }),
                        html.P("Intelligent Task Management", className="text-muted mb-0", style={"fontSize": "0.875rem"})
                    ])
                ], width="auto"),
                dbc.Col([
                    html.Div([
                        dbc.Button(
                            html.I(className="fas fa-bolt"),
                            id="focus-mode-btn",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-chart-line"),
                            id="analytics-btn",
                            color="light",
                            className="me-2"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-moon"),
                            id="theme-toggle",
                            color="light"
                        )
                    ], className="d-flex")
                ], width="auto", className="ms-auto")
            ], className="w-100 align-items-center")
        ], fluid=True)
    ], color="white", dark=False, className="mb-4 shadow-sm", style={"padding": "1rem 0"}),

    # Main content
    dbc.Row([
        # Left sidebar - Quick actions
        dbc.Col([
            # Quick add task
            dbc.Card([
                dbc.CardBody([
                    html.H5([html.I(className="fas fa-plus-circle me-2"), "Quick Add"], className="mb-3"),
                    dbc.Textarea(
                        id="quick-add-input",
                        placeholder="What needs to be done? Try 'Call mom tomorrow at 3pm'",
                        rows=3,
                        className="mb-3",
                        style={"fontSize": "0.95rem"}
                    ),
                    html.Div([
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
                                dbc.Label("Energy", size="sm"),
                                dbc.Select(
                                    id="task-energy",
                                    options=[{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in ENERGY_LEVELS.items()],
                                    value="medium",
                                    size="sm"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Time (min)", size="sm"),
                                dbc.Input(
                                    id="task-time",
                                    type="number",
                                    value=30,
                                    min=5,
                                    step=5,
                                    size="sm"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        dbc.Button(
                            [html.I(className="fas fa-plus me-2"), "Add Task"],
                            id="add-task-btn",
                            color="primary",
                            className="w-100"
                        )
                    ]),
                    html.Div(id="add-task-feedback", className="mt-2")
                ])
            ], className="mb-3"),

            # Today's focus
            dbc.Card([
                dbc.CardBody([
                    html.H5([html.I(className="fas fa-calendar-day me-2"), "Today's Focus"], className="mb-3"),
                    html.Div(id="daily-focus", className="text-center text-muted")
                ])
            ], className="mb-3"),

            # Pomodoro timer
            dbc.Card([
                dbc.CardBody([
                    html.H5([html.I(className="fas fa-clock me-2"), "Focus Timer"], className="mb-3"),
                    html.Div(id="pomodoro-display", className="text-center"),
                    dbc.ButtonGroup([
                        dbc.Button("Start", id="pomodoro-start", size="sm", color="success"),
                        dbc.Button("Pause", id="pomodoro-pause", size="sm", color="warning"),
                        dbc.Button("Reset", id="pomodoro-reset", size="sm", color="danger")
                    ], className="w-100 mt-2")
                ])
            ])
        ], width=12, lg=3),

        # Main task area
        dbc.Col([
            # Stats row
            dbc.Row([
                dbc.Col([
                    html.Div(id="stats-cards")
                ], width=12)
            ], className="mb-4"),

            # View selector
            dbc.Tabs([
                dbc.Tab(label="📋 All Tasks", tab_id="all", label_style={"fontSize": "0.95rem"}),
                dbc.Tab(label="⚡ Smart View", tab_id="smart", label_style={"fontSize": "0.95rem"}),
                dbc.Tab(label="📊 Analytics", tab_id="analytics", label_style={"fontSize": "0.95rem"})
            ], id="view-tabs", active_tab="smart", className="mb-3"),

            # Search and filters
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText(html.I(className="fas fa-search")),
                        dbc.Input(
                            id="search-input",
                            placeholder="Search tasks...",
                            type="text"
                        )
                    ])
                ], width=12, md=6),
                dbc.Col([
                    dbc.Select(
                        id="filter-category",
                        options=[{"label": "All Categories", "value": "all"}] +
                                [{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in CATEGORIES.items()],
                        value="all"
                    )
                ], width=12, md=3),
                dbc.Col([
                    dbc.Select(
                        id="filter-energy",
                        options=[{"label": "All Energy Levels", "value": "all"}] +
                                [{"label": f"{v['icon']} {v['name']}", "value": k} for k, v in ENERGY_LEVELS.items()],
                        value="all"
                    )
                ], width=12, md=3)
            ], className="mb-4"),

            # Task list
            html.Div(id="task-list-container")
        ], width=12, lg=9)
    ])
], fluid=True, className="p-4", style={"backgroundColor": "#f8fafc", "minHeight": "100vh"})

# Callbacks

@app.callback(
    Output('tasks-store', 'data'),
    Output('add-task-feedback', 'children'),
    Input('add-task-btn', 'n_clicks'),
    State('quick-add-input', 'value'),
    State('task-priority', 'value'),
    State('task-category', 'value'),
    State('task-energy', 'value'),
    State('task-time', 'value'),
    State('tasks-store', 'data'),
    prevent_initial_call=True
)
def add_task(n_clicks, description, priority, category, energy, time_estimate, tasks):
    """Add a new task"""
    if not description or not description.strip():
        return tasks, dbc.Alert("Please enter a task description!", color="warning", duration=3000, className="mt-2")

    # Parse natural language
    parsed = parse_natural_language_task(description)

    new_task = {
        "id": str(uuid.uuid4()),
        "description": parsed["description"],
        "priority": int(priority),
        "category": category,
        "energy": energy,
        "time_estimate": int(time_estimate) if time_estimate else 30,
        "due_date": parsed.get("due_date"),
        "due_time": parsed.get("due_time"),
        "created_at": datetime.now().isoformat(),
        "completed": False,
        "time_spent": 0
    }

    tasks.append(new_task)

    return tasks, dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Task added successfully!"],
        color="success",
        duration=3000,
        className="mt-2"
    )

@app.callback(
    Output('task-list-container', 'children'),
    Output('stats-cards', 'children'),
    Input('tasks-store', 'data'),
    Input('view-tabs', 'active_tab'),
    Input('search-input', 'value'),
    Input('filter-category', 'value'),
    Input('filter-energy', 'value')
)
def update_task_display(tasks, active_tab, search, filter_cat, filter_energy):
    """Update task list and stats"""
    if not tasks:
        empty_state = html.Div([
            html.I(className="fas fa-inbox", style={"fontSize": "4rem", "color": "#cbd5e1", "marginBottom": "1rem"}),
            html.H4("No tasks yet", className="text-muted"),
            html.P("Add your first task above to get started!", className="text-muted")
        ], className="text-center py-5")

        stats = create_basic_stats(tasks)
        return empty_state, stats

    # Filter tasks
    filtered_tasks = [t for t in tasks if not t.get("completed", False)]

    if search:
        filtered_tasks = [t for t in filtered_tasks if search.lower() in t["description"].lower()]

    if filter_cat and filter_cat != "all":
        filtered_tasks = [t for t in filtered_tasks if t.get("category") == filter_cat]

    if filter_energy and filter_energy != "all":
        filtered_tasks = [t for t in filtered_tasks if t.get("energy") == filter_energy]

    # Sort based on view
    if active_tab == "smart":
        # Smart sort by score
        filtered_tasks.sort(key=calculate_task_score, reverse=True)
    else:
        # Sort by created date
        filtered_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Create task cards
    task_cards = [create_task_card(task, i) for i, task in enumerate(filtered_tasks)]

    if not task_cards:
        task_cards = html.Div([
            html.I(className="fas fa-filter", style={"fontSize": "3rem", "color": "#cbd5e1", "marginBottom": "1rem"}),
            html.H5("No tasks match your filters", className="text-muted"),
            html.P("Try adjusting your search or filters", className="text-muted")
        ], className="text-center py-5")

    # Create stats
    stats = create_basic_stats(tasks)

    return html.Div(task_cards), stats

def create_basic_stats(tasks):
    """Create stats cards"""
    total = len(tasks)
    active = len([t for t in tasks if not t.get("completed", False)])
    completed_today = len([t for t in tasks if t.get("completed") and
                           t.get("completed_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))])

    # Calculate completion rate
    completed_total = len([t for t in tasks if t.get("completed", False)])
    completion_rate = int((completed_total / total * 100)) if total > 0 else 0

    return dbc.Row([
        dbc.Col([
            create_stats_card(
                "Active Tasks",
                str(active),
                f"{total} total tasks",
                "fa-tasks",
                "#6366f1"
            )
        ], width=12, md=6, lg=3),
        dbc.Col([
            create_stats_card(
                "Completed Today",
                str(completed_today),
                "Keep it up!",
                "fa-check-circle",
                "#10b981"
            )
        ], width=12, md=6, lg=3),
        dbc.Col([
            create_stats_card(
                "Completion Rate",
                f"{completion_rate}%",
                f"{completed_total} completed",
                "fa-chart-line",
                "#8b5cf6"
            )
        ], width=12, md=6, lg=3),
        dbc.Col([
            create_stats_card(
                "Streak",
                "0 days",
                "Start your streak!",
                "fa-fire",
                "#ef4444"
            )
        ], width=12, md=6, lg=3)
    ], className="g-3")

@app.callback(
    Output('tasks-store', 'data', allow_duplicate=True),
    Output('completed-tasks-store', 'data'),
    Input({'type': 'task-checkbox', 'index': ALL}, 'value'),
    State('tasks-store', 'data'),
    State('completed-tasks-store', 'data'),
    prevent_initial_call=True
)
def complete_task(checkbox_values, tasks, completed_tasks):
    """Mark task as completed"""
    if not ctx.triggered:
        return tasks, completed_tasks or []

    # Find which checkbox was clicked
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if not triggered_id:
        return tasks, completed_tasks or []

    task_id = json.loads(triggered_id)['index']

    # Find and complete the task
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            task['completed_at'] = datetime.now().isoformat()
            if completed_tasks is None:
                completed_tasks = []
            completed_tasks.append(task)
            break

    return tasks, completed_tasks

@app.callback(
    Output('tasks-store', 'data', allow_duplicate=True),
    Input({'type': 'delete-task', 'index': ALL}, 'n_clicks'),
    State('tasks-store', 'data'),
    prevent_initial_call=True
)
def delete_task(n_clicks, tasks):
    """Delete a task"""
    if not ctx.triggered or not any(n_clicks):
        return tasks

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    task_id = json.loads(triggered_id)['index']

    tasks = [t for t in tasks if t['id'] != task_id]
    return tasks

@app.callback(
    Output('pomodoro-display', 'children'),
    Output('pomodoro-state', 'data'),
    Output('pomodoro-interval', 'disabled'),
    Input('pomodoro-start', 'n_clicks'),
    Input('pomodoro-pause', 'n_clicks'),
    Input('pomodoro-reset', 'n_clicks'),
    Input('pomodoro-interval', 'n_intervals'),
    State('pomodoro-state', 'data'),
    prevent_initial_call=True
)
def update_pomodoro(start_clicks, pause_clicks, reset_clicks, n_intervals, state):
    """Update Pomodoro timer"""
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'pomodoro-start':
        state['running'] = True
        disabled = False
    elif button_id == 'pomodoro-pause':
        state['running'] = False
        disabled = True
    elif button_id == 'pomodoro-reset':
        state['time_left'] = 1500  # 25 minutes
        state['running'] = False
        disabled = True
    elif button_id == 'pomodoro-interval' and state['running']:
        state['time_left'] = max(0, state['time_left'] - 1)
        disabled = False
    else:
        disabled = not state.get('running', False)

    # Format time display
    minutes = state['time_left'] // 60
    seconds = state['time_left'] % 60

    display = html.Div([
        html.H2(f"{minutes:02d}:{seconds:02d}", className="mb-0", style={"fontSize": "3rem", "fontWeight": "700"}),
        html.P("Focus time" if state['running'] else "Ready to focus", className="text-muted mb-0")
    ], className="text-center")

    return display, state, disabled

@app.callback(
    Output('daily-focus', 'children'),
    Input('tasks-store', 'data')
)
def update_daily_focus(tasks):
    """Update daily focus section"""
    if not tasks:
        return html.P("No tasks yet", className="text-muted")

    # Get today's tasks
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = [t for t in tasks if not t.get("completed") and
                   (not t.get("due_date") or t.get("due_date") <= today)]

    if not today_tasks:
        return html.P("No tasks due today! 🎉", className="text-success")

    # Get highest priority task
    today_tasks.sort(key=calculate_task_score, reverse=True)
    focus_task = today_tasks[0]

    return html.Div([
        html.P("Your top priority:", className="text-muted mb-2", style={"fontSize": "0.875rem"}),
        html.H6(focus_task["description"], className="mb-2"),
        dbc.Badge(
            f"{PRIORITIES[focus_task['priority']]['name']} Priority",
            color="primary"
        )
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8052))
    app.run(debug=True, host='0.0.0.0', port=port)
