"""
Task Management Multiverse Application
A Sims-like task management app where characters walk around in multiple universes
and remind you about your tasks based on priority.
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import uuid
import random
import os

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"},
        {"name": "apple-mobile-web-app-title", "content": "Task Multiverse"},
        {"name": "theme-color", "content": "#667eea"},
        {"name": "description", "content": "A Sims-like task management app with characters in multiple universes"}
    ]
)

# Enable serving of static files
app.title = "Task Multiverse"

# Character personalities and traits
CHARACTERS = [
    {
        "id": "char1",
        "name": "Alex",
        "personality": "Energetic",
        "color": "#FF6B6B",
        "reminder_style": "enthusiastic",
        "emoji": "🏃"
    },
    {
        "id": "char2",
        "name": "Maya",
        "personality": "Thoughtful",
        "color": "#4ECDC4",
        "reminder_style": "gentle",
        "emoji": "🧘"
    },
    {
        "id": "char3",
        "name": "Leo",
        "personality": "Focused",
        "color": "#FFE66D",
        "reminder_style": "direct",
        "emoji": "🎯"
    },
    {
        "id": "char4",
        "name": "Zara",
        "personality": "Creative",
        "color": "#A8E6CF",
        "reminder_style": "inspiring",
        "emoji": "✨"
    },
    {
        "id": "char5",
        "name": "Sam",
        "personality": "Analytical",
        "color": "#B4A7D6",
        "reminder_style": "logical",
        "emoji": "🔬"
    }
]

# Universe themes
UNIVERSES = [
    {"id": "work", "name": "Work Universe", "color": "#667eea", "icon": "💼"},
    {"id": "home", "name": "Home Universe", "color": "#f093fb", "icon": "🏠"},
    {"id": "creative", "name": "Creative Universe", "color": "#4facfe", "icon": "🎨"},
    {"id": "zen", "name": "Zen Universe", "color": "#43e97b", "icon": "🧘"},
]

# Priority levels
PRIORITY_LEVELS = {
    1: {"name": "Critical", "color": "#FF4444", "reminder_interval": 5},
    2: {"name": "High", "color": "#FF8C00", "reminder_interval": 15},
    3: {"name": "Medium", "color": "#FFD700", "reminder_interval": 30},
    4: {"name": "Low", "color": "#90EE90", "reminder_interval": 60},
    5: {"name": "Someday", "color": "#87CEEB", "reminder_interval": 120}
}

def get_reminder_message(character, task):
    """Generate a personalized reminder message based on character personality"""
    style = character["reminder_style"]
    name = character["name"]
    task_desc = task["description"]
    priority = PRIORITY_LEVELS[task["priority"]]["name"]

    messages = {
        "enthusiastic": [
            f"Hey! {name} here! Don't forget about '{task_desc}' - it's {priority} priority! Let's crush it! 💪",
            f"Yo! {name} checking in! '{task_desc}' is waiting for you! Time to get it done! 🚀"
        ],
        "gentle": [
            f"Hi there... {name} wanted to gently remind you about '{task_desc}'. Take your time. 🌸",
            f"When you have a moment, {name} thinks you might want to look at '{task_desc}'. No rush. ☺️"
        ],
        "direct": [
            f"{name}: '{task_desc}' needs attention. Priority: {priority}.",
            f"Task reminder from {name}: '{task_desc}'. Let's focus and complete this."
        ],
        "inspiring": [
            f"✨ {name} believes in you! '{task_desc}' is your chance to shine! You've got this!",
            f"Hey friend! {name} here with a creative nudge: '{task_desc}' awaits your magic! 🎨"
        ],
        "logical": [
            f"{name}'s analysis: '{task_desc}' ({priority} priority) should be addressed to optimize your workflow.",
            f"Data from {name}: Task '{task_desc}' pending. Completion will improve productivity by 100%! 📊"
        ]
    }

    return random.choice(messages.get(style, messages["direct"]))

def create_character_card(character, position, universe, task_count=0):
    """Create a character card showing their current status"""
    return html.Div([
        html.Div([
            html.Div(character["emoji"], style={"fontSize": "40px"}),
            html.Div(character["name"], style={"fontWeight": "bold", "fontSize": "14px"}),
            html.Div(character["personality"], style={"fontSize": "11px", "opacity": "0.8"}),
            html.Div(f"Tasks: {task_count}", style={"fontSize": "11px", "marginTop": "5px"}),
        ], style={
            "backgroundColor": character["color"],
            "padding": "15px",
            "borderRadius": "15px",
            "textAlign": "center",
            "color": "white",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1)",
            "transition": "all 0.3s ease",
            "position": "absolute",
            "left": f"{position['x']}px",
            "top": f"{position['y']}px",
            "animation": "float 3s ease-in-out infinite",
            "minWidth": "100px"
        })
    ], id={"type": "character-card", "index": character["id"]})

def create_universe_zone(universe):
    """Create a visual zone for a universe"""
    return html.Div([
        html.Div([
            html.Span(universe["icon"], style={"fontSize": "24px", "marginRight": "10px"}),
            html.Span(universe["name"], style={"fontWeight": "bold", "fontSize": "16px"})
        ], style={"marginBottom": "10px"}),
        html.Div(id={"type": "universe-characters", "index": universe["id"]})
    ], style={
        "background": f"linear-gradient(135deg, {universe['color']}22, {universe['color']}44)",
        "border": f"2px solid {universe['color']}",
        "borderRadius": "20px",
        "padding": "20px",
        "minHeight": "200px",
        "position": "relative",
        "margin": "10px"
    }, className="universe-zone")

# App layout
app.layout = dbc.Container([
    # PWA Support
    html.Link(rel='manifest', href='/assets/manifest.json'),
    html.Link(rel='icon', type='image/png', sizes='192x192', href='/assets/icons/icon-192x192.png'),
    html.Link(rel='apple-touch-icon', sizes='180x180', href='/assets/icons/icon-192x192.png'),

    # Store components for state management
    dcc.Store(id='tasks-store', data=[]),
    dcc.Store(id='character-positions', data={}),
    dcc.Store(id='reminders-store', data=[]),

    # Interval components for updates
    dcc.Interval(id='movement-interval', interval=2000, n_intervals=0),  # Character movement
    dcc.Interval(id='reminder-interval', interval=5000, n_intervals=0),  # Check reminders

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🌍 Task Multiverse", style={
                "textAlign": "center",
                "marginTop": "20px",
                "marginBottom": "10px",
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "WebkitBackgroundClip": "text",
                "WebkitTextFillColor": "transparent",
                "fontWeight": "bold"
            }),
            html.P(
                "Where tasks meet characters across multiple universes",
                style={"textAlign": "center", "color": "#666", "marginBottom": "30px"}
            )
        ])
    ]),

    # Main content
    dbc.Row([
        # Left panel - Task Management
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("📝 Task Control Center", className="mb-0")),
                dbc.CardBody([
                    # Task creation form
                    dbc.Label("Task Description"),
                    dbc.Textarea(
                        id="task-description",
                        placeholder="What needs to be done?",
                        style={"marginBottom": "15px"}
                    ),

                    dbc.Label("Priority Level"),
                    dbc.Select(
                        id="task-priority",
                        options=[
                            {"label": f"{PRIORITY_LEVELS[i]['name']} - {PRIORITY_LEVELS[i]['color']}", "value": i}
                            for i in range(1, 6)
                        ],
                        value=3,
                        style={"marginBottom": "15px"}
                    ),

                    dbc.Label("Assign to Character"),
                    dbc.Select(
                        id="task-character",
                        options=[
                            {"label": f"{c['emoji']} {c['name']} ({c['personality']})", "value": c['id']}
                            for c in CHARACTERS
                        ],
                        style={"marginBottom": "15px"}
                    ),

                    dbc.Label("Universe"),
                    dbc.Select(
                        id="task-universe",
                        options=[
                            {"label": f"{u['icon']} {u['name']}", "value": u['id']}
                            for u in UNIVERSES
                        ],
                        value="work",
                        style={"marginBottom": "15px"}
                    ),

                    dbc.Button(
                        "Create Task",
                        id="create-task-btn",
                        color="primary",
                        className="w-100",
                        style={"marginBottom": "20px"}
                    ),

                    html.Div(id="task-feedback"),

                    # Task statistics
                    html.Hr(),
                    html.H5("Task Statistics"),
                    html.Div(id="task-stats", style={"marginTop": "15px"})
                ])
            ], style={"marginBottom": "20px"}),

            # Task list
            dbc.Card([
                dbc.CardHeader(html.H4("📋 Active Tasks", className="mb-0")),
                dbc.CardBody([
                    html.Div(id="task-list")
                ])
            ])
        ], width=12, lg=4),

        # Right panel - Multiverse visualization
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("🌌 The Multiverse", className="mb-0")),
                dbc.CardBody([
                    html.Div([
                        create_universe_zone(universe)
                        for universe in UNIVERSES
                    ], id="multiverse-container", style={"position": "relative"})
                ])
            ], style={"marginBottom": "20px"}),

            # Reminders panel
            dbc.Card([
                dbc.CardHeader(html.H4("🔔 Reminders", className="mb-0")),
                dbc.CardBody([
                    html.Div(id="reminders-container", style={
                        "maxHeight": "300px",
                        "overflowY": "auto"
                    })
                ])
            ])
        ], width=12, lg=8)
    ]),

    # Custom CSS
    html.Style("""
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .universe-zone {
            transition: all 0.3s ease;
        }

        .universe-zone:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .task-item {
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .task-item:hover {
            transform: translateX(5px);
        }

        /* Mobile optimizations */
        @media (max-width: 768px) {
            .container-fluid {
                padding: 10px !important;
            }

            h1 {
                font-size: 24px !important;
            }

            .card {
                margin-bottom: 10px !important;
            }

            .universe-zone {
                margin: 5px !important;
                padding: 10px !important;
                min-height: 150px !important;
            }

            button {
                font-size: 14px !important;
                padding: 10px !important;
            }

            /* Improve touch targets */
            .btn {
                min-height: 44px;
                min-width: 44px;
            }

            /* Prevent zoom on input focus */
            input, textarea, select {
                font-size: 16px !important;
            }
        }

        /* Add touch feedback */
        .task-item:active, .btn:active {
            transform: scale(0.98);
            opacity: 0.8;
        }

        /* Smooth scrolling for mobile */
        * {
            -webkit-overflow-scrolling: touch;
        }
    """),

    # Service Worker Registration
    html.Script("""
        // Register service worker for PWA functionality
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/assets/service-worker.js')
                    .then(function(registration) {
                        console.log('ServiceWorker registered:', registration.scope);
                    })
                    .catch(function(error) {
                        console.log('ServiceWorker registration failed:', error);
                    });
            });
        }

        // Add to home screen prompt
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            console.log('App can be installed');
        });

        // Handle install
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed successfully');
            deferredPrompt = null;
        });

        // Prevent pull-to-refresh on mobile
        document.body.style.overscrollBehavior = 'contain';
    """)
], fluid=True, style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "paddingBottom": "50px"})

# Callbacks

@app.callback(
    Output('tasks-store', 'data'),
    Output('task-feedback', 'children'),
    Input('create-task-btn', 'n_clicks'),
    State('task-description', 'value'),
    State('task-priority', 'value'),
    State('task-character', 'value'),
    State('task-universe', 'value'),
    State('tasks-store', 'data'),
    prevent_initial_call=True
)
def create_task(n_clicks, description, priority, character_id, universe, tasks):
    """Create a new task"""
    if not description or not description.strip():
        return tasks, dbc.Alert("Please enter a task description!", color="warning", duration=3000)

    if not character_id:
        return tasks, dbc.Alert("Please assign a character!", color="warning", duration=3000)

    new_task = {
        "id": str(uuid.uuid4()),
        "description": description.strip(),
        "priority": int(priority),
        "character_id": character_id,
        "universe": universe,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "last_reminder": None
    }

    tasks.append(new_task)

    character = next((c for c in CHARACTERS if c["id"] == character_id), None)
    char_name = character["name"] if character else "Unknown"

    return tasks, dbc.Alert(
        f"✅ Task assigned to {char_name}!",
        color="success",
        duration=3000
    )

@app.callback(
    Output('task-list', 'children'),
    Output('task-stats', 'children'),
    Input('tasks-store', 'data')
)
def update_task_list(tasks):
    """Update the task list display"""
    if not tasks:
        return html.P("No tasks yet. Create your first task!", style={"color": "#999", "fontStyle": "italic"}), []

    active_tasks = [t for t in tasks if t["status"] == "active"]

    task_items = []
    for task in active_tasks:
        character = next((c for c in CHARACTERS if c["id"] == task["character_id"]), None)
        priority_info = PRIORITY_LEVELS[task["priority"]]

        task_items.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(
                            priority_info["name"],
                            style={
                                "backgroundColor": priority_info["color"],
                                "color": "white",
                                "padding": "2px 8px",
                                "borderRadius": "10px",
                                "fontSize": "11px",
                                "marginRight": "10px"
                            }
                        ),
                        html.Span(
                            f"{character['emoji']} {character['name']}" if character else "Unknown",
                            style={"fontSize": "12px", "opacity": "0.8"}
                        )
                    ], style={"marginBottom": "8px"}),
                    html.P(task["description"], style={"marginBottom": "5px", "fontSize": "14px"}),
                    html.Div([
                        dbc.Button(
                            "Complete ✓",
                            id={"type": "complete-task", "index": task["id"]},
                            size="sm",
                            color="success",
                            outline=True
                        )
                    ])
                ])
            ], className="task-item", style={"marginBottom": "10px"})
        )

    # Statistics
    stats = []
    priority_counts = {}
    for task in active_tasks:
        p = task["priority"]
        priority_counts[p] = priority_counts.get(p, 0) + 1

    stats.append(html.Div([
        html.Strong("Total Active: "),
        html.Span(len(active_tasks))
    ]))

    for p, count in sorted(priority_counts.items()):
        stats.append(html.Div([
            html.Span("●", style={"color": PRIORITY_LEVELS[p]["color"], "marginRight": "5px"}),
            html.Span(f"{PRIORITY_LEVELS[p]['name']}: {count}")
        ], style={"fontSize": "14px", "marginTop": "5px"}))

    return task_items, stats

@app.callback(
    Output('tasks-store', 'data', allow_duplicate=True),
    Input({"type": "complete-task", "index": ALL}, "n_clicks"),
    State('tasks-store', 'data'),
    prevent_initial_call=True
)
def complete_task(n_clicks, tasks):
    """Mark a task as completed"""
    if not ctx.triggered or not any(n_clicks):
        return tasks

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    task_id = json.loads(button_id)["index"]

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            break

    return tasks

@app.callback(
    Output('character-positions', 'data'),
    Input('movement-interval', 'n_intervals'),
    State('character-positions', 'data')
)
def update_character_positions(n_intervals, positions):
    """Update character positions for animation"""
    if not positions:
        # Initialize positions
        positions = {}
        for i, char in enumerate(CHARACTERS):
            positions[char["id"]] = {
                "x": random.randint(20, 180),
                "y": random.randint(20, 120),
                "universe": UNIVERSES[i % len(UNIVERSES)]["id"]
            }

    # Random walk for each character
    for char_id in positions:
        pos = positions[char_id]
        pos["x"] = max(20, min(180, pos["x"] + random.randint(-30, 30)))
        pos["y"] = max(20, min(120, pos["y"] + random.randint(-20, 20)))

        # Occasionally change universe
        if random.random() < 0.1:
            pos["universe"] = random.choice(UNIVERSES)["id"]

    return positions

@app.callback(
    Output('multiverse-container', 'children'),
    Input('character-positions', 'data'),
    Input('tasks-store', 'data')
)
def update_multiverse(positions, tasks):
    """Update the multiverse visualization with character positions"""
    if not positions:
        return [create_universe_zone(universe) for universe in UNIVERSES]

    # Count tasks per character
    task_counts = {}
    active_tasks = [t for t in tasks if t["status"] == "active"]
    for task in active_tasks:
        char_id = task["character_id"]
        task_counts[char_id] = task_counts.get(char_id, 0) + 1

    # Create universe zones with characters
    universe_zones = []
    for universe in UNIVERSES:
        # Get characters in this universe
        chars_in_universe = []
        for char in CHARACTERS:
            if positions.get(char["id"], {}).get("universe") == universe["id"]:
                pos = positions[char["id"]]
                task_count = task_counts.get(char["id"], 0)
                chars_in_universe.append(
                    create_character_card(char, pos, universe["id"], task_count)
                )

        zone = html.Div([
            html.Div([
                html.Span(universe["icon"], style={"fontSize": "24px", "marginRight": "10px"}),
                html.Span(universe["name"], style={"fontWeight": "bold", "fontSize": "16px"})
            ], style={"marginBottom": "10px"}),
            html.Div(chars_in_universe, style={"position": "relative", "minHeight": "160px"})
        ], style={
            "background": f"linear-gradient(135deg, {universe['color']}22, {universe['color']}44)",
            "border": f"2px solid {universe['color']}",
            "borderRadius": "20px",
            "padding": "20px",
            "minHeight": "200px",
            "position": "relative",
            "margin": "10px"
        }, className="universe-zone")

        universe_zones.append(zone)

    return universe_zones

@app.callback(
    Output('reminders-container', 'children'),
    Output('reminders-store', 'data'),
    Output('tasks-store', 'data', allow_duplicate=True),
    Input('reminder-interval', 'n_intervals'),
    State('tasks-store', 'data'),
    State('reminders-store', 'data'),
    prevent_initial_call=True
)
def check_reminders(n_intervals, tasks, reminders):
    """Check if any tasks need reminders"""
    now = datetime.now()
    active_tasks = [t for t in tasks if t["status"] == "active"]

    new_reminders = reminders[-10:] if reminders else []  # Keep last 10 reminders
    updated_tasks = tasks.copy()

    for task in active_tasks:
        priority_info = PRIORITY_LEVELS[task["priority"]]
        reminder_interval = priority_info["reminder_interval"]

        last_reminder = task.get("last_reminder")
        should_remind = False

        if not last_reminder:
            should_remind = True
        else:
            last_time = datetime.fromisoformat(last_reminder)
            if (now - last_time).total_seconds() / 60 >= reminder_interval:
                should_remind = True

        if should_remind:
            character = next((c for c in CHARACTERS if c["id"] == task["character_id"]), None)
            if character:
                message = get_reminder_message(character, task)
                new_reminders.append({
                    "id": str(uuid.uuid4()),
                    "message": message,
                    "character": character,
                    "timestamp": now.isoformat(),
                    "priority": task["priority"]
                })

                # Update task's last reminder time
                for t in updated_tasks:
                    if t["id"] == task["id"]:
                        t["last_reminder"] = now.isoformat()
                        break

    # Create reminder display
    reminder_items = []
    for reminder in reversed(new_reminders[-10:]):  # Show latest 10
        char = reminder["character"]
        priority_color = PRIORITY_LEVELS[reminder["priority"]]["color"]

        reminder_items.append(
            dbc.Alert([
                html.Div([
                    html.Span(char["emoji"], style={"fontSize": "20px", "marginRight": "10px"}),
                    html.Strong(char["name"])
                ]),
                html.P(reminder["message"], style={"marginTop": "10px", "marginBottom": "5px"}),
                html.Small(
                    datetime.fromisoformat(reminder["timestamp"]).strftime("%I:%M %p"),
                    style={"opacity": "0.7"}
                )
            ], color="light", style={
                "borderLeft": f"4px solid {priority_color}",
                "marginBottom": "10px"
            })
        )

    if not reminder_items:
        reminder_items = [html.P("No reminders yet. Your characters will notify you soon!", style={"color": "#999", "fontStyle": "italic"})]

    return reminder_items, new_reminders, updated_tasks

# Server setup
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8051))
    app.run_server(debug=True, host='0.0.0.0', port=port)
