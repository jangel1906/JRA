"""
Flow - Intelligent Task Management Application
Production-ready version optimized for Render deployment
Beautiful UI/UX with smart features and mobile-first design
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import uuid
import re
import os

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
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_until = (due - datetime.now()).days
            if days_until < 0:
                score += 100  # Overdue
            elif days_until == 0:
                score += 50   # Due today
            elif days_until == 1:
                score += 30   # Tomorrow
        except:
            pass

    return score

def create_task_card(task):
    """Create a beautiful task card"""
    category = CATEGORIES.get(task.get("category", "personal"))
    priority = PRIORITIES[task.get("priority", 3)]

    # Due date badge
    due_badge = None
    if task.get("due_date"):
        try:
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_until = (due - datetime.now()).days

            if days_until < 0:
                due_text, due_color = f"Overdue {abs(days_until)}d", "danger"
            elif days_until == 0:
                due_text, due_color = "Due today", "warning"
            elif days_until == 1:
                due_text, due_color = "Tomorrow", "info"
            else:
                due_text, due_color = due.strftime("%b %d"), "secondary"

            due_badge = dbc.Badge(due_text, color=due_color, className="me-2")
        except:
            pass

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                dbc.Checkbox(
                    id={"type": "complete-task", "index": task["id"]},
                    className="me-3",
                    style={"transform": "scale(1.4)"}
                ),
                html.Div([
                    html.H6(task["description"], className="mb-2", style={"fontWeight": "600"}),
                    html.Div([
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
                        ),
                        due_badge
                    ])
                ], style={"flex": "1"}),
                html.Div([
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
            ], className="d-flex align-items-center")
        ])
    ], className="mb-3 task-card", style={
        "borderLeft": f"4px solid {category['color']}",
        "transition": "all 0.3s ease"
    })

# App Layout
app.layout = dbc.Container([
    # Data stores
    dcc.Store(id="tasks-store", data=[]),
    dcc.Store(id="filter-state", data={"category": "all", "search": ""}),
    dcc.Store(id="edit-task-store", data=None),

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
                html.H1([
                    html.Span("✨ ", style={"fontSize": "2rem"}),
                    "Flow"
                ], className="mb-1", style={
                    "fontWeight": "800",
                    "background": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "backgroundClip": "text"
                }),
                html.P("Intelligent Task Management", className="text-muted mb-0")
            ], className="text-center mb-4")
        ])
    ]),

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
            ])
        ], width=6, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-check-circle fa-2x mb-2", style={"color": "#10b981"}),
                        html.H3(id="stat-completed", children="0", className="mb-0"),
                        html.Small("Completed", className="text-muted")
                    ], className="text-center")
                ])
            ])
        ], width=6, md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-fire fa-2x mb-2", style={"color": "#ef4444"}),
                        html.H3(id="stat-streak", children="0", className="mb-0"),
                        html.Small("Day Streak", className="text-muted")
                    ], className="text-center")
                ])
            ])
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
            ])
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
                            {"label": "📅 Due Today", "value": "today"}
                        ],
                        value="smart",
                        className="mb-2"
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

# Callbacks

@app.callback(
    Output("tasks-store", "data"),
    Output("add-feedback", "children"),
    Input("add-task-btn", "n_clicks"),
    State("task-input", "value"),
    State("task-priority", "value"),
    State("task-category", "value"),
    State("task-due-date", "value"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def add_task(n, description, priority, category, due_date, tasks):
    """Add a new task"""
    if not description or not description.strip():
        return tasks, dbc.Alert("Please enter a task!", color="warning", duration=3000)

    # Parse natural language
    parsed = parse_natural_language(description)

    new_task = {
        "id": str(uuid.uuid4()),
        "description": description.strip(),
        "priority": int(priority),
        "category": category,
        "due_date": due_date or parsed.get("due_date"),
        "created_at": datetime.now().isoformat(),
        "completed": False
    }

    tasks.append(new_task)

    return tasks, dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), "Task added!"],
        color="success",
        duration=3000
    )

@app.callback(
    Output("task-list", "children"),
    Output("stat-active", "children"),
    Output("stat-completed", "children"),
    Output("stat-rate", "children"),
    Input("tasks-store", "data"),
    Input("view-filter", "value"),
    Input("search-input", "value"),
    Input("category-filter", "value")
)
def update_tasks(tasks, view, search, category):
    """Update task list and stats"""
    if not tasks:
        empty = html.Div([
            html.I(className="fas fa-inbox fa-4x mb-3", style={"color": "#cbd5e1"}),
            html.H5("No tasks yet", className="text-muted"),
            html.P("Add your first task to get started!", className="text-muted")
        ], className="text-center py-5")
        return empty, "0", "0", "0%"

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
        today = datetime.now().strftime("%Y-%m-%d")
        filtered = [t for t in filtered if t.get("due_date") == today]
    elif view == "smart":
        filtered.sort(key=calculate_task_score, reverse=True)

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

    return task_cards, str(active_count), str(completed_count), completion_rate

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Input({"type": "complete-task", "index": ALL}, "value"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def complete_task(values, tasks):
    """Mark task as completed"""
    if not ctx.triggered:
        return tasks

    trigger = ctx.triggered[0]["prop_id"]
    if not trigger or ".value" not in trigger:
        return tasks

    task_id = json.loads(trigger.split(".")[0])["index"]

    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            break

    return tasks

@app.callback(
    Output("tasks-store", "data", allow_duplicate=True),
    Input({"type": "delete-task", "index": ALL}, "n_clicks"),
    State("tasks-store", "data"),
    prevent_initial_call=True
)
def delete_task(n_clicks, tasks):
    """Delete a task"""
    if not ctx.triggered or not any(n_clicks):
        return tasks

    trigger = ctx.triggered[0]["prop_id"]
    task_id = json.loads(trigger.split(".")[0])["index"]

    tasks = [t for t in tasks if t["id"] != task_id]
    return tasks

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
    prevent_initial_call=True
)
def save_edited_task(n_clicks, task_id, description, priority, category, due_date, tasks):
    """Save edited task"""
    if not n_clicks or not task_id:
        return tasks

    # Find and update the task
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = description.strip() if description else task["description"]
            task["priority"] = int(priority)
            task["category"] = category
            task["due_date"] = due_date if due_date else None
            break

    return tasks

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8052))
    app.run(debug=False, host="0.0.0.0", port=port)
